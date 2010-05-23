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

## Hacking ##
You can use the [VirtualBox applicance](http://sudosocial.me/static/sudosocial.zip) and your good to go.

This code and data is very early days and subject to change.

If you want to setup from scratch, this is a Django app and borrows from
[addons.mozilla.org](http://addons.mozilla.org) and [support.mozilla.org](http://support.mozilla.org).  
Please follow [the docs](http://jbalogh.github.com/zamboni/topics/installation/) from
the [zamboni](http://github.com/jbalogh/zamboni) project 
as well as [Django 1.1 docs](http://docs.djangoproject.com/en/1.1/).

### Requirements ###
Again, you can find these in the VM, but:

 * Python 2.5
 * Mysql
 * See requirements.txt for Python requirements.

### Patchouli ###
Currently this repository should be named patchouli and not **`sudo`Social**.

What is "patchouli" in the code?
This **was** the working name of the project. This project is a small step towards **personal cloud control**. 
In meatspace, *Hippies use patchouli instead of showers and deodorant*. Respect... I'm a neo-hippie, I'm just say'n.

**`sudo`Social** is a *slightly* better name. Patches welcome :)

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

    # m h dom mon dow   command
    */5 * *   *   *     /home/ozten/.virtualenvs/patchouli/bin/python /home/ozten/patchouli/cron/feeder.py > /home/ozten/patchouli/cron/feeder.log