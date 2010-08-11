def prepare_entry(entryJSON, log):
    """
    {
   'license':'http://creativecommons.org/licenses/by-sa/2.0/deed.en',
   'summary_detail':{
      'base':'http://api.flickr.com/services/feeds/photos_public.gne?id=30663385@N00&lang=en-us&format=rss_200',
      'type':'text/html',
      'language':None,
      'value':'<p><a href="http://www.flickr.com/people/ozten/">oztenphoto</a> posted a photo:</p>\n<p><a href="http://www.flickr.com/photos/ozten/4440801175/" title="Sketchnoters 5"><img src="http://farm3.static.flickr.com/2773/4440801175_8974b978c2_m.jpg" width="240" height="135" alt="Sketchnoters 5" /></a></p>'
   },
   'dc_date.taken':'2010-03-16T11:45:28-08:00',
   'updated_parsed':[2010,3,17,19,31,30,2,76,0],
   'links':[
      {'href':'http://www.flickr.com/photos/ozten/4440801175/',
         'type':'text/html',
         'rel':'alternate'}
   ],
   'title':'Sketchnoters 5',
   'author':'nobody@flickr.com (oztenphoto)',
   'updated':'Wed, 17 Mar 2010 12:31:30 -0700',
   'summary':'<p><a href="http://www.flickr.com/people/ozten/">oztenphoto</a> posted a photo:</p>\n<p><a href="http://www.flickr.com/photos/ozten/4440801175/" title="Sketchnoters 5"><img src="http://farm3.static.flickr.com/2773/4440801175_8974b978c2_m.jpg" width="240" height="135" alt="Sketchnoters 5" /></a></p>',
   'content':[
      {
         'base':'http://api.flickr.com/services/feeds/photos_public.gne?id=30663385@N00&lang=en-us&format=rss_200',
         'type':'image/jpeg',
         'language':None,
         'value':''
      }
   ],
   'credit':'oztenphoto',
   'title_detail':{
      'base':'http://api.flickr.com/services/feeds/photos_public.gne?id=30663385@N00&lang=en-us&format=rss_200',
      'type':'text/plain',
      'language':None,
      'value':'Sketchnoters 5'
   },
   'link':'http://www.flickr.com/photos/ozten/4440801175/',
   'id':'tag:flickr.com,2004:/photo/4440801175',
   'author_detail':{
      'name':'oztenphoto',
      'email':'nobody@flickr.com'
   },
   'thumbnail':'',
   'guidislink':False
}
    """
    
    content = None
    if 'summary' in entryJSON:
        content = entryJSON['summary']
    elif 'content' in entryJSON and 'value' in entryJSON.content[0]:
        content = entryJSON['content'][0].value
    else:
        log.warn("No Flickr Summary")
        log.warn(entryJSON)
    if content:
        if content.find('</a> posted a photo:</p>') > 0:
            #<p><a href="http://www.flickr.com/people/ozten/">oztenphoto</a> posted a photo:</p>\n<p><a href="http://www.flickr.com/photos/ozten/4440801175/" title="Sketchnoters 5"><img src="http://farm3.static.flickr.com/2773/4440801175_8974b978c2_m.jpg" width="240" height="135" alt="Sketchnoters 5" /></a></p>
            parts = content.split('<p>')
            content = '<p>' + parts[2]
    tags = []
    if 'tags' in entryJSON:
        for tag_spaced in entryJSON['tags']:
            for tag in tag_spaced['term'].split():
                #tags.append({'tag': tag['term'], 'url': tag['scheme'] + tag['term']})
                tags.append({'tag': tag, 'url': tag_spaced['scheme'] + tag})
    return {'title': entryJSON['title'], 'content': content, 'tags': tags, 'raw': entryJSON, 'permalink': entryJSON.link}