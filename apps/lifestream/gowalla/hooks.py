from lifestream.generic.hooks import tidy_up

def prepare_entry(entryJSON, log):
    content = ''
    if 'content' in entryJSON:
        content = entryJSON['content'][0].value
    elif 'description' in entryJSON:
        content = entryJSON['description']
    else:
        #log.debug('unreadable... ' + str(entryJSON))
        pass
    image = None
    if 'links' in entryJSON:
        for link in entryJSON['links']:
            if link['rel'] == 'image':
                image = link['href']
    
    title = tidy_up(entryJSON['title'], log)
    content = tidy_up(content, log)
    
    tags = []
    if 'tags' in entryJSON:
        for tag in entryJSON['tags']:
            if 'term' in tag:
                tags.append({'tag': tag['term'], 'name': tag['term']})
    return {'entry': content, 'tags': tags, 'title': title, 'image': image, 'permalink': entryJSON['link'], 'raw': entryJSON}
    #return {'entry': str(entryJSON)}