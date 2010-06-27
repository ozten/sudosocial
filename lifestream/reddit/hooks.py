from lifestream.generic.hooks import tidy_up

def prepare_entry(entryJSON, log):
    content = ''
    if 'content' in entryJSON:
        content = entryJSON['content'][0].value
    elif 'description' in entryJSON:
        content = entryJSON['description']
    elif 'title' in entryJSON:
        content = entryJSON['title']
    else:
        content = 'unreadable... ' + str(entryJSON)    
    try:
        content = tidy_up(content, log)    
    except Exception, x:
        log.error("Ouch, unable to linkify _%s_" % content)
        log.exception(x)
    tags = []
    if 'tags' in entryJSON:
        for tag in entryJSON['tags']:
            if 'term' in tag:
                tags.append({'tag': tag['term'], 'name': tag['term']})
    
    return {'entry': content, 'tags': tags, 'raw': entryJSON, 'permalink': entryJSON.link}
    #return {'entry': str(entryJSON)}