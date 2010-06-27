# CRON Bootstrap
import sys
sys.path.append('/home/aking/patchouli')
from django.core.management import setup_environ
import settings
setup_environ(settings)

from lifestream.models import User
from lifestream.models import Feed
from lifestream.models import Entry
print "number_users:%d number_feeds:%d number_entries:%d" % (User.objects.count(),
                                                             Feed.objects.count(),
                                                             Entry.objects.count())