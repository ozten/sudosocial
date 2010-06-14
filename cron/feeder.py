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
import logging
import time

from django.db import IntegrityError
import django.utils.encoding
import django.utils.hashcompat as hashcompat
import feedparser
import jsonpickle
if config.cache:
    import shelve
    from feedcache import cache

import lifestream.models

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(process)d %(message)s', )
log = logging.getLogger()

def cron_fetch_feeds():
    """ """
    log.info("Starting")
    start = time.time()
    new_entry_count = 0
    feeds = lifestream.models.Feed.objects.all()
    
    if config.cache:
        storage = shelve.open('.feedcache')
        
    try:
        if config.cache:
            fc = cache.Cache(storage)
        for feed in feeds:
            if config.cache:
                stream = fc.fetch(feed.url)
            else:
                stream = feedparser.parse(feed.url)                            
            #stream = feedparser.parse(feed.url)
            if 1 == stream.bozo and 'bozo_exception' in stream.keys():
                log.error('Unable to fetch %s Exception: %s',
                          feed.url, stream.bozo_exception)
            else:
                log.info('Processing %s', feed.url)
                if 'feed' in stream and 'title' in stream.feed:
                    log.info('Processing title: %s', stream.feed.title)
                if 'feed' in stream and 'title' in stream.feed and feed.title != stream.feed.title:
                    feed.title = stream.feed.title
                    try:
                        feed.save()
                    except Exception, x:
                        log.error("Unable to update feed title from=%s to=%s" % (feed.title, stream.title))
                        log.error(x)
                else:
                    if (not 'feed' in stream) or (not 'title' in stream.feed):
                        log.warn("Feed doesn't have a title property")
                        log.info(stream)
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
                        yr, mon, d, hr, min, sec = entry.updated_parsed[:-3]
                        last_publication = datetime.datetime(yr, mon, d, hr, min, sec)
                        new_entry = lifestream.models.Entry(feed=feed, guid=entry_guid, raw=json_entry,
                                                           visible=True, last_published_date=last_publication)
                        try:
                            new_entry.save()
                            new_entry_count += 1
                        except IntegrityError, e:
                            pass
                            #log.info('Skipping duplicate entry %s, caught error: %s', entry_guid, e)
                    except:
                        # TODO monitor exceptions here, for now this keeps us from a dead cron
                        pass            
    finally:
        if config.cache:
            log.info("Done with cache")
            storage.close()
        else:
            log.info("Without caching")
    log.info("Finished run in %f seconds" % (time.time() - start))  
    return 'Finished importing %d items' % new_entry_count

if __name__ == '__main__':
    cron_fetch_feeds()