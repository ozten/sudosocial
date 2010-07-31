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
from streamManager.stream_config import StreamConfig

logging.basicConfig(level = config.log_level, filename='foo.log',
                    format = '%(asctime)s %(levelname)s %(process)d %(message)s', )
log = logging.getLogger()
def update_feed(feed_meta):
    """
    Update a single feed.
    
    feed_meta - lifestream.models.Feed object
    
    Returns number of newly fetched entries.
    """
    new_entry_count = 0
    try:
        feed = fetch_feed(feed_meta)
        if feed:
            log.debug('Processing %s %s' % (feed_meta.url_hash, feed_meta.url))
            if 'feed' in feed and 'title' in feed.feed:
                log.debug('Processing title: %s', feed.feed.title)
            
            dirty_feed = False
            if 'feed' in feed and 'title' in feed.feed and feed_meta.title != feed.feed.title:
                feed_meta.title = feed.feed.title
                dirty_feed = True
            else:
                if (not 'feed' in feed) or (not 'title' in feed.feed):
                    log.warn("Feed doesn't have a title property")
            if dirty_feed:
                try:
                    feed_meta.save()
                except KeyboardInterrupt:
                    raise
                except Exception, x:
                    log.error("Unable to update feed")
                    log.exception(x)
            # A feed lives in several streams
            stream_feed_configs = []
            for stream in feed_meta.streams.all():
                stream_config = StreamConfig(stream.config)
                for feed_config in stream_config.config['feeds']:
                    if feed_config['url_hash'] == feed_meta.url_hash:
                        # We'll reuse this config but add which stream it's for...
                        feed_config['stream'] = stream
                        stream_feed_configs.append(feed_config)
            for entry in feed.entries:
                if save_entry(feed_meta, entry, stream_feed_configs):
                    new_entry_count += 1
    except KeyboardInterrupt:
        raise
    except Exception, e:                
        log.error("General Error starting loop: %s", e)
        log.exception(e)
    return new_entry_count

def fetch_feed(feed):
    """
    Fetch a feed from its URL and update its metadata if necessary.
    
    feed - lifestream.models.Feed object

    Returns stream if feed had updates, None otherwise.
    """
    dirty_feed = False
    has_updates = False
    if feed.etag == None:
            feed.etag = ''                    
    if feed.last_modified == None:
        feed.last_modified = datetime.datetime(1975, 1, 10)                
    stream = feedparser.parse(feed.url, etag=feed.etag, modified=feed.last_modified.timetuple())                    
    if 'links' in stream.feed:
        feed_hub_link = 0
        for link in stream.feed.links:
            if 'rel' in link and link.rel == 'hub':
                feed_hub_link += 1
                
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
    return has_updates and stream or None
    


def save_entry(feed, entry, stream_configs):
    """Save a new entry to the database.
        Returns true if successful and false otherwise. """
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
                                           last_published_date=last_publication)
        try:
            new_entry.save()
            for config in stream_configs:
                new_streamentry = lifestream.models.StreamEntry(entry=new_entry, stream=config['stream'], visible=config['entries_visible_default'])
                new_streamentry.save()
            return True
        except IntegrityError, e:
            #log.info('Skipping duplicate entry %s, caught error: %s', entry_guid, e)
            pass
    except KeyboardInterrupt:
        raise
    except Exception, e:
        log.error('General Error on %s: %s', feed.url, e)
        log.exception(e)
    return False

def cron_fetch_feeds():
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
            new_entry_count += update_feed(feed)
    finally:
        lock.close()
    log.info("Finished run in %f seconds for %d new entries" % ((time.time() - start), new_entry_count))  
    return 'Finished importing %d items' % new_entry_count

if __name__ == '__main__':
    cron_fetch_feeds()
