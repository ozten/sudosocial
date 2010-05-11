import re

from bleach import Bleach
bleach = Bleach()

def prepareEntry(entryJSON, log):
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
   """
    title = entryJSON['title']
    parts = title.split(':')
    if (len(parts) > 1):
        tweet = ':'.join(parts[1:])
    else:
        tweet = title
    rawtags = [s.replace('#', '') for s in re.findall('#\w+', tweet)]
    tags = []
    for r in rawtags:
        tags.append({'tag': r, 'name': r})
    tweet = re.sub('#(\w+)', '<a href="http://twitter.com/search?q=%23\\1">#\\1</a>', tweet)
    tweet = re.sub('@(\w+)', '<a href="http://twitter.com/\\1">@\\1</a>', tweet)
    tweet = bleach.linkify(tweet.replace('\n', '<br />'))
    
    
    return {'tweeter': parts[0], 'tweet': tweet, 'permalink': entryJSON['link'], 'tags': tags}