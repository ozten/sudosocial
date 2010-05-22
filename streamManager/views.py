import logging
import datetime

import simplejson as json

import django.http
import django.template
import django.template.loaders
import django.utils.hashcompat as hashcompat
import django.utils.encoding

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

import lifestream.models
import patchouli_auth.preferences
from patchouli.plugins.stream_editor import StreamEditorPlugin
from lifestream.views import render_entries
from streamManager.stream_config import StreamConfig

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
        
        stream = get_object_or_404(lifestream.models.Stream, user=request.user, name=streamname)
        stream_config = StreamConfig(stream.config)        
        feed_rows = stream.feed_set.all()
        stream_config.ensureFeedsConfig(feed_rows)
        feed_id_to_feed = {}
        for row in feed_rows:
            feed_id_to_feed[row.pk] = row
        feeds = []
        for feed in stream_config.config['feeds']:
            feed_row = feed_id_to_feed[feed['url_hash']]
            feeds.append({'url': feed_row.url,
                          'title': feed_row.title,
                          'pk': feed_row.pk,
                          'entries_visible_default': feed['entries_visible_default']})
        
        raw_entries = (lifestream.models.Entry.objects.order_by('-last_published_date')
                      .filter(feed__user=request.user,
                              feed__streams__name__exact = streamname))[:150]
        plugins = [StreamEditorPlugin(log)]
        entry_pair = zip(raw_entries, render_entries(raw_entries, plugins))        
        feed_model = lifestream.models.FeedForm()
                
        stream.url = "/u/%s/s/%s" % (username, stream.name)
            
        preferences = patchouli_auth.preferences.getPreferences(request.user)
        template_data = { 'feeds': feeds,
                                'entry_pair': entry_pair,
                                'unused_feeds': [],
                                'form': feed_model,
                                'request': request,
                                'stream': stream,
                                'stream_config': stream_config,
                                'username': request.user.username,
                                'preferences': preferences}
        [template_data.update(plugin.template_variables(template_data)) for plugin in plugins]
        return render_to_response('stream_editor.html',
                              template_data,
                              context_instance=django.template.RequestContext(request))
    else:
        return django.http.HttpResponse(HACKING_MESSAGE, status=400)
        
@login_required    
def manage_all_streams(request, username):
    if request.user.username == username:
        feeds = lifestream.models.Feed.objects.filter(user=request.user).all()
        streams = lifestream.models.Stream.objects.filter(user=request.user).all()
        stream_name2feed = {}
        for feed in feeds:
            for stream in feed.streams.all():
                if not stream.name in stream_name2feed:
                    stream_name2feed[stream.name] = []
                stream_name2feed[stream.name].append(feed)                
        for stream in streams:
            if stream.name in stream_name2feed:
                stream.feeds = stream_name2feed[stream.name]
        for stream in streams:
            stream.url = "/u/%s/s/%s" % (username, stream.name)
        return render_to_response('index.html',
                              { 'feeds': feeds,
                                'unused_feeds': [],
                                'request': request,
                                'streams': streams,
                                'streamname': streams[0] if streams else  '',
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
            feed_url_hash = hashcompat.md5_constructor(
                django.utils.encoding.smart_str(request.POST['url'])).hexdigest()
            params = request.POST.copy()
            #params['streams'] = []
            
            streams = lifestream.models.Stream.objects.filter(user=request.user,
                                                              name=params['streams[]'])
            if len(streams) == 0:
                raise Exception("No such stream")
                
            #params['user'] = str(request.user.id)
            a_feed = lifestream.models.Feed(url_hash = feed_url_hash, user=request.user, created_date=datetime.datetime.today())
            if len(streams) > 0:
                a_feed.streams.add(streams[0])
            form = lifestream.models.FeedForm(params, instance=a_feed)
            if form.is_valid():
                
                #new_feed_form = form.save(commit=False)
                new_feed_form = form.save()
                #new_feed_form.user = request.user
                
                #new_feed_form.streams.add(streams)
                #new_feed_form.save_m2m()
                new_feed_form.save()
                if len(streams) > 0:
                    stream_config = StreamConfig(streams[0].config)
                    stream_config.ensureFeedsConfig(streams[0].feed_set.all())
                    streams[0].config = stream_config.__unicode__()
                    streams[0].save()
                new_feed = lifestream.models.Feed.objects.get(pk=feed_url_hash)
                return django.http.HttpResponse(json.dumps({"message":"OK", "feed": new_feed.to_primitives()}), mimetype='application/json')
                #return django.http.HttpResponse('{"message":"OK"}', mimetype='application/json')
            else:
                errors = ''
                for error in form.errors:
                    errors += error + ': '
                    for msg in form.errors[error]:
                        errors += ' ' + str(msg)
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

def entry(request, entry_id):
    """
        change-visibility set to true - show entry
        change-visibility set to false - hide entry
    """
    if 'POST' == request.method:
        entry = get_object_or_404(lifestream.models.Entry, id=entry_id,feed__user=request.user)
        if entry:            
            if 'change-visibility' in request.POST and request.POST['change-visibility'] == 'true':
                entry.visible = True
            elif 'change-visibility' in request.POST and request.POST['change-visibility'] == 'false':
                entry.visible = False
            else:
                return django.http.HttpResponse(
                    '{"status":"ERROR", "error-message":"Change not understood"}',
                    mimetype='applicaiton/json', status=400)
            try:
                entry.save()
                fresh_entry = lifestream.models.Entry.objects.get(id=entry_id)
                payload = {'status': 'OK', 'guid': fresh_entry.guid,
                           'id': fresh_entry.id,
                           'visible': fresh_entry.visible}
                return django.http.HttpResponse(
                    json.dumps(payload), mimetype='applicaiton/json')
            except Exception, x:
                payload = {'status':'ERROR', 'error-message': str(x),
                           'description': 'Unable to save'}
                return django.http.HttpResponse(
                    json.dumps(payload),
                    mimetype='applicaiton/json', status=500)
        else:
            return django.http.HttpResponse(entry_id, status=404)

def homepage(request):
    
    return render_to_response('homepage.html',
                          {'css_url': '/static/css/general-site.css'},
                          context_instance=django.template.RequestContext(request))
