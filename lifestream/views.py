import hashlib
import logging
import re

import jsonpickle
import simplejson as json

import django.utils.encoding
import django.template
import django.template.loaders
import django.http
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from django.contrib.auth.models import User

import lifestream.models
import patchouli_auth.preferences
from patchouli.plugins.social_identities import SocialIdentityFromTagsPlugin

logging.basicConfig( level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', )
log = logging.getLogger()

def profile(request, username):
    return stream(request, username, 'home')
    
def js_embed_stream(request, username, streamname):

    pageVars = common_stream(request, username, streamname)

    embedString = render_to_string('lifestream/embed.html', pageVars)
    # do something like document.write("escaped string");
    embedString = json.dumps(embedString)
    embedString = embedString.replace('</script>', '</scr");document.write("ipt>')
    
    javaScriptString = "document.write(%s);" % embedString
    return django.http.HttpResponse(javaScriptString)


def stream(request, username, streamname):
    ctx = django.template.RequestContext(request)
    ctx.autoescape=False #TODO Need more thinking around best way to handle this...
    
    pageVars = common_stream(request, username, streamname)

    return render_to_response('lifestream/profile.html',
                          pageVars,
                          context_instance=ctx,
                          )

def common_stream(request, username, streamname):
    username = username.lower()
    user = User.objects.get(username=username)
    rawEntries = (lifestream.models.Entry.objects.order_by('-last_published_date')
                  .filter(feed__user=user,
                          feed__streams__name__exact = streamname,
                          visible=True))[:50]
    entries = []
    plugins = []
    if username == 'ozten':
        plugins = [SocialIdentityFromTagsPlugin()]
    renderedEntries = render_entries(rawEntries, plugins)
    
    profile = renderProfile(request, user, plugins)
        
    preferences = patchouli_auth.preferences.getPreferences(user)
    
    if 'default' == preferences['javascript_url']:
        js_url = '/static/js/behavior.js'
    else:
        js_url = preferences['javascript_url']
        
    if 'default' == preferences['css_url']:
        css_url = '/static/css/stylo.css'
    else:
        css_url = preferences['css_url']
    
    return {'entries': renderedEntries,
                'profile': profile,
                'css_url': css_url,
                'javascript_url': js_url,
                'processing_js': preferences['processing_js'],
                'stream_name': streamname,
                'user': user,
                'username': username}
            
def render_entries(rawEntries, plugins=[]):
    """ plugins - list of functions to be run once for each entry's variables """
    renderedEntries = []    
    for entry in rawEntries:
        jsn = jsonpickle.decode(entry.raw)
        guid = entry.feed_id + entry.guid

        feedType = websiteFeedType(jsn)        
        #hooks = __import__(feedType)
        # TODO use http://docs.python.org/py3k/library/importlib.html
        exec "from %s import hooks" % feedType
        entry_variables = hooks.prepare_entry(jsn, log)
        [plugin.modify_entry_variables(jsn, entry_variables) for plugin in plugins]
        
        t = django.template.loader.select_template(('foo', feedType + '/entry.html'))
        c = django.template.Context(entry_variables)
        renderedEntries.append(t.render(c))        
        [p.observe_stream_entry(entry, entry_variables) for p in plugins]
    [p.post_observe_stream_entries() for p in plugins]    
    return renderedEntries
        
def renderProfile(request, user, plugins):
    sourcesResults = lifestream.models.Feed.objects.order_by('url').filter(user=user)    
    sources = [{'title': s.title, 'url':s.url} for s in sourcesResults]
    
    # avatar
    gravatarHash = hashlib.md5(
        django.utils.encoding.smart_str(user.email)).hexdigest()
    avatar_url = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash

    show_fn = False
    if user.first_name or user.last_name:
        show_fn = True
    data = {'avatar_src': avatar_url, 'avatar_width':'80', 'avatar_height':'80',
            'user': user,
            'show_fn': show_fn,
            'username': user.username,
            'preferences': json.loads(user.get_profile().properties),
            'sources': sources}
    [data.update(plugin.template_variables()) for plugin in plugins]
    
    #data.update()
    t = django.template.loader.select_template(('foo', 'lifestream/profile_blurb.html'))
    c = django.template.Context(data)
    return t.render(c)
    
def websiteFeedType(entryJson):
    if 'link' in entryJson:
        #log.debug("websiteFeedType %s" % entryJson['link'])
        if 'summary_detail' in entryJson and 'base' in entryJson['summary_detail'] and re.search('^.*delicious\.com/.*$', entryJson['summary_detail']['base']):
            return 'delicious'
        elif re.search('^.*identi\.ca/.*$', entryJson['link']):
            return 'identica'
        elif re.search('^.*reddit\.com/.*$', entryJson['link']):
            return 'reddit'
        elif 'title_detail' in entryJson and 'base' in entryJson['title_detail'] and re.search('^.*delicious\.com/.*$', entryJson['title_detail']['base']):
            return 'delicious'
        elif re.search('^.*twitter\.com/.*$', entryJson['link']):
            return 'twitter_com'
        elif re.search('^.*flickr\.com/.*$', entryJson['link']):
            return 'flickr'
        else:
            return'generic'
    else:
        raise RuntimeError, 'Hmm, dont know quite what to do here, no url'