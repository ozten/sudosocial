# coding=utf-8

import simplejson

import patchouli_auth.models

def getPreferences(user):
    # Put all known preferences here...
    profileProps = {
        'css_url': 'default',
        'javascript_url': 'default',
        'processing_js': '',
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
        'before_stream_html_area': 'before stream',
        'after_stream_html_area': 'after stream',
        'show_profile_blurb': True,
        'show_follow_me_links': True,
        'before_profile_html_area': 'before profile',
        'after_profile_html_area': after_profile_html_area,
    }
    
    existingProps = simplejson.loads(page.config)
    pageProps.update(existingProps)
    return pageProps

def savePageOrStreamProperties(model, properties):
    """ Given a Page or Stream model, persists the
        properties """
    model.config = simplejson.dumps(properties)
    model.save()