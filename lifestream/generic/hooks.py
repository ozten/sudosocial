from bleach import Bleach
bleach = Bleach()

import re

def tidy_up(entry, log):
    # TODO Security, mostly using bleach to linkify and cleanup (tidy style)
    html_tags = ['a', 'abbr', 'b', 'blockquote', 'br', 'code', 'div', 'em', 'font', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                 'i', 'img', 'hr',
                 'math', 'mi', 'mo', 'mn', 'mfrac', 'mrow', 'msqrt', 'msup',
                 'pre', 'span', 'strong',
                 'svg', 'path', 'line', 'circle',
                 'table', 'caption', 'thead', 'tfoot', 'tbody', 'tr', 'td', 'th', 'colgroup', 'col', 
                 'ul', 'li', 'ol', 'p', 'q']
    attrs = {
        'a':       ['href', 'title'],
        'abbr':    ['title'],
        'acronym': ['title'],
    }
    try:
        return bleach.linkify(
                bleach.clean(entry, tags=html_tags, attributes=attrs))
    except Exception, x:
        log.error("Ouch, unable to linkify or clean _%s_" % entry)
        log.exception(x)
        return entry

def prepare_entry(entryJSON, log):
    content = ''
    if 'content' in entryJSON:
        content = entryJSON['content'][0].value
    elif 'description' in entryJSON:
        content = entryJSON['description']
    else:
        #log.debug('unreadable... ' + str(entryJSON))
        pass
    
    title = tidy_up(entryJSON['title'], log)
    content = tidy_up(content, log)
    
    tags = []
    if 'tags' in entryJSON:
        for tag in entryJSON['tags']:
            if 'term' in tag:
                tags.append({'tag': tag['term'], 'name': tag['term']})
    return {'entry': content, 'tags': tags, 'title': title, 'permalink': entryJSON['link'], 'raw': entryJSON}
    #return {'entry': str(entryJSON)}