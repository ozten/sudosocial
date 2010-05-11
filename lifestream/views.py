import datetime
import hashlib
import logging
import re

import feedparser
import jsonpickle
import simplejson as json

from django.db import IntegrityError
import django.utils.hashcompat as hashcompat
import django.template
import django.template.loaders
import django.http
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache

import lifestream.models
import patchouli_auth.preferences

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
    #rawEntries = lifestream.models.Entry.objects.order_by('last_published_date').reverse().all()[:50]
    rawEntries = lifestream.models.Entry.objects.order_by('last_published_date').reverse().filter(feed__streams__user__username=username, feed__streams__name__exact = streamname)[:50]
    entries = []
    renderedEntries = []
    
    identities = []
    identityCount = {}
    entriesWithIdentity = {}
    
    for entry in rawEntries:
        jsn = jsonpickle.decode(entry.raw)
        guid = entry.feed_id + entry.guid
        if jsn['title'].find('SXSW') > 0:
            log.debug(str(jsn))
        feedType = websiteFeedType(jsn)        
        #hooks = __import__(feedType)
        exec "from %s import hooks" % feedType
        entryVariables = hooks.prepareEntry(jsn, log)
        
        t = django.template.loader.select_template(('foo', feedType + '/entry.html'))
        c = django.template.Context(entryVariables)
        renderedEntries.append(t.render(c))
        #entries.append({'content': content})
        entriesWithIdentity[guid] = {'tags': []}
        
        for tag in entryVariables['tags']:
            t = tag['tag'].lower()
            #Skip List
            if 'ping.fm' == t:
                continue
            if not t in identityCount:
                tagName = tag['tag'].capitalize()
                if 'name' in tag:
                    tagName = tag['name']
                identityCount[t] = {'count': 0, 'name': tagName, 'tag': t}
            entriesWithIdentity[guid]['tags'].append(t)
            log.debug("Fixing " + str(identityCount[t]['count']))
            identityCount[t]['count'] = identityCount[t]['count'] + 1
            #identities.append({'name': t.capitalize(), 'tag': t.lower()})
            identities.append(identityCount[t]) # should only copy top N
        """
        if 'tags' in jsn:
            tagName = None
            for tag in jsn['tags']:
                if 'term' in tag:
                    tagName = 'term'
                else:
                    log.debug("Fix me, saw tags, but term is not the key\n" + str(jsn['tags']))
                
                
                if tagName:
                    for t in tag[tagName].split():
                        #Skip List
                        if 'ping.fm' == t.lower():
                            continue
                        if not t.lower() in identityCount:
                            identityCount[t.lower()] = {'count': 0, 'name': t.capitalize(), 'tag': t.lower()}
                        entriesWithIdentity[guid]['tags'].append(t.lower())
                        log.debug("Fixing " + str(identityCount[t.lower()]['count']))
                        identityCount[t.lower()]['count'] = identityCount[t.lower()]['count'] + 1
                        #identities.append({'name': t.capitalize(), 'tag': t.lower()})
                        identities.append(identityCount[t.lower()]) # should only copy top N
                        
        elif 'category' in jsn:
            identities.append({'name': jsn['category'], 'tag': jsn['category']})
    """
    # This should be it's own plugin... not in views.py
    identities = []
    for _ in range(5):
        #log.debug(sorted(identityCount.items(), cmp=cmpIdentity))
        identityList = sorted(identityCount.values(), cmp=cmpIdentity)
        # We skip of up to 5 current topics
        if len(identityList) == 0 or (not identityList[0]['count'] > 1):
            break;
        identities.append(identityCount.pop(identityList[0]['tag']))
        for k, value in entriesWithIdentity.items():
            if identityList[0]['tag'] in value['tags']:
                # nuke entry
                for t in value['tags']:
                    log.debug("Removing " + t)
                    # Skips t == identityList[0]['tag'], which we've already removed
                    if t in identityCount:
                        identityCount[t]['count'] -= 1
                # remove this entry
                log.debug("Removing guid " + k)
                entriesWithIdentity.pop(k)
    
    #for k, v in identityCount:
    #    pass
    # highlander... now that we know #1, we have to adjust identityCount and dis-count uses where this tag was present with another tag
    # on the same item...
    """
    entries = [
        entry[feed_id+guid] = [{tag, count}, {tag, count}]
    ]
    identityCount {
        'tag': {tag, name, count, entries[feed_id+guid, feed_id+guid]}
    }
    1 load all entries
    2 update identityCount
    3.1 if empty, break
    3.2 sort by count
    4 pop top tag
    5.1 if top tags > 5, break
    5.2 remove all entres with that tag
    6 goto 2
    """
    user = User.objects.get(username=username)    
    #identity
    #renderedEntries.append(renderProfile(request), identities)
    profile = renderProfile(request, user, identities)
    
    #{ 'entries': entries, },
    
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
                'username': username,
                }
    
def cmpIdentity(x, y):
    #xkey, xvalue = x
    #ykey, yvalue = y
    #log.debug("Comparing " + str(xvalue) + " to " + str(yvalue))
    return cmp(y['count'], x['count'])
    
def renderProfile(request, user, identities):
    """ Quick n dirty, would be DB driven """
    sourcesResults = lifestream.models.Feed.objects.order_by('url').filter(user__username=user.username)
    sources = []
    for s in sourcesResults:
        if s.title:
            sources.append({'title': s.title, 'url': s.url})
    
    # avatar
    
    gravatarHash = hashlib.md5(user.email).hexdigest()
    avatar_url = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash
    
    t = django.template.loader.select_template(('foo', 'lifestream/profile_blurb.html'))
    c = django.template.Context(
        {'avatar_src': avatar_url, 'avatar_width':'80', 'avatar_height':'80',
         'user': user,
         'username': user.username,
         'preferences': json.loads(user.get_profile().properties),
         'sources': sources,
         'identities': identities})
    return t.render(c)
    
def websiteFeedType(entryJson):
    if 'link' in entryJson:
        log.debug(entryJson['link'])
        if re.search('^.*reddit\.com/.*$', entryJson['link']):
            return 'reddit'
        elif 'summary_detail' in entryJson and 'base' in entryJson['summary_detail'] and re.search('^.*delicious\.com/.*$', entryJson['summary_detail']['base']):
            return 'delicious'
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