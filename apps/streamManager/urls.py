from django.conf.urls.defaults import *

urlpatterns = patterns('streamManager',
    (r'^account/(?P<username>\w+)$', 'views.manage'),
    (r'^account/(?P<username>\w+)/stream/(?P<stream_id>\d+)/feed/(?P<feed_id>\w+)$', 'views.edit_feed'),
    (r'^account/(?P<username>\w+)/stream/(?P<stream_id>\d+)/preview_feed/(?P<feed_id>\w+)$', 'views.preview_feed'),
    (r'^stream/design$', 'views.manage_page_design'),
    (r'^stream/(?P<username>\w+)/s/(?P<page_name>\w+)$', 'views.manage_page'),
    
    (r'^page/(?P<page_name>\w+)$', 'views.manage_page_widgets'),
    
    (r'^urls/(?P<username>\w+)$', 'views.urls'),
    (r'^url/(?P<username>\w+)/(?P<feed_url_hash>\w+)$', 'views.url'),
    (r'^reset_url/(?P<username>\w+)/(?P<feed_url_hash>\w+)$', 'views.reset_url'),
    
    (r'^stream/(?P<stream_id>.*)/entry/(?P<entry_id>.*)$', 'views.entry'),
)
