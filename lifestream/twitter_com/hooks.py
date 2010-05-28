import re

from bleach import Bleach
bleach = Bleach()

def prepare_entry(entryJSON, log):
    """ Given entryJSON, output a dictionary of variables for use in
    templates/twitter_com/entry.html
    
    Here is the layout of a typical Twitter Entry looks like:
   {
   'summary_detail':{
      'base':'http://twitter.com/statuses/user_timeline/1127361.rss',
      'type':'text/html',
      'language':None,
      'value':"ozten: @mriggen I can only imagine... I'm getting sentimental about it and the future!"
   },
   'updated_parsed':[ 2010, 3, 18, 3, 35, 24, 3, 77, 0],
   'links':[
      { 'href':'http://twitter.com/ozten/statuses/10653573637',
         'type':'text/html',
         'rel':'alternate'}],
   'title':"ozten: @mriggen I can only imagine... I'm getting sentimental about it and the future!",
   'updated':'Thu, 18 Mar 2010 03:35:24 +0000',
   'summary':"ozten: @mriggen I can only imagine... I'm getting sentimental about it and the future!",
   'guidislink':True,
   'title_detail':{
      'base':'http://twitter.com/statuses/user_timeline/1127361.rss',
      'type':'text/plain',
      'language':None,
      'value':"ozten: @mriggen I can only imagine... I'm getting sentimental about it and the future!"
   },
   'link':'http://twitter.com/ozten/statuses/10653573637',
   'id':'http://twitter.com/ozten/statuses/10653573637'
   }
   #TODO if someone else is tweeting to me, don't remove the username
   
   Search is different
    {u'lang': u'fr', u'updated': u'2010-05-15T10:44:59Z',
    u'subtitle': u'<a href="http://search.twitter.com/search?q=%23Mozilla">#Mozilla</a> lance <a href="http://search.twitter.com/search?q=%23PluginCheck">#<b>PluginCheck</b></a>, un v\xe9rificateur de <a href="http://search.twitter.com/search?q=%23plugins">#plugins</a> multi-navigateurs | Jean-Marie Gall.com <a href="http://bit.ly/9Zmv8c">http://bit.ly/9Zmv8c</a>',
    u'published_parsed': [2010, 5, 15, 10, 44, 59, 5, 135, 0],
    u'links': [{u'href': u'http://twitter.com/jmgall/statuses/14030858884', u'type': u'text/html', u'rel': u'alternate'},
               {u'href': u'http://a3.twimg.com/profile_images/284467989/jmbg54000_normal.jpg', u'type': u'image/png', u'rel': u'image'}],
    u'title': u'#Mozilla lance #PluginCheck, un v\xe9rificateur de #plugins multi-navigateurs | Jean-Marie Gall.com http://bit.ly/9Zmv8c',
    u'author': u'jmgall (Jean-Marie Gall)',
    u'id': u'tag:search.twitter.com,2005:14030858884',
    u'content': [{u'base': u'http://search.twitter.com/search.atom?q=plugincheck', u'type': u'text/html', u'language': u'en-US',
                 u'value': u'<a href="http://search.twitter.com/search?q=%23Mozilla">#Mozilla</a> lance <a href="http://search.twitter.com/search?q=%23PluginCheck">#<b>PluginCheck</b></a>, un v\xe9rificateur de <a href="http://search.twitter.com/search?q=%23plugins">#plugins</a> multi-navigateurs | Jean-Marie Gall.com <a href="http://bit.ly/9Zmv8c">http://bit.ly/9Zmv8c</a>'}],
    u'source': {},
    u'title_detail': {u'base': u'http://search.twitter.com/search.atom?q=plugincheck', u'type': u'text/plain', u'language': u'en-US', u'value': u'#Mozilla lance #PluginCheck, un v\xe9rificateur de #plugins multi-navigateurs | Jean-Marie Gall.com http://bit.ly/9Zmv8c'},
    u'href': u'http://twitter.com/jmgall',
    u'link': u'http://twitter.com/jmgall/statuses/14030858884',
    u'published': u'2010-05-15T10:44:59Z',
    u'author_detail': {u'href': u'http://twitter.com/jmgall',
                u'name': u'jmgall (Jean-Marie Gall)'},
    u'geo': u'', u'result_type': u'recent',
    u'updated_parsed': [2010, 5, 15, 10, 44, 59, 5, 135, 0], u'metadata': u''}

   """
    title = entryJSON['title']
    tweet = title
    tweeter = ''
    if re.match(r'^\w+:.*$', title):
        parts = title.split(':')
        if parts:
            tweeter = parts[0]
            tweet = ':'.join(parts[1:])            
    elif 'author' in entryJSON and 'name' in entryJSON.author:
        tweeter = entryJSON.author.name
    

    rawtags = re.findall('#(\w+)', tweet)
    tags = [{'tag': r, 'name': r} for r in rawtags]
    
    tweet = re.sub('#(\w+)', r'<a href="http://twitter.com/search?q=%23\1">#\1</a>', tweet)
    tweet = re.sub('@(\w+)', r'<a href="http://twitter.com/\1">@\1</a>', tweet)
    try:        
        tweet = bleach.linkify(tweet.replace('\n', '<br />'))
    except Exception, x:
        log.error("Ouch, unable to linkify _%s_ caught" % tweet)
        log.exception(x)
    
    
    return {'tweeter': tweeter, 'tweet': tweet, 'permalink': entryJSON['link'], 'tags': tags, 'raw': entryJSON}