# `sudo`Social #
**`sudo`Social** is a labs experiment around creating a stream
publishing platform. Lifestreams, Friendstreams, homepages,
and topichubs all rely on streams for data. 

Content aggregation has been around for a long time, but there isn't a popular
open source self-hosted web app for owning the content
and presentation of streams.

## Philosophy ##

Respect for privacy and privacy control preferences are critical features that
many users don't notice or care about currently. Privacy isn't an
easy choice, there are no set it and forget it preferences. We [builders]
can make many nuanced decisions.
**Example:** Don't display timestamps in streams by default. You're leaking
 information (oh they're writing yelp reviews at work?)
that isn't a primary concern. Authoring a lifestream that is displayed
on a timeline... then include timestamps as it's relevant data.

Cloud control - full access to the user. Self-hosted, Import, export, delete account.
The stream editor could show which entries are public, shared, and private.

Mozilla wants to broaden the community. One goal of this project is to be
approachable and hackable for many different types of people.

                    ____________________
                ____| CSS - Designer
           _____| Processing.js - Artist
       ____| JS - Web Developer
    __| Python - Web Developer
    
Another goal is to demonstrate a well behaved distributed
content publishing system. We want to republish
content, but to push the value back into the originating source.
**Example:** Display Flick photos in a really attractive way, send
users to Flick as soon as possible, since that app is optimized for
viewing and editing photos. Provide 'Like' and 'comment' features,
but send that data back to Flickr (OpenLike? and Salmon?). 
The data the platform provides should be in standard formats (ActivityStreams)
and be published with standards based markup (Microformats).

And of course, the overall Mozilla mission of keeping the web open
and accessible.

## License ##
This codebase is tri-licensed
  * [Mozilla Public License](http://www.mozilla.org/MPL/MPL-1.1.html), version 1.1 or later
  * [GNU General Public License](http://www.gnu.org/licenses/gpl-2.0.html), version 2.0 or later
  * [GNU Lesser General Public License](http://www.gnu.org/licenses/lgpl-2.1.html), version 2.1 or later
  
## CREDITS ##
Jeff Balogh
James Socol (Bleach)
Zach Hale
Ian Bicking (Silver Lining)

## Hacking ##
This code and data is very early days and subject to change.

If you run into trouble installing or hacking, this framework is Django plus enhancements from from [addons.mozilla.org](http://addons.mozilla.org) and [support.mozilla.org](http://support.mozilla.org), so you can refer to [the docs](http://jbalogh.github.com/zamboni/topics/installation/) from
the [zamboni](http://github.com/jbalogh/zamboni) project 
as well as [Django 1.1 docs](http://docs.djangoproject.com/en/1.1/).

### Requirements ###
You'll need easy_install, MySQL client and server, and Python 2.5 or greater.

For Ubuntu you could do 
sudo apt-get install python-setuptools libmysqlclient-dev libxml2-dev libxslt1-dev python-dev
sudo easy_install pip

1. Grab the source

        git clone git://github.com/ozten/sudosocial.git
        cd sudosocial

1. *Optional* setup a virtualenv for sudosocial (See link above for zamboni virtual env setup and pro tips)

        easy_install virtualenv
        virtualenv --no-site-packages ~/.sudosocial
        source ~/.sudosocial/bin/activate
   Your command line should now show something like:

        (.sudosocial)jrhacker@home:~/sudosocial$ 
2. 

        pip install -r requirements.txt
3. Any errors? 
4. create a database

        $ mysql -uroot -p 
        mysql> create database sudosocial_dev charset 'utf8';
        mysql> exit

5. Create Django settings file and then edit mysql username and password

        cp settings-dev.py settings.py
   
6. run 

        python manage.py syncdb
7. 

        python manage.py runserver 0.0.0.0:8000

8. Install cron job (or run manually once and a while)

  Assuming your using virtualenv

        ~/.sudosocial/bin/python ~/sudosocial/cron/feeder.py

  (more details on setting up a cron are furth down in this README)

9. Go to http://localhost:8000
    Click "create your own Homestream"



Step 847, there is no step 847. It's that easy.

## Updating after git pull ##

Things are still under development, so you have two choices after a git pull brings down model.py changes (and migration files)

1. Update the database
  Drop database and syncdb
  or
  From mysql prompt, execute the migrations under docs/database/migrations/

2. 

        pip install -r requirements.txt

3. Check for updates to the settings-dev.py file

        diff settings.py settings-dev.py
  
### Patchouli ###
What is "patchouli" in the code?
This **was** the working name of the project. This project is a small step towards **personal cloud control**. 
In meatspace, *Hippies use patchouli instead of showers and deodorant*. Respect... I'm a neo-hippie, I'm just say'n.

**`sudo`Social** is a *slightly* better name. [Patches welcome](http://groups.google.com/group/mozilla-labs-sudosocial/browse_thread/thread/2bb964af28c46755) :)

### Lifecycle ###
Feeds are fetch and entries are pickled and stored in the database.
When a stream is viewed, the appropriate entries are retrieved, and
a mapping is made from feed url to an importer. The importer
gets to prepare the feed via hooks.py and then render it via
entry.html

### Want to customize how a certain feed is handled? ###
1. Run bin/create_feed_type.sh <sitename>
2. Add a regex to lifestream/views.py in the websiteFeedType function
3. Edit lifestream/<sitename>/hooks.py
4. Edit templates/<sitename>/entry.html

*TODO*  Put these three items into the same directory.

### CRONs ###
#### Feed Fetcher ####

Assuming you had this code in /home/ozten/sudosocial and a virtualenv under /home/ozten/.virtualenvs/sudosocial, you would

1. cp /home/ozten/sudosocial/cron/config.py.dist /home/ozten/sudosocial/cron/config.py
2. Edit /home/ozten/sudosocial/cron/config.py (optional)
3. install the following cron:

        # m h dom mon dow   command
        */5 * *   *   *     /home/ozten/.virtualenvs/sudosocial/bin/python /home/username/sudosocial/cron/feeder.py > /home/username/sudosocial/cron/feeder.log


### Plugins ###
There is the begginings of a Plugin system. Poke around under the plugins directory. APIs are not frozen. ["I must break you"](http://www.youtube.com/watch?v=ygQvB6OjHOU)