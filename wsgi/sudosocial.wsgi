import os
import site

os.environ['DJANGO_SETTINGS_MODULE'] = 'patchouli.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# Uncomment this to figure out what's going on with the mod_wsgi environment.
#def application(env, start_response):
#    start_response('200 OK', [('Content-Type', 'text/plain')])
#    return '\n'.join('%r: %r' % item for item in sorted(env.items()))

# vim: ft=python
