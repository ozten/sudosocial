""" 
    Run python manage.py dbsync 
    Then run this migration
    Create a config.py based off of config.py.dist in this directory... then run as
    python docs/database/migrations/0.5-split-entry.py
"""
import sys

import config
sys.path.append(config.path)

from django.core.management import setup_environ
import settings
setup_environ(settings)

import os 
import site

ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)
site.addsitedir(path('../../../apps'))

import logging
logging.basicConfig(level = config.log_level,
                    format = '%(asctime)s %(levelname)s %(process)d %(message)s', )
log = logging.getLogger()

log.info("Added %s" % path('../../../apps'))

from django.db import connection, transaction
cursor = connection.cursor()

log.info("So far so good so what")
log.info(sys.path)

from lifestream.models import Webpage, Stream

log.info("Adding webpage_id column")
cursor.execute("ALTER TABLE lifestream_stream ADD COLUMN webpage_id integer NOT NULL")
log.info("Adding foreign key constraint")
cursor.execute("ALTER TABLE `lifestream_stream` ADD CONSTRAINT `webpage_id_refs_id_6804d8c3` FOREIGN KEY (`webpage_id`) REFERENCES `lifestream_webpage` (`id`)")

transaction.commit_unless_managed()

for stream in Stream.objects.all():
    webpage = Webpage.objects.get(user__id = stream.user_id,
                                  name='home')
    stream.webpage_id = webpage.id
    stream.save()

#transaction.commit_unless_managed()
log.info("Done success")
