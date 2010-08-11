from django.conf.urls.defaults import *

urlpatterns = patterns('patchouli_auth.views',
    (r'^confirm_profile$', 'confirm_profile', {}, 'confirm_profile'),
    (r'^profile/(?P<username>\w+)$', 'profile', {}, 'edit_profile'),
    (r'^profile/(?P<username>\w+)/delete$', 'delete_profile', {}, 'delete_profile'),
    (r'^logout$', 'logout', {}, 'logout'),
    (r'^gravatar/(?P<email>[^/]+)$', 'gravatar'),
    
    (r'^$', 'account_checkauth', {}, 'auth_or_editor'),
)
