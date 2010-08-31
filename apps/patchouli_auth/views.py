import logging
import hashlib
import simplejson

from django.conf import settings
import django.http
from django.shortcuts import render_to_response
import django.utils.encoding

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

import lifestream.models
import patchouli_auth.models
import patchouli_auth.preferences

logging.basicConfig(filename=settings.LOG_FILENAME, level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', )
log = logging.getLogger()

#@login_required
def account_checkauth(request):
    if request.user.is_authenticated():
        manageUrl = "/manage/account/%s" % request.user.username.encode('utf-8')
        try:
            _ = lifestream.models.Stream.objects.all().filter(user=request.user)
            encoded_url = django.utils.encoding.iri_to_uri(manageUrl)
            resp = django.http.HttpResponseRedirect(encoded_url)
        except lifestream.models.Stream.DoesNotExist:
            log.debug("Account didn't exist")            
            stream = lifestream.models.Stream()
            stream.user_id = request.user.id
            stream.name = 'home'
            log.info("Saving %s %s" % (request.user.id, 'home'))
            stream.save()
            webpage = lifestream.models.Webpage(name=stream.name, user=request.user, config='{}')
            patchouli_auth.preferences.savePageOrStreamProperties(
                webpage, patchouli_auth.preferences.getPageProperties(webpage))            
            resp = django.http.HttpResponseRedirect('/auth/confirm_profile')
        except Exception, exception:
            log.exception("Unable to load user... trying to save %s", exception)
        encoded_username = django.utils.encoding.iri_to_uri(request.user.username)
        name = "%s %s" % (request.user.first_name, request.user.last_name)
        id = request.user.useropenid_set.all()[0].display_id
        resp['X-Account-Management-Status'] = "active; name=\"%s\"; id=\"%s\"" % (name, id)
        return resp
    else:        
        return django.http.HttpResponseRedirect('/openid/login')
    return resp

@login_required
def profile(request, username):
    """ Don't use username for anything... """    
    profileProps = patchouli_auth.preferences.getPreferences(request.user)
    if profileProps['publish_email']:
        publishEmailFlag = 'checked'
    else:
        publishEmailFlag = ''
    if 'langauge_code' in profileProps:
        lang_code = profileProps['language_code']
    else:
        lang_code = request.LANGUAGE_CODE
    
    gravatarHash = hashlib.md5(
        django.utils.encoding.smart_str(request.user.email)).hexdigest()
    avatar_url = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash

    return render_to_response('index.html',
                          { 'show_delete': True,
                            'css_url': '/static/css/general-site.min.css',
                            'username':   request.user.username,                            
                            'email':      request.user.email,
                            
                            'lang_dir': 'LTR',
                            'page_lang': 'en',
                          
                            'publish_email_flag': publishEmailFlag,
                            'first_name': request.user.first_name,
                            'last_name':  request.user.last_name,
                            'language_code': lang_code,
                            'gravatar': avatar_url,
                            },
                          context_instance=django.template.RequestContext(request))
    
def delete_profile(request, username):    
    """ Don't use username for anything... TODO: Add captcha since we can't force / trust an OpenID login step """
    if 'POST' == request.method:
        user = request.user
        logout(request)
        log.info("Deleting account for username %s" % (user.username))
        user.delete()
        return django.http.HttpResponseRedirect('/auth')
    else:
        return render_to_response('confirm_delete.html',
                          {
                            'css_url': '/static/css/general-site.min.css',
                            'lang_dir': 'LTR',
                            'page_lang': 'en',
                           },
                          context_instance=django.template.RequestContext(request))

@login_required
def confirm_profile(request):
    """ TODO use a FormModel """
    profileProps = patchouli_auth.preferences.getPreferences(request.user)
    
    error = None
    if 'POST' == request.method:
        params = request.POST.copy()
        params['username'] = params['username'].lower()
        request.user.username   = params['username']
        request.user.email      = params['email']
        request.user.first_name = params['first_name']
        request.user.last_name  = params['last_name']
        if 'publish_email' in params and params['publish_email']:            
            profileProps['publish_email'] = True
        else:            
            profileProps['publish_email'] = False
        patchouli_auth.preferences.savePreferences(request.user, profileProps)
        
        if request.user.username and request.user.email:            
            try:
                request.user.save()
                return django.http.HttpResponseRedirect('/auth')
            except:
                error = "%s unavailable, try another" % request.user.username
        else:
            error = 'Username and Email address are required'
    if profileProps['publish_email']:
        publishEmailFlag = 'checked'
    else:
        publishEmailFlag = ''
    
    gravatarHash = hashlib.md5(
        django.utils.encoding.smart_str(request.user.email)).hexdigest()
    avatar_url = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash

    return render_to_response('index.html',
                          { 'css_url': '/static/css/general-site.min.css',
                            'username':   request.user.username,                            
                            'email':      request.user.email,
                            
                            'lang_dir': 'LTR',
                            'page_lang': 'en',
                            
                            'publish_email_flag': publishEmailFlag,
                            'first_name': request.user.first_name,
                            'last_name':  request.user.last_name,
                            'gravatar': avatar_url,
                            'error':      error
                            },
                          context_instance=django.template.RequestContext(request))
def gravatar(request, email):
    gravatarHash = hashlib.md5(
        django.utils.encoding.smart_str(email)).hexdigest()
    return django.http.HttpResponse("http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash) 

import django.contrib.auth.views

# Messing with Account Manager
def logout(request):
    resp = django.contrib.auth.views.logout(request, '/openid/login')
    resp['X-Account-Management-Status'] = "none;"
    return resp

#====== Account Manager ==========
def session_status(request):
    if request.user.is_authenticated and request.user.is_active:        
        name = "%s %s" % (request.user.first_name, request.user.last_name)
        id = request.user.useropenid_set.all()[0].display_id
        amstatus = "active; name=\"%s\"; id=\"%s\"" % (name, id)
    else:
        amstatus = "none;"
    resp = django.http.HttpResponse("X-Account-Managment-Status will be %s" % amstatus)
    resp['X-Account-Management-Status'] = amstatus
    return resp
