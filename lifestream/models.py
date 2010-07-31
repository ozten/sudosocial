import logging

from django.conf import settings

from django.db import models
from django.forms import ModelForm
from django.forms import ModelChoiceField
import django.forms.models
from django.contrib.auth.models import User

from streamManager.stream_config import StreamConfig

logging.basicConfig(filename=settings.LOG_FILENAME, level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', )
log = logging.getLogger()

class Webpage(models.Model):
    """ A webpage is composed of Streams, page widgets,
        and other funage.    
    """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=140)
    title = models.CharField(max_length=140)
    # PageConfig
    config = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True,
                                        verbose_name='Last Modified')
    
class Stream(models.Model):
    """ A stream is composed of Feeds. """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=140)
    # StreamConfig
    config = models.TextField()
    # StreamEditList
    edit_list = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True,
                                        verbose_name='Last Modified')
    # ALTER TABLE lifestream_stream ADD COLUMN `config` longtext NOT NULL;
    # ALTER TABLE lifestream_stream ADD COLUMN  `edit_list` longtext NOT NULL;

    def __unicode__(self):
        return self.name

class Feed(models.Model):
    title = models.CharField(max_length=140)
    url = models.CharField(max_length=2048)
    url_hash = models.CharField(max_length=32, primary_key=True)
    user = models.ForeignKey(User)
    streams = models.ManyToManyField(Stream)
    # HTTP Headers
    etag = models.CharField(max_length=140)
    last_modified = models.DateTimeField()
    
    # If a feed has issues, it will be disabled
    enabled = models.BooleanField(default=True)
    disabled_reason = models.CharField(max_length=2048)
    
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True,
                                        verbose_name='Last Modified')
    
    def to_primitives(self):
        return {'url': self.url, 'title': self.title, 'url_hash': self.url_hash,
                'created_date': str(self.created_date),
                'updated_date': str(self.updated_date)}
    
    def __unicode__(self):
        return self.url

# TODO: Split Feed into Feed and StreamFeed
# Feed - Singleton
""" class StreamFeed(models.Model):
    website_url = models.CharField(max_length=140)
    website_title = models.CharField(max_length=140) # this was Feed.title
    # url and url_hash stay on Feed
    user = models.ForeignKey(User)
    streams = models.ManyToManyField(Stream)
    
"""
    
class FeedForm(ModelForm):
    class Meta:
        model = Feed        
        exclude = ('title', 'user', 'streams', 'url_hash',
                   'etag', 'last_modified', 'enabled', 'disabled_reason',
                   'created_date', 'updated_date')
        # excluded columns won't be displayed in the form,
        # but you can't set their values either
        
class Entry(models.Model):
    """
    Single instance of an Entry from a Feed in the DB. This 
    can be reused and changed via a specific Stream's Feed
    as an StreamEntry
    """
    feed = models.ForeignKey(Feed)
    # 960 so we can keep it under 1000 bytes MYSQL index limit
    # not necissarily unique across feeds, but unique in this feed
    guid = models.CharField(max_length=960) 
    raw = models.TextField()

    # Feed entry updated field
    last_published_date = models.DateTimeField() 
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True,
                                        verbose_name='Last Modified')

class StreamEntry(models.Model):
    """
    This is the place to put data that can change for an entry based on
    which Stream it's in.
    """
    entry = models.ForeignKey(Entry)
    stream = models.ForeignKey(Stream)
    visible = models.BooleanField()
    # 0.5 migration adds unique constraint against entry, streams

stream_entries_cache = {}

def recent_entries(user, stream, count=150, only_visible=True):
    return _recent_entries(user, stream, 'ANY', count, only_visible)

def recent_feed_entries(user, stream, feed_id, count=150, only_visible=True):
    return _recent_entries(user, stream, feed_id, count, only_visible)

def _recent_entries(user, stream, feed_id, count=150, only_visible=True):
    # Grab entries for each feed basedon the stream constraints per feed
    stream_id = stream.id
    stream_config = StreamConfig(stream.config)
    feed_ids = []
    if 'ANY' == feed_id:
        for feed in stream_config.config['feeds']:
            feed_ids.append(feed['url_hash'])
    else:
        feed_ids.append(feed_id)

    entries = []
    for a_feed_id in feed_ids:
        feed_config = stream_config.feed_config(a_feed_id)
        query = (Entry.objects.order_by('-last_published_date')
                          .filter(feed__user=user,
                                  feed__url_hash=a_feed_id,
                                  feed__streams__id = stream_id))        
        # Visible is special, we want to see hidden items in the editor
        if only_visible:
            query = query.filter(streamentry__visible=True)
        # Lastly... LIMIT
        if 'enable_num_entries_shown' in feed_config and True == feed_config['enable_num_entries_shown'] and 'num_entries_shown' in feed_config:
            entries += query[0:feed_config['num_entries_shown']]
        else:
            entries += query[:count]

    entries = sorted(entries, compare_entries)
    entries = entries[:count]
    log.info("Got back %d entries", len(entries))
    
    # Performance tweak... We always also want to load all StreamEntry objects in one go. This isn't 
    # hooked up as a straight ont-to-one so select_related can't be used on Entry
    stream_entries = []
    for a_feed_id in feed_ids:
        feed_config = stream_config.feed_config(a_feed_id)
        query = (StreamEntry.objects.select_related()
                         .order_by('-entry__last_published_date')
                         .filter(entry__feed__url_hash=a_feed_id, stream__id=stream_id))
        if only_visible:
            query = query.filter(visible=True)
        # Lastly... LIMIT
        if 'enable_num_entries_shown' in feed_config and True == feed_config['enable_num_entries_shown'] and 'num_entries_shown' in feed_config:
            log.info("using config num_entires_shown")
            log.info(feed_config['num_entries_shown'])
            stream_entries += query[0:feed_config['num_entries_shown']]
        else:
            log.info("using 150")
            stream_entries += query[:count]
    log.debug("stream entries")
    log.debug(stream_entries)
    log.debug(django.db.connection.queries)

    for se in stream_entries:
        key = "%s_%d" % (str(stream_id), se.entry_id)
        stream_entries_cache[key] = se
    for e in entries:
        key = "%s_%d" % (str(stream_id), e.id)
        # Easy Access from templates
        if key in stream_entries_cache:
            e.stream_entry = stream_entries_cache[key]
        else:
            e.stream_entry = {}
    return entries

def compare_entries(a, b):
    if a.updated_date == b.updated_date:
        return 0
    elif a.updated_date < b.updated_date:
        return 1
    else:
        return -1

def stream_entry(stream_id, entry):
    key = "%s_%d" % (str(stream_id), entry.id)
    return stream_entries_cache[key]
