from django.conf.urls.defaults import *

urlpatterns = patterns('patchouli_auth.views',
    (r'^confirm_profile$', 'confirm_profile'),
    (r'^logout$', 'logout'),
    (r'^$', 'account_checkauth'),
)
