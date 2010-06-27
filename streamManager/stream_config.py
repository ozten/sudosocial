"""
Contains StreamConfig
"""
import logging

import simplejson


from django.conf import settings

logging.basicConfig(filename=settings.LOG_FILENAME, level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', )
log = logging.getLogger()

class StreamConfig(object):
    """ A Stream has a few configurable aspects.
        * The order of the feeds.
        
        * For a Feed, should entries be shown as soon
        as they are imported, or should they be hidden
        by default.
    """
    def __init__(self, config):
        """ 
        config - JSON encoded string
        stream - Database results for a stream
        
        Sample Config:
        
        {
          'style': 'home',
          'feeds': [
            {
              'url_hash': '8aebbd89274c9356403136ab9e9b7a6d',
              'entries_visible_default': false
            }, ...s
          ]
        }
        Constructor repairs the config, giving default values
        """
        try:
            self.config = simplejson.loads(config)
        except Exception, error:
            self.config = {}
            
        if not 'style' in self.config:
            # The home style implies entries_visible_default = true
            self.config['style'] = 'home'
        if not 'feeds' in self.config:
            self.config['feeds'] = []
        
    def ensureFeedsConfig(self, feeds):
        active_feeds = {}
        for feed in feeds:
            if not hasattr(feed, 'url_hash'):
                raise InvalidFeedError("Feed is missing an url_hash")
            active_feeds[feed.url_hash] = True
            self.ensureFeedConfig(feed)
        for feed_config in self.config['feeds'][:]:
            if feed_config['url_hash'] not in active_feeds:
                #log.debug("Removing %s", feed_config)
                self.config['feeds'].remove(feed_config)
            else:
                #log.debug("Keeping %s", feed_config)
                pass
            
    def ensureFeedConfig(self, feed):
        """ Make sure this feed is in the feedsConfig """
        
        for feedConfig in self.config['feeds']:
            if 'url_hash' not in feedConfig:
                raise InvalidFeedError("FeedConfig is missing a url_hash")
            if feed.url_hash == feedConfig['url_hash']:
                if 'entries_visible_default' not in feedConfig:                    
                    #if 'home' == self.config.style:
                    # Future settings... research = False, etc
                    feedConfig['entries_visible_default'] = True                    
                return self
        # No matches.. add to end of config list
        self.add_feed(feed, True)
        return self
    
    def add_feed(self, feed, visible):
        """ Adds a new feed to the feeds configuration
            feed - A lifestream.models.Feed
            visible - Should entries be visible by default for this feed """
        self.config['feeds'].append({'url_hash':feed.url_hash, 'entries_visible_default': visible})
    
    def to_json(self):
        return simplejson.dumps(self.config)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.to_json()

class InvalidFeedError(Exception):
    """ A bad Feed was detected """
    def __init__(self, value):
        self.value = value