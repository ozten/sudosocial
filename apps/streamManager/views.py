import logging
import datetime
import hashlib
import time

import feedparser
from pyquery import PyQuery
import simplejson as json

from django.conf import settings
import django.http
import django.template
import django.template.loaders
import django.utils.hashcompat as hashcompat
import django.utils.encoding

from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

import lifestream.models
from lifestream import lang
import patchouli_auth.preferences
from plugins.stream_editor import StreamEditorPlugin
from lifestream.views import render_entries
from lifestream.generic.hooks import tidy_up
from streamManager.stream_config import StreamConfig
from cron.feeder import update_feed

logging.basicConfig(filename=settings.LOG_FILENAME, level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', )
log = logging.getLogger()

HACKING_MESSAGE = 'Hack much? Your request has been logged. Authorities have been dispatched.'
        
@login_required
def manage_profile(request):
    return django.http.HttpResponse("TODO, let you edit your profile info")

@login_required
def manage(request, username):
    if request.user.username == username:
        pages = lifestream.models.Webpage.objects.filter(user=request.user).all()
        if len(pages) == 1:            
            return manage_page(request, username, pages[0].name)
        else:
            return manage_all_pages(request, username)
    else:
        return django.http.HttpResponse(HACKING_MESSAGE, status=400)
        
def entry_pair_for_entries(request, raw_entries, plugins):
    """ Helper method """    
    return zip(raw_entries, render_entries(request, raw_entries, plugins))

@login_required    
def manage_page(request, username, page_name):
    if request.user.username == username:
        log.info("Grabbing webpage")
        webpage = get_object_or_404(lifestream.models.Webpage, user=request.user, name=page_name)
        webpage_properties = patchouli_auth.preferences.getPageProperties(webpage)
        streams = []
        for stream_id in webpage_properties['stream_ids']:
            stream = get_object_or_404(lifestream.models.Stream, user=request.user, id=stream_id)
            streams.append(stream)
            stream_config = StreamConfig(stream.config)
            feed_rows = stream.feed_set.all()
            stream_config.ensureFeedsConfig(feed_rows)
            feed_id_to_feed = {}
            for row in feed_rows:
                feed_id_to_feed[row.pk] = row
            stream.feeds = []
            for feed in stream_config.config['feeds']:
                feed_row = feed_id_to_feed[feed['url_hash']]
                stream.feeds.append({'url': feed_row.url,
                              'title': feed_row.title,
                              'pk': feed_row.pk,
                              'enabled': feed_row.enabled,
                              'disabled_reason': feed_row.disabled_reason,
                              'entries_visible_default': feed['entries_visible_default']})
            plugins = [StreamEditorPlugin(log)]
            entries = lifestream.models.recent_entries(request.user, stream, 150, False)
            stream.entry_pair = entry_pair_for_entries(request, entries, plugins)
            for entry, entry_html in stream.entry_pair:
                log.info(entry.stream_entry)
            feed_model = lifestream.models.FeedForm()
                
            stream.url = "/u/%s/s/%s" % (username, stream.name)
        
        gravatarHash = hashlib.md5(
            django.utils.encoding.smart_str(request.user.email)).hexdigest()
        gravatar = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash
            
        preferences = patchouli_auth.preferences.getPreferences(request.user)
        
        if webpage_properties['css_type'] == 'css_raw':
            css_raw_default = webpage_properties['css_value']
        else:
            css_raw_default = ''
        if webpage_properties['css_type'] == 'css_url':
            css_url_default = webpage_properties['css_value']
        else:
            css_url_default = 'http://'
            
        if webpage_properties['js_type'] == 'js_raw':
            js_raw_default = webpage_properties['js_value']
        else:
            js_raw_default = ''
        if webpage_properties['js_type'] == 'js_url':
            js_url_default = webpage_properties['js_value']
        else:
            js_url_default = 'http://'
        
        template_data = { #'feeds': feeds,
                          'css_raw_default': css_raw_default,
                          'css_url_default': css_url_default,
                          'page_props_s': str(webpage_properties),

                          'unused_feeds': [],
                          'form': feed_model,
                          'gravatar': gravatar,
                          'js_raw_default': js_raw_default,
                          'js_url_default': js_url_default,
                          
                          # Common 
                          'lang_dir': 'LTR',
                          'page_lang': 'en',
                          
                          
                          'page_langs': lang.HTML_LANG,
                          'page_lang_desc': lang.HTML_LANG[webpage_properties['page_lang']],
                          'page_lang_dirs': lang.DIR_CHOICES,
                          'page_name': page_name,
                          'request': request,
                          'streams': streams,
                          'stream_id': stream.id,
                          'stream_config': stream_config,
                          'username': request.user.username,
                          'page_props': webpage_properties,
                          'preferences': preferences}
        if streams:
            template_data['first_stream'] = streams[0]
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
                                                               
                                'lang_dir': 'LTR',
                                'page_lang': 'en',
                          
                                'unused_feeds': [],
                                'request': request,
                                'streams': streams,
                                'page_name': streams[0] if streams else  '',
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
    log.info("Saving for stream with an id of")
    log.info(params['streams[]'])
    stream = get_object_or_404(lifestream.models.Stream, 
                               user=request.user,
                               id=params['streams[]'])
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
def reset_url(request, username, feed_url_hash):
    if request.user.username == username:
        feed = lifestream.models.Feed.objects.get(pk=feed_url_hash)
        if feed.enabled == False:
            feed.enabled = True
            feed.save()
        # Skip Caching
        feed.etag = ''
        feed.last_modified = datetime.datetime(1975, 1, 10)
        entries = update_feed(feed)
        feed = lifestream.models.Feed.objects.get(pk=feed_url_hash)
        payload = {"message":"OK",
                   "number_new_entries": entries,
                   "enabled": feed.enabled,
                   "disabled_reason": feed.disabled_reason}
        return django.http.HttpResponse(json.dumps(payload), mimetype='applicaiton/json')
        
    else:
        return django.http.HttpResponse('{"message":"' + HACKING_MESSAGE + '"}', mimetype='applicaiton/json', status=400)

@login_required
def manage_page_design(request):
    if 'POST' == request.method:
        params = request.POST.copy()
        webpage = get_object_or_404(lifestream.models.Webpage, name=params['page_name'], user=request.user)
        props = patchouli_auth.preferences.getPageProperties(webpage)

        props['css_type'] = params['css_type']
        props['css_value'] = ''
        if 'css_url' == params['css_type']:
            props['css_value'] = params['css_url']
        elif 'css_raw' == params['css_type']:
            props['css_value'] = params['css_raw']
        
        props['js_type'] = params['js_type']
        props['js_value'] = ''
        if 'js_url' == params['js_type']:
            props['js_value'] = params['js_url']
        elif 'js_raw' == params['js_type']:
            props['js_value'] = params['js_raw']
        
        props['processing_js'] = params['processing']
        patchouli_auth.preferences.savePageOrStreamProperties(webpage, props)
        return django.http.HttpResponseRedirect("/auth") #TODO django.core.urlresolvers reverse('confirm_profile')
        
@login_required
def manage_page_widgets(request, page_name):    
    if 'POST' == request.method:
        params = request.POST.copy()
        # KISS stream and page have the same name
        page = get_object_or_404(lifestream.models.Webpage, name=page_name, user=request.user)        
        preferences = patchouli_auth.preferences.getPageProperties(page)
        
        preferences['before_profile_html_area'] = tidy_up(params['before_profile_html_area'], log)        
        preferences['after_profile_html_area'] = tidy_up(params['after_profile_html_area'], log)
        preferences['before_stream_html_area'] = tidy_up(params['before_stream_html_area'], log)
        preferences['after_stream_html_area'] = tidy_up(params['after_stream_html_area'], log)
        
        preferences['page_lang'] = params['page_lang']
        if preferences['page_lang'] not in lang.HTML_LANG.keys():
            preferences['page_lang'] = 'en'
        preferences['page_lang_dir'] = params['page_lang_dir']
        if preferences['page_lang_dir'] not in lang.DIR_CHOICES.keys():
            preferences['page_lang_dir'] = 'LTR'
        
        # Checkboxes
        if 'show_profile_blurb' in params:
            preferences['show_profile_blurb'] = True
        else:
            preferences['show_profile_blurb'] = False
        if 'show_follow_me_links' in params:
            preferences['show_follow_me_links'] = True
        else:
            preferences['show_follow_me_links'] = False
        
        
        patchouli_auth.preferences.savePageOrStreamProperties(page, preferences)
        manageUrl = "/manage/account/%s" % request.user.username.encode('utf-8')
        return django.http.HttpResponseRedirect(manageUrl)
        
def entry(request, stream_id, entry_id):
    """
        change-visibility set to true - show entry
        change-visibility set to false - hide entry
    """
    if 'POST' == request.method:
        entry = get_object_or_404(lifestream.models.Entry, id=entry_id,feed__user=request.user) # proves ownership of entry_id
        streamentry = get_object_or_404(lifestream.models.StreamEntry, stream__id=stream_id, entry__id=entry_id)
        if entry:
            if 'change-visibility' in request.POST and request.POST['change-visibility'] == 'true':
                streamentry.visible = True
            elif 'change-visibility' in request.POST and request.POST['change-visibility'] == 'false':
                streamentry.visible = False
            else:
                return django.http.HttpResponse(
                    '{"status":"ERROR", "error-message":"Change not understood"}',
                    mimetype='applicaiton/json', status=400)
            try:
                streamentry.save()
                fresh_streamentry = get_object_or_404(lifestream.models.StreamEntry, stream__id=stream_id, entry__id=entry_id)
                payload = {'status': 'OK', 'guid': entry.guid,
                           'id': entry.id,
                           'visible': fresh_streamentry.visible}
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
            
def edit_feed(request, username, stream_id, feed_id):
    if 'POST' == request.method:
        return edit_feed_update(request, username, stream_id, feed_id)
    else:
        return edit_feed_show(request, username, stream_id, feed_id)

def edit_feed_update(request, username, stream_id, feed_id):    
    feed = get_object_or_404(lifestream.models.Feed, url_hash=feed_id)
    stream = get_object_or_404(lifestream.models.Stream, id=stream_id)
    stream_config = StreamConfig(stream.config)        
    stream_config.ensureFeedsConfig(stream.feed_set.all())
    
    feed_config = feed_config_from_stream(stream_config, feed_id)
    
    # TODO hmmm this code sucks because I'm writing directly to the confic Dict
    # instead of an Abstract Data Type... fixme
    
    params = request.POST.copy()
    # TODO use per-stream feed title in editor and lifestream views
    if 'title' in params:
        feed_config['feed_title'] = params['title']
        
    if 'entries_visible_default' in params:
        if 'True' == params['entries_visible_default']:
            feed_config['entries_visible_default'] = True
        else:
            feed_config['entries_visible_default'] = False
    if 'enable_num_entries_shown' in params and 'True' == params['enable_num_entries_shown']:
        feed_config['enable_num_entries_shown'] = True
        try:
            num_entries = int(params['num_entries_shown'])
            if num_entries > 50:
                num_entries = 50
            if num_entries < 0: #WTF?
                num_entries = 5
            feed_config['num_entries_shown'] = num_entries
        except ValueError:
            log.info("Unable to parse int out of %s" % params['num_entries_shown'])
            feed_config['num_entries_shown'] = 5
    else:
        feed_config['enable_num_entries_shown'] = False
        
    stream_config.update_feed_config(feed_config)    
    stream.config = stream_config.__unicode__()
    stream.save()
    return django.http.HttpResponseRedirect("/manage/account/%s/stream/%s/feed/%s" % (username, stream_id, feed_id))
    
def feed_config_from_stream(stream_config, feed_id):
    feed_config = {}
    for config in stream_config.config['feeds']:
        if config['url_hash'] == feed_id:
            feed_config = config
    return feed_config

def edit_feed_show(request, username, stream_id, feed_id):
    feed = get_object_or_404(lifestream.models.Feed, url_hash=feed_id)
    stream = get_object_or_404(lifestream.models.Stream, id=stream_id)
    feed_config = feed_config_from_stream(StreamConfig(stream.config), feed_id)    
        
    return render_to_response('feed_editor.html',
                              { 'feed': feed,
                                'feed_id': feed_id,
                                'stream': stream,
                                'stream_id': stream_id,
                                'feed_config': feed_config,
                                'lang_dir': 'LTR',
                                'page_lang': 'en',
                          
                                #'unused_feeds': [],
                                'request': request,
                                #'streams': streams,
                                'feed_id': feed_id,
                                'username': request.user.username,},
                              context_instance=django.template.RequestContext(request))
    
def preview_feed(request, username, stream_id, feed_id):
    feed = get_object_or_404(lifestream.models.Feed, url_hash=feed_id)
    stream = get_object_or_404(lifestream.models.Stream, id=stream_id)
    user = get_object_or_404(django.contrib.auth.models.User, username=username)
    stream_config = StreamConfig(stream.config)
    entries = lifestream.models.recent_feed_entries(user, stream, feed_id, 150, False)
    plugins = [StreamEditorPlugin(log)]
    stream.entry_pair = entry_pair_for_entries(request, entries, plugins)
                                        
    
    return render_to_response('feed_editor_preview.html',
                              { #'entry_pair': entry_pair,
                                'stream': stream,
                                'stream_id': stream.id,
                              },
                              context_instance=django.template.RequestContext(request))
@login_required
def streams(request, username, page_name):
    if request.user.username == username:
        if 'POST' == request.method:
            webpage = get_object_or_404(lifestream.models.Webpage, user=request.user, name=page_name)
            webpage_props = patchouli_auth.preferences.getPageProperties(webpage)
            new_stream_name = "Untitled %d" % int(time.mktime(datetime.datetime.now().timetuple()) * 1000)
            new_stream = lifestream.models.Stream(user=request.user, name=new_stream_name, webpage=webpage)
            new_stream.save()

            webpage_props['stream_ids'].append(new_stream.id)
            patchouli_auth.preferences.savePageOrStreamProperties(webpage, webpage_props)
            payload = {'status': 'OK', 'new_stream_id': new_stream.id}
            #TODO type in all these content-types.... WTF?
            return django.http.HttpResponse(json.dumps(payload), mimetype='applicaiton/json')

        else:
            return django.http.HttpResponse('Hey')
    else:
        return django.http.HttpResponse('{"message":"' + HACKING_MESSAGE + '"}', mimetype='applicaiton/json', status=400)

@login_required
def stream(request, username, stream_id):
    if request.user.username == username:
        if 'DELETE' == request.method:
            stream = get_object_or_404(lifestream.models.Stream, user=request.user, id=stream_id)
            payload = {'status': 'ERROR', 'msg': 'Unabled to remove stream'}
            log.info("Removing stream %d %s" % (stream.id, stream.name))
            if patchouli_auth.preferences.removeStreamFromPage(stream.webpage, stream):
                payload = {'status': 'OK', 'msg': 'Stream removed'}
            return django.http.HttpResponse(json.dumps(payload), mimetype='applicaiton/json')            
        else:
            return django.http.HttpResponse('Hey')
    else:
        return django.http.HttpResponse('{"message":"' + HACKING_MESSAGE + '"}', mimetype='applicaiton/json', status=400)

# ----------------- Sitewide Functions --------------#
def homepage(request):
    return render_to_response('homepage.html',
                          {'css_url': '/static/css/general-site.min.css',
                           'lang_dir': 'LTR',
                           'page_lang': 'en',},
                          context_instance=django.template.RequestContext(request))

def page_not_found(request):
    response = render_to_response('404.html',
                          {'css_url': '/static/css/general-site.min.css'},
                          context_instance=django.template.RequestContext(request))
    response.status_code = 404
    return response
    
def server_error(request):
    response = render_to_response('500.html',
                          {'css_url': '/static/css/general-site.min.css'},
                          context_instance=django.template.RequestContext(request))
    response.status_code = 500
    return response
