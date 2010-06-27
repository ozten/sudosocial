from django.core.management import setup_environ
import settings
setup_environ(settings)

import logging
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(process)d %(message)s', )
log = logging.getLogger()

from lifestream.models import Stream
from lifestream.models import Webpage
import lifestream.models

import patchouli_auth.preferences

streams = Stream.objects.all()
for stream in streams:
    log.info("Checking page exists for %s owned by %s" % (stream.name, stream.user.username))
    try:
        Webpage.objects.get(name=stream.name, user=stream.user)        
    except Webpage.DoesNotExist:
        webpage = Webpage(name=stream.name, user=stream.user, config='{}')
        patchouli_auth.preferences.savePageOrStreamProperties(
            webpage, patchouli_auth.preferences.getPageProperties(webpage))