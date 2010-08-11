import os
import site

import django.core.handlers.wsgi

# Add the parent dir to the python path so we can import manage
wsgidir = os.path.dirname(__file__)
site.addsitedir(os.path.abspath(os.path.join(wsgidir, '../../')))

# manage.py adds the `apps` and `lib` directories to the path
ROOT = os.path.abspath(os.path.join(wsgidir, '../'))
ROOT_PACKAGE = os.path.basename(ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % ROOT_PACKAGE

__import__('%s.manage' % ROOT_PACKAGE)

# for mod-wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# Uncomment this to figure out what's going on with the mod_wsgi environment.
#def application(env, start_response):
#    start_response('200 OK', [('Content-Type', 'text/plain')])
#    return '\n'.join('%r: %r' % item for item in sorted(env.items()))

# vim: ft=python
