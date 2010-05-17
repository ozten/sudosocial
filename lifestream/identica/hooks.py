import re

from bleach import Bleach
bleach = Bleach()

def prepare_entry(entryJSON, log):
    """ Given entryJSON, output a dictionary of variables for use in
    templates/identica/entry.html
    {u'updated': u'2010-05-15T06:09:36+00:00',
    u'subtitle': u"Bookclub just got weird. Looks like I'm reading World War Z next, but the &quot;discussion&quot; will be in a karaoke booth.",
    u'published_parsed': [2010, 5, 15, 6, 9, 36, 5, 135, 0],
    u'links': [{u'href': u'http://identi.ca/notice/32272261', u'type': u'text/html', u'rel': u'alternate'},
    {u'href': u'http://identi.ca/conversation/32149749', u'type': u'text/html', u'rel': u'ostatus:conversation'}],
    u'title': u'Bookclub just got weird. Looks like I\'m reading World War Z next, but the "discussion" will be in a karaoke booth.',
    u'content': [{u'base': u'http://identi.ca/api/statuses/user_timeline/69091.atom', u'type': u'text/html', u'language': u'en-US',
    u'value': u"Bookclub just got weird. Looks like I'm reading World War Z next, but the &quot;discussion&quot; will be in a karaoke booth."}],
    u'title_detail': {u'base': u'http://identi.ca/api/statuses/user_timeline/69091.atom', u'type': u'text/plain', u'language': u'en-US',
    u'value': u'Bookclub just got weird. Looks like I\'m reading World War Z next, but the "discussion" will be in a karaoke booth.'},
    u'link': u'http://identi.ca/notice/32272261', u'published': u'2010-05-15T06:09:36+00:00', u'id':
    u'http://identi.ca/notice/32272261', u'updated_parsed': [2010, 5, 15, 6, 9, 36, 5, 135, 0]}
    
    A conversation:
    {u'updated': u'2010-05-15T15:37:40+00:00',
    u'subtitle': u'@<span class="vcard"><a href="http://identi.ca/user/59637" class="url" title="Stefan Pampel"><span class="fn nickname">pisco</span></a></span> True Dat!',
    u'published_parsed': [2010, 5, 15, 15, 37, 40, 5, 135, 0],
    u'links': [{u'href': u'http://identi.ca/notice/32316840', u'type': u'text/html', u'rel': u'alternate'},
               {u'href': u'http://identi.ca/notice/32304325', u'type': u'text/html', u'rel': u'related'},
               {u'href': u'http://identi.ca/conversation/32175701', u'type': u'text/html', u'rel': u'ostatus:conversation'},
               {u'href': u'http://identi.ca/user/59637', u'type': u'text/html', u'rel': u'ostatus:attention'}],
    u'title': u'@pisco True Dat!', u'published': u'2010-05-15T15:37:40+00:00',
    u'content': [{u'base': u'http://identi.ca/api/statuses/user_timeline/69091.atom', u'type': u'text/html', u'language': u'en-US',
                u'value': u'@<span class="vcard"><a href="http://identi.ca/user/59637" class="url" title="Stefan Pampel"><span class="fn nickname">pisco</span></a></span> True Dat!'}], u'title_detail': {u'base': u'http://identi.ca/api/statuses/user_timeline/69091.atom', u'type': u'text/plain', u'language': u'en-US', u'value': u'@pisco True Dat!'},
                u'link': u'http://identi.ca/notice/32316840', u'in-reply-to': u'', u'id': u'http://identi.ca/notice/32316840',
                u'updated_parsed': [2010, 5, 15, 15, 37, 40, 5, 135, 0]}

   """
    status = ''
    if 'subtitle' in entryJSON:
        status = entryJSON['subtitle']
    elif 'title' in entryJSON:
        status = entryJSON['title']
    else:
        log.debug("subtitle expected, missing %s" % str(entryJSON   ))
    if re.match(r'^\w+:.*$', status):
        parts = status.split(':')
        if parts:
            tweeter = parts[0]
            status = ':'.join(parts[1:])            
    
    rawtags = re.findall('#(\w+)', status)
    tags = [{'tag': r, 'name': r} for r in rawtags]
    
    status = re.sub('!(\w+)', r'<a href="http://identi.ca/group/\1">!\1</a>', status)
    status = re.sub('#(\w+)', r'<a href="http://identi.ca/tag/\1">#\1</a>', status)
    status = re.sub('@(\w+)', r'<a href="http://identi.ca/\1">@\1</a>', status)
    status = bleach.linkify(status.replace('\n', '<br />'))
    
    
    return {'status': status, 'permalink': entryJSON['link'], 'tags': tags, 'raw': entryJSON}