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

import logging
logging.basicConfig(level = config.log_level,
                    format = '%(asctime)s %(levelname)s %(process)d %(message)s', )
log = logging.getLogger()

from django.db import connection, transaction
cursor = connection.cursor()

log.info("Adding unique constraint")
cursor.execute("ALTER TABLE lifestream_streamentry ADD UNIQUE (entry_id, stream_id)")

log.info('Populating lifestream_streamentry')
cursor.execute("""
INSERT INTO lifestream_streamentry (entry_id, stream_id, visible) 
    SELECT lifestream_entry.id, lifestream_feed_streams.stream_id, lifestream_entry.visible
    FROM lifestream_entry 
    JOIN lifestream_feed ON lifestream_feed.url_hash = lifestream_entry.feed_id
    JOIN lifestream_feed_streams ON lifestream_feed_streams.feed_id = lifestream_feed.url_hash""")
log.info("Inserted %d rows" % cursor.rowcount)
transaction.commit_unless_managed()

log.info('Dropping visible column from  lifestream_entry')
cursor.execute("ALTER TABLE lifestream_entry DROP COLUMN visible")
transaction.commit_unless_managed()

log.info("Done success")
