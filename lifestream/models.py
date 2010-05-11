from django.db import models
from django.forms import ModelForm

from django.contrib.auth.models import User

import django.forms

class Stream(models.Model):
    """ A Stream is like a 'page'. A stream is combosed of Feeds. """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=140)    
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='Last Modified')

    def __unicode__(self):
        return self.name

class Feed(models.Model):
    title = models.CharField(max_length=140)
    url = models.CharField(max_length=2048)
    url_hash = models.CharField(max_length=32, primary_key=True)
    user = models.ForeignKey(User)
    streams = models.ManyToManyField(Stream)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='Last Modified')
    
    def to_primitives(self):
        return {'url': self.url, 'url_hash': self.url_hash, 'created_date': str(self.created_date), 'updated_date': str(self.updated_date)}
    
    def __unicode__(self):
        return self.url
    
class FeedForm(ModelForm):
    class Meta:
        model = Feed        
        exclude = ('title', 'user', 'streams', 'url_hash', 'created_date', 'updated_date')
        # excluded columns won't be displayed in the form, but you can't set their values
        # either
        
class Entry(models.Model):
    feed = models.ForeignKey(Feed)
    # 960 so we can keep it under 1000 bytes MYSQL index limit
    guid = models.CharField(max_length=960) # not necissarily unique across feeds, but unique in this feed
    raw = models.TextField()
    last_published_date = models.DateTimeField() # Feed entry updated field
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='Last Modified')
# CREATE UNIQUE INDEX `lifestream_entry_feed_id_guid` ON `lifestream_entry` (`feed_id`, `guid`);