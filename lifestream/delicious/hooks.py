def prepare_entry(entryJSON, log):
    """
{
   'summary_detail':{
      'base':'http://feeds.delicious.com/v2/rss/ozten?count=15',
      'type':'text/html',
      'language':None,
      'value':'Activity theory is aimed at understanding the mental capabilities of a single human being. However, it rejects the isolated human being as an adequate unit of analysis, focusing instead on cultural and technical mediation of human activity. Activity theory is most often used to describe activity in a socio-technical system as a set of six interdependent elements (Bryant et al.) which constitute a general conceptual system that can be used as a foundation for more specific theories:'
   },
   'updated_parsed':[2010,3,17,19,31,30,2,76,0],
   'links':[
      {
         'href':'http://en.wikipedia.org/wiki/Scandinavian_activity_theory',
         'type':'text/html',
         'rel':'alternate'
      }
   ],
   'author':'ozten',
   'title':'Scandinavian activity theory - Wikipedia, the free encyclopedia',
   'updated':'Wed, 17 Mar 2010 04:10:12 +0000',
   'comments':'http://delicious.com/url/7793611890adeec7cdfd558079c92a82',
   'summary':'Activity theory is aimed at understanding the mental capabilities of a single human being. However, it rejects the isolated human being as an adequate unit of analysis, focusing instead on cultural and technical mediation of human activity. Activity theory is most often used to describe activity in a socio-technical system as a set of six interdependent elements (Bryant et al.) which constitute a general conceptual system that can be used as a foundation for more specific theories:',
   'guidislink':False,
   'title_detail':{
      'base':'http://feeds.delicious.com/v2/rss/ozten?count=15',
      'type':'text/plain',
      'language':None,
      'value':'Scandinavian activity theory - Wikipedia, the free encyclopedia'
   },
   'link':'http://en.wikipedia.org/wiki/Scandinavian_activity_theory',
   'source':{

   },
   'wfw_commentrss':'http://feeds.delicious.com/v2/rss/url/7793611890adeec7cdfd558079c92a82',
   'id':'http://delicious.com/url/7793611890adeec7cdfd558079c92a82#ozten',
   'tags':[
      {
         'term':'lifestream',
         'scheme':'http://delicious.com/ozten/',
         'label':None
      },
      {
         'term':'activitytheory',
         'scheme':'http://delicious.com/ozten/',
         'label':None
      }
   ]
}

Note: Two flavors ... sometimes summary is blank and title has 'base'
    """
    tags = []
    showDescription = False
    if 'tags' in entryJSON:
        for tag in entryJSON['tags']:
           tags.append({'tag': tag['term'], 'url': tag['scheme'] + tag['term']})
    
    if 'summary' in entryJSON and len(entryJSON['summary']) > 0:
        showDescription = True
        desc = entryJSON['summary']
    else:
        desc = ''
        
    #return {'entry': content}
    return {'title': entryJSON['title'], 'link': entryJSON['link'],
            'description': desc, 'showDescription': showDescription,
            'tags': tags,
            'permalink': entryJSON.id,
            'raw': entryJSON}