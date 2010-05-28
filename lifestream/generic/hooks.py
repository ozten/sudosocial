from bleach import Bleach
bleach = Bleach()

import re

def prepare_entry(entryJSON, log):
    content = ''
    if 'content' in entryJSON:
        content = entryJSON['content'][0].value
    elif 'description' in entryJSON:
        content = entryJSON['description']
    else:
        #log.debug('unreadable... ' + str(entryJSON))
        pass
    try:
        content = bleach.linkify(content)
    except Exception, x:
        log.error("Ouch, unable to linkify _%s_" % content)
        log.exception(x)
    tags = []
    if 'tags' in entryJSON:
        for tag in entryJSON['tags']:
            if 'term' in tag:
                tags.append({'tag': tag['term'], 'name': tag['term']})
    return {'entry': content, 'tags': tags, 'title': entryJSON['title'], 'link': entryJSON['link'], 'raw': entryJSON}
    #return {'entry': str(entryJSON)}