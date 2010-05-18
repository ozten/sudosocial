""" WARNING: This plugin API is subject to change.

    This plugin looks at the tags in a stream and tries to figure
    out the user's current set of social identities.
"""
from patchouli.plugins.basic import BasicPlugin

class SocialIdentityFromTagsPlugin(BasicPlugin): #
    """
        entries_with_identity = [
           entry[feed_id+guid] = [{tag, count}, {tag, count}]
        ]
        identity_count {
            'tag': {tag, name, count, entries[feed_id+guid, feed_id+guid]}
        }
        1 load all entries
        2 update identity_count
        3.1 if empty, break
        3.2 sort by count
        4 pop top tag
        5.1 if top tags > 5, break
        5.2 remove all entres with that tag
        6 goto 2
    """
    def __init__(self):
        self.identities = []
        self.identity_count = {}
        self.entries_with_identity = {}
        
    def observe_stream_entry(self, entry, entry_variables):
        """ Callback for inspecting an entry or it's
            post-hook variables """
        guid = entry.feed_id + entry.guid
        self.entries_with_identity[guid] = {'tags': []}
        for tag in entry_variables['tags']:
            low_tag = tag['tag'].lower()
            #Skip List
            if 'ping.fm' == low_tag:
                continue
            if low_tag not in self.identity_count:
                tag_name = tag['tag'].capitalize()
                if 'name' in tag:
                    tag_name = tag['name']
                self.identity_count[low_tag] = {'count': 0, 'name': tag_name,
                                          'tag': low_tag}
            self.entries_with_identity[guid]['tags'].append(low_tag)
            self.identity_count[low_tag]['count'] += 1
            self.identities.append(self.identity_count[low_tag]) 

    def post_observe_stream_entries(self):
        """ Callback after observe_stream_entry has been called
            with every entry """
        self.identities = []
        for _ in range(5):
            # TODO apply decorate-sort-undecorate pattern.
            # sorted(identity_count.values(),
            # key=lambda x: x['count']) is the preferred way.
            identity_list = sorted(self.identity_count.values(),
                                   cmp=cmp_identity)
            
            # We skip of up to 5 current topics
            if len(identity_list) == 0 or (not identity_list[0]['count'] > 1):
                break
            self.identities.append(
                self.identity_count.pop(
                    identity_list[0]['tag']))
            for k, value in self.entries_with_identity.items():
                if identity_list[0]['tag'] in value['tags']:
                    # nuke entry
                    for tag in value['tags']:
                        # Skips t == identity_list[0]['tag'],
                        # which we've already removed
                        if tag in self.identity_count:
                            self.identity_count[tag]['count'] -= 1
                    # remove this entry
                    self.entries_with_identity.pop(k)
    def template_variables(self):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        return {'identities': self.identities,
                'show_social_identities': True}
                    
def cmp_identity(left_tag, right_tag):
    """ Compares two tags for sort order, basedon their
        count property """
    return cmp(right_tag['count'], left_tag['count'])
