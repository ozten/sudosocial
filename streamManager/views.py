import datetime
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
from django.contrib.auth.decorators import login_required

import lifestream.models
import patchouli_auth.preferences

logging.basicConfig( level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', )
log = logging.getLogger()

HACKING_MESSAGE = 'Hack much? Your request has been logged. Authorities have been dispatched.'
        
@login_required
def manage_profile(request):
    return django.http.HttpResponse("TODO, let you edit your profile info")

@login_required
def manage(request, username):
    if request.user.username == username:
        streams = lifestream.models.Stream.objects.filter(user=request.user).all()
        if len(streams) == 1:            
            return manage_stream(request, username, 'home')
        else:
            return manage_all_streams(request, username)
    else:
        return django.http.HttpResponse(HACKING_MESSAGE, status=400)
@login_required    
def manage_stream(request, username, streamname):
    if request.user.username == username:
        feeds = lifestream.models.Feed.objects.filter(user=request.user).all()
        streams = lifestream.models.Stream.objects.filter(user=request.user).all()
        feedModel = lifestream.models.FeedForm()
        
        streamName2Feed = {}
        for feed in feeds:
            for stream in feed.streams.all():
                if not stream.name in streamName2Feed:
                    streamName2Feed[stream.name] = []
                streamName2Feed[stream.name].append(feed)                
        for stream in streams:
            if stream.name in streamName2Feed:
                stream.feeds = streamName2Feed[stream.name]
        for s in streams:
            s.url = "/u/%s/s/%s" % (username, s.name)
            
        preferences = patchouli_auth.preferences.getPreferences(request.user)
        
        return render_to_response('stream_editor.html',
                              { 'feeds': feeds,
                                'unusedFeeds': [],
                                'form': feedModel,
                                'request': request,
                                'streams': streams,
                                'streamname': streams[0] if (len(streams) > 0) else  '',
                                'username': request.user.username,
                                'preferences': preferences},
                              context_instance=django.template.RequestContext(request))
    else:
        return django.http.HttpResponse(HACKING_MESSAGE, status=400)
        
@login_required    
def manage_all_streams(request, username):
    if request.user.username == username:
        feeds = lifestream.models.Feed.objects.filter(user=request.user).all()
        streams = lifestream.models.Stream.objects.filter(user=request.user).all()
        feedModel = lifestream.models.FeedForm()
        
        streamName2Feed = {}
        for feed in feeds:
            for stream in feed.streams.all():
                if not stream.name in streamName2Feed:
                    streamName2Feed[stream.name] = []
                streamName2Feed[stream.name].append(feed)                
        for stream in streams:
            if stream.name in streamName2Feed:
                stream.feeds = streamName2Feed[stream.name]
        for s in streams:
            s.url = "/u/%s/s/%s" % (username, s.name)
        
        return render_to_response('index.html',
                              { 'feeds': feeds,
                                'unusedFeeds': [],
                                'form': feedModel,
                                'request': request,
                                'streams': streams,
                                'streamname': streams[0] if (len(streams) > 0) else  '',
                                'username': request.user.username,},
                              context_instance=django.template.RequestContext(request))
    else:
        return django.http.HttpResponse(HACKING_MESSAGE, status=400)

@login_required
def urls(request, username):
    if request.user.username == username:
        if 'POST' == request.method:
            # url_hash is 'exclude' aka editable=False, so we have to create a model
            # and set the url_hash, in order to get the data into the db
            feed_url_hash = hashcompat.md5_constructor(request.POST['url']).hexdigest()
            params = request.POST.copy()
            #params['streams'] = []
            streams = lifestream.models.Stream.objects.filter(user=request.user, name='home')
            if len(streams) > 0:
                #params['streams'].append(str(streams[0].id))
                pass
            #params['user'] = str(request.user.id)
            aFeed = lifestream.models.Feed(url_hash = feed_url_hash, user=request.user)
            if len(streams) > 0:
                aFeed.streams.add(streams[0])
            form = lifestream.models.FeedForm(params, instance=aFeed)
            if form.is_valid():
                log.debug('valid, saving to %s' % (feed_url_hash))
                
                #newFeedForm = form.save(commit=False)
                newFeedForm = form.save()
                #newFeedForm.user = request.user
                
                #newFeedForm.streams.add(streams)
                #newFeedForm.save_m2m()
                newFeedForm.save()
                
                newFeed = lifestream.models.Feed.objects.get(pk=feed_url_hash)
                log.debug('formatting response')
                return django.http.HttpResponse(json.dumps({"message":"OK", "feed": newFeed.to_primitives()}), mimetype='application/json')
                #return django.http.HttpResponse('{"message":"OK"}', mimetype='application/json')
            else:
                errors = ''
                for error in form.errors:
                    errors += error + ': '
                    for msg in form.errors[error]:
                        errors += ' ' + msg
                return django.http.HttpResponse('{"message":"Error ' + errors + '"}', mimetype='application/json', status=400)
        else:
            return django.http.HttpResponse('{"message":"Error unsupported method"}', mimetype='applicaiton/json', status=400)
    else:
        return django.http.HttpResponse('{"message":"' + HACKING_MESSAGE + '"}', mimetype='applicaiton/json', status=400)

@login_required
def url(request, username, feed_url_hash):
    if request.user.username == username:
        if 'DELETE' == request.method:
            feed = lifestream.models.Feed.objects.get(pk=feed_url_hash)
            feed.delete()
            return django.http.HttpResponse('{"message":"OK"}', mimetype='application/json')
        else:
            return django.http.HttpResponse('Hi there')
    else:
        return django.http.HttpResponse('{"message":"' + HACKING_MESSAGE + '"}', mimetype='applicaiton/json', status=400)

def cron_fetch_feeds(request, key):
    """ """
    if key != 'Miracles192010':
        return django.http.HttpResponse('ERROR')
    newEntryCount = 0
    feeds = lifestream.models.Feed.objects.all()
    for feed in feeds:
        stream = feedparser.parse(feed.url)
        if 1 == stream.bozo and 'bozo_exception' in stream.keys():
            log.error('Unable to fetch %s Exception: %s', feed.url, stream.bozo_exception)
        else:
            log.info('Processing %s', feed.url)
            if 'feed' in stream and 'title' in stream.feed:
                log.info('Processing title: %s', stream.feed.title)
            if 'feed' in stream and 'title' in stream.feed and feed.title != stream.feed.title:
                feed.title = stream.feed.title
                try:
                    feed.save()
                except Exception, x:
                    log.error("Unable to update feed title from=%s to=%s" % (feed.title, stream.title))
                    log.error(x)
            else:
                if (not 'feed' in stream) or (not 'title' in stream.feed):
                    log.warn("Feed doesn't have a title property")
                    log.info(stream)
            for entry in stream.entries:
                
                jsonEntry = jsonpickle.encode(entry)
                entryGuid = ''
                if 'guid' in entry:
                    entryGuid = entry.guid
                else:
                    entryGuid = hashcompat.md5_constructor(jsonEntry).hexdigest()
                yr, mon, d, hr, min, sec = entry.updated_parsed[:-3]
                lastPub = datetime.datetime(yr, mon, d, hr, min, sec)
                newEntry = lifestream.models.Entry(feed=feed, guid=entryGuid, raw=jsonEntry, last_published_date=lastPub)
                try:
                    newEntry.save()
                    newEntryCount += 1
                except IntegrityError, e:
                    log.info('Skipping duplicate entry %s, caught error: %s', entryGuid, e)
    return django.http.HttpResponse('Finished importing %d items' % newEntryCount)

@login_required
def manage_stream_design(request):
    if 'POST' == request.method:
        preferences = patchouli_auth.preferences.getPreferences(request.user)        
        params = request.POST.copy()
        log.info(str(preferences))
        
        if 'default' == params['css_type']:
            preferences['css_url'] = 'default'
        else:
            preferences['css_url'] = params['css_url']
            
        if 'default' == params['js_type']:
            preferences['javascript_url'] = 'default'
        else:
            preferences['javascript_url'] = params['js_url']
        
        preferences['processing_js'] = params['processing']        
        patchouli_auth.preferences.savePreferences(request.user, preferences)
        return django.http.HttpResponseRedirect('/auth')
        
import django.http
from django.shortcuts import render_to_response

def homepage(request):
    
    return render_to_response('homepage.html',
                          {'css_url': '/static/css/stylo.css'},
                          context_instance=django.template.RequestContext(request))
