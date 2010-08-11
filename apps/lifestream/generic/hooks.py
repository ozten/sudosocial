import re

import lxml.etree
import lxml.html.soupparser

from django.conf import settings

from bleach import Bleach
bleach = Bleach()

def tidy_up(entry, log):
    # TODO Security, mostly using bleach to linkify and cleanup (tidy style)
    html_tags = ['a', 'abbr', 'b', 'blockquote', 'br',
                 'cite', 'code', 'dd', 'dl', 'div', 'dt',
                 'em', 'font', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                 'i', 'img', 'hr',
                 'math', 'mi', 'mo', 'mn', 'mfrac', 'mrow', 'msqrt', 'msup',
                 'pre', 'span', 'strong',
                 'svg', 'path', 'line', 'circle',
                 'strike', 'strong', 'sub'
                 'table', 'caption', 'thead', 'tfoot', 'tbody', 'tr', 'td', 'th', 'colgroup', 'col',
                 'tt', 'var',
                 'ul', 'li', 'ol', 'p', 'q']
    
    a_attrs = ['href', 'rel', 'title']
    img_attrs = ['align', 'alt', 'border', 'height','src', 'width']
    basic_attrs = ['class', 'dir', 'lang', 'title']
    
    [x.extend(basic_attrs) for x in (a_attrs, img_attrs)]
    
    attrs = {
        'a': a_attrs,
        'img': img_attrs,
        
        'abbr':    basic_attrs,
        'acronym': basic_attrs,
        'div': basic_attrs,
        'span': basic_attrs,
        'p': basic_attrs,
        
    }    
    try:
        # Bugfix wrap content in <div> and then pop it out, othewise 'foo <span>bar</span>' will fail        
        htmlElement = lxml.html.soupparser.fromstring("<div>%s</div>" % entry[0:settings.PATCHOULI_TLDR])
        elements = ''.join([lxml.html.tostring(el) for el in htmlElement.getchildren()])
        
        # <div> - 5 </div> - 6 characters
        return bleach.linkify(
                bleach.clean(elements[5:-6], tags=html_tags, attributes=attrs))
    except Exception, x:
        log.error("Ouch, unable to linkify or clean _%s_\nError: %s" % (entry, x))
        log.exception(x)
        return entry

def prepare_entry(entryJSON, log):    
    content = ''
    if 'content' in entryJSON:        
        content = entryJSON['content'][0].value
    elif 'description' in entryJSON:
        content = entryJSON['description']
    else:
        log.debug('unreadable... ' + str(entryJSON))
        pass
        
    title = tidy_up(entryJSON['title'], log)
    content = tidy_up(content, log)
    
    # Generic image in feed?
    image = None
    if 'links' in entryJSON:
        for link in entryJSON['links']:
            if link['rel'] == 'image':
                image = link['href']
            
    tags = []
    if 'tags' in entryJSON:
        for tag in entryJSON['tags']:
            if 'term' in tag:
                tags.append({'tag': tag['term'], 'name': tag['term']})
    return {'entry': content, 'tags': tags, 'title': title, 'permalink': entryJSON['link'], 'raw': entryJSON, 'image': image}