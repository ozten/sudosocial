from django.conf.urls.defaults import *

urlpatterns = patterns('lifestream.views',
    (r'^(?P<username>\w+)/s/(?P<streamname>\w+)$', 'stream'),
    (r'^(?P<username>\w+)/embed/stream/(?P<streamname>\w+)\.js$', 'js_embed_stream'),
    (r'^(?P<username>\w+)', 'profile'),
)