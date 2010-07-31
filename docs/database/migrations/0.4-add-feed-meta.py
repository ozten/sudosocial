import sys
sys.path.append('/home/aking/patchouli')

from django.core.management import setup_environ
import settings
setup_environ(settings)

import logging
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(process)d %(message)s', )
log = logging.getLogger()

from lifestream.models import Stream
from lifestream.models import Webpage
import lifestream.models

import patchouli_auth.preferences

streams = Stream.objects.all()
for stream in streams:
    log.info("Checking page exists for %s owned by %s" % (stream.name, stream.user.username))
    try:
        Webpage.objects.get(name=stream.name, user=stream.user)        
    except Webpage.DoesNotExist:
        webpage = Webpage(name=stream.name, user=stream.user, config='{}')
        log.info("Saving %s for %s" % (stream.name, stream.user.username))
        patchouli_auth.preferences.savePageOrStreamProperties(
            webpage, patchouli_auth.preferences.getPageProperties(webpage))
        
# 2nd step clean up user preferences and push them into the pagePreferences
from lifestream.models import User
for user in User.objects.all():
    user_pref = patchouli_auth.preferences.getPreferences(user)
    css_type = 'default'
    css_value = ''
    if 'css_url' in user_pref and user_pref['css_url'] != 'default':
        css_type = 'url'
        css_value = user_pref['css_url']
        del user_pref['css_url']
    if 'css_url' in user_pref:
        del user_pref['css_url']
    js_type = 'default'
    js_value = ''
    if 'js_url' in user_pref and user_pref['js_url'] != 'default':
        js_type = 'url'
        js_value = user_pref['js_url']
    if 'js_url' in user_pref:
        del user_pref['js_url']
    processing_js = ''
    if 'processing_js' in user_pref:
        processing_js = user_pref['processing_js']        
        del user_pref['processing_js']
    log.info("Saving %s %s" % (user.username, str(user_pref)))
    patchouli_auth.preferences.savePreferences(user, user_pref)
    
    for page in Webpage.objects.filter(user=user):
        page_pref = patchouli_auth.preferences.getPageProperties(page)
        page_pref['css_type'] = css_type
        page_pref['css_value'] = css_value
        page_pref['js_type'] = js_type
        page_pref['js_value'] = js_value
        page_pref['processing_js'] = processing_js
        log.info("Saving webpage %s" % str(page_pref))
        patchouli_auth.preferences.savePageOrStreamProperties(page, page_pref)
log.info("Done success")
