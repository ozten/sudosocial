import logging
import datetime

import feedparser
from pyquery import PyQuery
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
                          'enabled': feed_row.enabled,
                          'disabled_reason': feed_row.disabled_reason,
                          'entries_visible_default': feed['entries_visible_default']})
        
        raw_entries = (lifestream.models.Entry.objects.order_by('-last_published_date')
                      .filter(feed__user=request.user,
                              feed__streams__name__exact = streamname))[:150]
        plugins = [StreamEditorPlugin(log)]
        entry_pair = zip(raw_entries, render_entries(request, raw_entries, plugins))        
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
        [template_data.update(plugin.template_variables()) for plugin in plugins]
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
        
def is_possible_feed(url):
    """ Attempts to read url as a valid RSS or Atom feed.
        returns a Dict with metadata or
                False if url is not a feed """
    possible_feed = feedparser.parse(url)
    if 1 == possible_feed.bozo and len(possible_feed.entries) == 0:
        log.info("%s triggered feedparser's bozo detection" % url)
        return False
    else:
        log.info("%s is a valid feed according to feedparser" % url)
        # The url is a feed
        feed_title = 'Unknown'
        if 'feed' in possible_feed and 'title' in possible_feed['feed']:
            feed_title = possible_feed['feed']['title']
        return {'feed_url': url, 'feed_title': feed_title}
        
def make_possible_feed(link_element):
    """ Visits each <link rel="alternate" href="http://..." /> element """
    link = PyQuery(link_element)
    title = 'Unknown'
    if link.attr('title'):
        title = link.attr('title')
    if link.attr('href'):        
        return {'feed_url': link.attr('href'), 'feed_title': title}
    else:
        log.info("Skipping malformed link element for feed, missing href")
        return False

def append_if_dict(a_list, maybe_dict):
    """ Shim to avoid global variables in PyQuery callback """
    if maybe_dict:
        a_list.append(maybe_dict)

def save_feeds(request, username):
    new_feeds_to_save = []
    params = request.POST.copy()
    stream = get_object_or_404(lifestream.models.Stream, user=request.user,
                                                      name=params['streams[]'])
    feed_url = request.POST['url']
    possible_feed = is_possible_feed(feed_url)
    if possible_feed:
        new_feeds_to_save.append(possible_feed)
    else:
        pq = PyQuery(feed_url)
        pq('link[rel=alternate]').each(
            lambda link_el: append_if_dict(new_feeds_to_save,
                                           make_possible_feed(link_el)))
    new_feeds = []
    forms = []
    something_saved = False
    for new_feed_to_save in new_feeds_to_save:
        # This might have been 1 URL posted that turned into multiple embeded Feed links
        params['url'] = new_feed_to_save['feed_url']
        feed_url_hash = hashcompat.md5_constructor(
            django.utils.encoding.smart_str(new_feed_to_save['feed_url'])).hexdigest()        
        a_feed = lifestream.models.Feed(url_hash = feed_url_hash, title=new_feed_to_save['feed_title'],
                                        url = new_feed_to_save['feed_url'],
                                        etag='', last_modified=datetime.datetime(1975, 1, 10),
                                        enabled=True, disabled_reason='',
                                        user=request.user, created_date=datetime.datetime.today())        
        a_feed.streams.add(stream)
        form = lifestream.models.FeedForm(params, instance=a_feed)
        forms.append(form)
        if form.is_valid():
            form.save()            
            db_feed = lifestream.models.Feed.objects.get(pk=feed_url_hash)
            new_feeds.append(db_feed.to_primitives())
            something_saved = True
        else:
            log.info("Error, couldn't save %s" % feed_url_hash)
            pass # Keep trying other feeds
    if something_saved:
        stream_config = StreamConfig(stream.config)
        stream_config.ensureFeedsConfig(stream.feed_set.all())
        stream.config = stream_config.__unicode__()
        stream.save()
        return (True, new_feeds, forms)
    else:
        return (False, [], forms)

@login_required
def urls(request, username):
    if request.user.username == username:
        if 'POST' == request.method:
            # url_hash is 'exclude' aka editable=False, so we have to create a model
            # and set the url_hash, in order to get the data into the db
            status, new_feeds, forms = save_feeds(request, username)
            if status:                
                return django.http.HttpResponse(json.dumps({"message":"OK", "feeds": new_feeds}), mimetype='application/json')
            else:
                errors = ''
                for form in forms:
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
        return django.http.HttpResponseRedirect('/auth') #TODO django.core.urlresolvers reverse('confirm_profile')
        
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
# ----------------- Sitewide Functions --------------#
def homepage(request):
    return render_to_response('homepage.html',
                          {'css_url': '/static/css/general-site.css', },
                          context_instance=django.template.RequestContext(request))

def page_not_found(request):
    response = render_to_response('404.html',
                          {'css_url': '/static/css/general-site.css'},
                          context_instance=django.template.RequestContext(request))
    response.status_code = 404
    return response
    
def server_error(request):
    response = render_to_response('500.html',
                          {'css_url': '/static/css/general-site.css'},
                          context_instance=django.template.RequestContext(request))
    response.status_code = 500
    return response