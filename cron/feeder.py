#!/usr/bin/env python

# CRON Bootstrap
import config
import sys
sys.path.append(config.path)
from django.core.management import setup_environ
import settings
setup_environ(settings)

# Imports for this cron
import datetime
import fcntl
import logging
import socket
import time

from django.db import IntegrityError
import django.utils.encoding
import django.utils.hashcompat as hashcompat
import feedparser
import jsonpickle

import lifestream.models

logging.basicConfig(level = config.log_level,
                    format = '%(asctime)s %(levelname)s %(process)d %(message)s', )
log = logging.getLogger()

def cron_fetch_feeds():
    """ TODO: Refactor this function into little pieces """
    log.info("Starting")
    start = time.time()
    new_entry_count = 0
    socket.setdefaulttimeout(config.timeout)
    feeds = lifestream.models.Feed.objects.filter(enabled=True)
    
    
    # Only 1 cron instance
    lock = open("%s/cron/lock" % config.path, 'a+')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)        
    except IOError:
        log.warn("Looks like the old cron is still running... Exiting")
        sys.exit(0)
    try:
        for feed in feeds:
            dirty_feed = False
            has_updates = False
            try:
                if feed.etag == None:
                    feed.etag = ''                    
                if feed.last_modified == None:
                    feed.last_modified = datetime.datetime(1975, 1, 10)                
                log.debug("feed id=%s feed url=%s etag=%s last_modified=%s" % (feed.url_hash, feed.url, feed.etag, str(feed.last_modified)))
                stream = feedparser.parse(feed.url, etag=feed.etag, modified=feed.last_modified.timetuple())                    
                if 'links' in stream.feed:
                    feed_hub_link = 0
                    for link in stream.feed.links:
                        if 'rel' in link and link.rel == 'hub':
                            feed_hub_link += 1
                            log.info("This feed is hub enabled %d..." % feed_hub_link)
                            
                # Next 70 lines of code Inspired... err stolen from planet/planet/.__init__.py Channel update
                url_status = str(500)
                if stream.has_key("status"):
                    url_status = str(stream.status)
                elif stream.has_key("entries") and len(stream.entries)>0:
                    url_status = str(200)
                elif stream.bozo and stream.bozo_exception.__class__.__name__=='Timeout':
                    url_status = str(408)                
                
                if url_status == '301' and \
                    (stream.has_key("entries") and len(stream.entries)>0):
                    # TODO: Change in semantics... url_hash != md5(feed.url) ... does that cause any issues?
                    log.info("Feed has moved from <%s> to <%s>", feed.url, stream.url)
                    feed.url = stream.url
                    dirty_feed = True                     
                elif url_status == '304':
                    log.debug("Feed unchanged")
                elif url_status == '404':
                    log.info("Not a Feed or Feed %s is gone", feed.url)
                    feed.enabled = False
                    feed.disabled_reason = "This is not a feed or it's been removed removed!";
                    dirty_feed = True                    
                elif url_status == '410':                    
                    log.info("Feed %s gone", feed.url)
                    feed.enabled = False
                    feed.disabled_reason = "This feed has been removed!";
                    dirty_feed = True                    
                elif url_status == '408':
                    feed.enabled = False
                    feed.disabled_reason = "This feed didn't respond after %d seconds" % config.timeout
                    dirty_feed = True
                elif int(url_status) >= 400:
                    feed.enabled = False
                    bozo_msg = ""
                    if 1 == stream.bozo and 'bozo_exception' in stream.keys():
                        log.error('Unable to fetch %s Exception: %s',
                              feed.url, stream.bozo_exception)
                        bozo_msg = stream.bozo_exception
                    feed.disabled_reason = "Error while reading the feed: %s __ %s" % (url_status, bozo_msg)
                    dirty_feed = True
                else:
                    # We've got a live one...                    
                    feed.disabled_reason = '' # reset
                    has_updates = True
                
                if stream.has_key("etag") and stream.etag != feed.etag and stream.etag != None:
                    log.info("New etag %s" % stream.etag)
                    feed.etag = stream.etag
                    dirty_feed = True                
                
                if stream.has_key("modified") and stream.modified != feed.last_modified:
                    feed.last_modified = time.strftime("%Y-%m-%d %H:%M:%S", stream.modified)
                    log.info("New last_modified %s" % feed.last_modified)                    
                    dirty_feed = True                    
                if dirty_feed:
                    try:
                        dirty_feed = False
                        log.debug("Feed changed, updating db" % feed)
                        feed.save()                        
                    except KeyboardInterrupt:
                        raise
                    except Exception, x:
                        log.error("Unable to update feed")
                        log.exception(x)                
                if has_updates:
                    log.debug('Processing %s %s' % (feed.url_hash, feed.url))
                    if 'feed' in stream and 'title' in stream.feed:
                        log.debug('Processing title: %s', stream.feed.title)
                    if 'feed' in stream and 'title' in stream.feed and feed.title != stream.feed.title:
                        feed.title = stream.feed.title
                        dirty_feed = True
                    else:
                        if (not 'feed' in stream) or (not 'title' in stream.feed):
                            log.warn("Feed doesn't have a title property")
                            log.info(stream)
                    if dirty_feed:
                        try:
                            feed.save()
                        except KeyboardInterrupt:
                            raise
                        except Exception, x:
                            log.error("Unable to update feed")
                            log.exception(x)
                    for entry in stream.entries:
                        try:
                            json_entry = jsonpickle.encode(entry)
                            entry_guid = ''
                            if 'guid' in entry:
                                entry_guid = entry.guid
                            else:
                                entry_guid = hashcompat.md5_constructor(
                                    django.utils.encoding.smart_str(
                                        json_entry)).hexdigest()
                            if 'updated_parsed' in entry:
                                yr, mon, d, hr, min, sec = entry.updated_parsed[:-3]
                                last_publication = datetime.datetime(yr, mon, d, hr, min, sec)
                            else:
                                log.warn("Entry has no updated field, faking it")
                                last_publication = datetime.datetime.now()
                            
                            new_entry = lifestream.models.Entry(feed=feed, guid=entry_guid, raw=json_entry,
                                                               visible=True, last_published_date=last_publication)
                            try:
                                new_entry.save()
                                new_entry_count += 1
                            except IntegrityError, e:
                                pass
                                #log.info('Skipping duplicate entry %s, caught error: %s', entry_guid, e)
                        except KeyboardInterrupt:
                            raise
                        except Exception, e:
                            log.error('General Error on %s: %s', feed.url, e)
                            log.exception(e)                            
            except KeyboardInterrupt:
                raise
            except Exception, e:                
                log.error("General Error starting loop: %s", e)
                log.exception(e)
    finally:
        lock.close()
    log.info("Finished run in %f seconds for %d new entries" % ((time.time() - start), new_entry_count))  
    return 'Finished importing %d items' % new_entry_count

if __name__ == '__main__':
    cron_fetch_feeds()
