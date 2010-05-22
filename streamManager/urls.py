from django.conf.urls.defaults import *

urlpatterns = patterns('streamManager',
    (r'^account/(?P<username>\w+)$', 'views.manage'),
    (r'^stream/design$', 'views.manage_stream_design'),
    (r'^stream/(?P<username>\w+)/s/(?P<streamname>\w+)$', 'views.manage_stream'),
    
    (r'^urls/(?P<username>\w+)$', 'views.urls'),
    (r'^url/(?P<username>\w+)/(?P<feed_url_hash>\w+)$', 'views.url'),
    
    (r'^entry/(?P<entry_id>.*)$', 'views.entry'),
)