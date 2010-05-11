from django.conf.urls.defaults import *

urlpatterns = patterns('lifestream.views',
    (r'^(?P<username>\w+)/s/(?P<streamname>\w+)$', 'stream'),
    (r'^(?P<username>\w+)', 'profile'),
)