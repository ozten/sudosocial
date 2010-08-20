# coding=utf-8

import simplejson

import patchouli_auth.models
import lifestream.models

def getPreferences(user):
    # Put all known preferences here...
    profileProps = {
        'publish_email':False,
        }
    try:
        # TODO cache by username
        profile = user.get_profile()
        existingProps = simplejson.loads( profile.properties )
        # Pick up any new Properties, override with users choices
        profileProps.update(existingProps)
    except patchouli_auth.models.UserProfile.DoesNotExist, e:
        profile = patchouli_auth.models.UserProfile()
        profile.user = user
        profile.properties = simplejson.dumps(profileProps)
        profile.save()
    return profileProps

def savePreferences(user, properties):
    try:
        profile = user.get_profile()
        profile.properties = simplejson.dumps( properties )
        profile.save()
    except patchouli_auth.models.UserProfile.DoesNotExist, e:
        # Violates a pre-condition that getPreferences will be called atleast once before savePreferences is called..
        pass
    
def getPageProperties(page):
    """ Loads the properties for a Page.
        This includes migrating any settings
        for new code """
    after_profile_html_area = """
<!-- Give props to Robert Podgórski -->
<h5>Firefoxzilla protects the city</h5>
<div>Background imagery By <a href="http://creative.mozilla.org/people/blackmoondev">Blackmoondev</a></div>
    """
    pageProps = {
        'page_lang': 'en',
        'page_lang_dir': 'LTR',
        'before_stream_html_area': '',
        'after_stream_html_area': '',

        'show_profile_blurb': True,
        'show_follow_me_links': True,

        'before_profile_html_area': '',
        'after_profile_html_area': after_profile_html_area,
        
        'js_type': 'default',
        'js_value': '',
        
        'css_type': 'default',
        'css_value': '',
        
        'processing_js': '',

        'stream_ids': []
    }
    
    existingProps = simplejson.loads(page.config)
    pageProps.update(existingProps)
    if 0 == len(pageProps['stream_ids']):
        # Repair and save
        streams = (lifestream.models.Stream.objects.all()
                      .order_by('id')
                      .filter(webpage__id = page.id))
        for stream in streams:
            pageProps['stream_ids'].append(stream.id)
        savePageOrStreamProperties(page, pageProps)
    return pageProps    

def removeStreamFromPage(webpage, stream):
    props = getPageProperties(webpage)
    if stream.id in props['stream_ids']:
        props['stream_ids'].remove(stream.id)
        savePageOrStreamProperties(webpage, props)
        stream.delete()
        return True
    return False

def savePageOrStreamProperties(model, properties):
    """ Given a Page or Stream model, persists the
        properties """
    model.config = simplejson.dumps(properties)
    model.save()
