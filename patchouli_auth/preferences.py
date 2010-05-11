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