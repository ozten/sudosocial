import logging
import hashlib
import simplejson

import django.http
from django.shortcuts import render_to_response
import django.utils.encoding

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

import lifestream.models
import patchouli_auth.models
import patchouli_auth.preferences

logging.basicConfig( level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', )
log = logging.getLogger()

#@login_required
def account_checkauth(request):
    if request.user.is_authenticated():
        manageUrl = "/manage/account/%s" % request.user.username
        try:
            stream = lifestream.models.Stream.objects.get(user__exact=request.user)
            log.debug("Same old same old %s" % stream.name)
            resp = django.http.HttpResponseRedirect(manageUrl)
        except:
            log.debug("New user encountered")
            stream = lifestream.models.Stream()
            stream.user_id = request.user.id
            stream.name = 'home'
            log.debug("Saving %s %s" % (request.user.id, 'home'))
            stream.save()
            resp = django.http.HttpResponseRedirect('/auth/confirm_profile')
        resp['X-Account-Manager-Status'] = "active; name=\"%s\"" % request.user.username
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
    
    gravatarHash = hashlib.md5(
        django.utils.encoding.smart_str(request.user.email)).hexdigest()
    avatar_url = "http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash

    return render_to_response('index.html',
                          { 'show_delete': True,
                            'css_url': '/static/css/general-site.css',
                            'username':   request.user.username,                            
                            'email':      request.user.email,
                            'publish_email_flag': publishEmailFlag,
                            'first_name': request.user.first_name,
                            'last_name':  request.user.last_name,
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
        log.debug("Redirect to auth")
        return django.http.HttpResponseRedirect('/auth')
    else:
        return render_to_response('confirm_delete.html',
                          {'css_url': '/static/css/general-site.css',},
                          context_instance=django.template.RequestContext(request))

@login_required
def confirm_profile(request):
    """ TODO use a FormModel """
    profileProps = patchouli_auth.preferences.getPreferences(request.user)
        
    error = None
    if 'POST' == request.method:
        params = request.POST.copy()
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
                          { 'css_url': '/static/css/general-site.css',
                            'username':   request.user.username,                            
                            'email':      request.user.email,
                            'publish_email_flag': publishEmailFlag,
                            'first_name': request.user.first_name,
                            'last_name':  request.user.last_name,
                            'gravatar': avatar_url,
                            'error':      error
                            },
                          context_instance=django.template.RequestContext(request))
def gravatar(request, email):
    log.debug("Creating gravatar for %s" % email)
    gravatarHash = hashlib.md5(
        django.utils.encoding.smart_str(email)).hexdigest()
    return django.http.HttpResponse("http://www.gravatar.com/avatar/%s.jpg?d=monsterid&s=80" % gravatarHash) 

import django.contrib.auth.views

# Messing with Account Manager
def logout(request):
    resp = django.contrib.auth.views.logout(request, '/openid/login')
    resp['X-Account-Management-Status'] ='none'
    return resp
