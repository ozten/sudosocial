from django.conf.urls.defaults import *
from django.views.static import *

""" TODO For hosted apps, this isn't a problem
             For self-hosted apps... automate checking
             For self-hosted dev mode... this needs work ... Add code to automatically figure this out """

handler404 = 'streamManager.views.page_not_found'
handler500 = 'streamManager.views.server_error'

urlpatterns = patterns('',    
    (r'^.well-known/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/aking/patchouli/static/.well-known/'}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/aking/patchouli/static/'}),
    (r'^$', 'patchouli.streamManager.views.homepage', {}, 'homepage'),
    (r'^auth/', include('patchouli.patchouli_auth.urls')),
    (r'^manage/', include('patchouli.streamManager.urls')),
    (r'^u/', include('patchouli.lifestream.urls')),
    #(r'^openid/logout$', 'django.contrib.auth.views.logout', {'next_page':'/openid/login'}),
    # temporarily now auth
    (r'^openid/', include('django_openid_auth.urls')),
)
