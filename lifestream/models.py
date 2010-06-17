from django.db import models
from django.forms import ModelForm
from django.forms import ModelChoiceField
import django.forms.models
from django.contrib.auth.models import User

class Stream(models.Model):
    """ A Stream is like a 'page'. A stream is combosed of Feeds. """
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
    
class FeedForm(ModelForm):
    class Meta:
        model = Feed        
        exclude = ('title', 'user', 'streams', 'url_hash',
                   'etag', 'last_modified', 'enabled', 'disabled_reason',
                   'created_date', 'updated_date')
        # excluded columns won't be displayed in the form,
        # but you can't set their values either
        
class Entry(models.Model):
    feed = models.ForeignKey(Feed)
    # 960 so we can keep it under 1000 bytes MYSQL index limit
    # not necissarily unique across feeds, but unique in this feed
    guid = models.CharField(max_length=960) 
    raw = models.TextField()
    visible = models.BooleanField()
    # Feed entry updated field
    last_published_date = models.DateTimeField() 
    created_date = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Created On')
    updated_date = models.DateTimeField(auto_now=True,
                                        verbose_name='Last Modified')
# CREATE UNIQUE INDEX `lifestream_entry_feed_id_guid` ON
#   `lifestream_entry` (`feed_id`, `guid`);
# ALTER TABLE lifestream_entry ADD COLUMN `visible`
#    bool NOT NULL DEFAULT true;