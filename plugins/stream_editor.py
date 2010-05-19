""" Used by the Stream Editor to show all optional attributes
    of an entry
"""
import datetime
import urlparse

from patchouli.plugins.basic import BasicPlugin

class StreamEditorPlugin(BasicPlugin):
    """
        Plugin controls behaviors related to the stream editor
    """
    def modify_entry_variables(self, entry, entry_variables):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        
        metadata = {'published': None, 'time_ago': None,
                    'show_everything': True}
        #TODO get Hooks to populate this universally
        if 'link' in entry:
            urlparts = urlparse.urlparse(entry.link)
            metadata['website_name'] = urlparts.netloc
        if 'published_parsed' in entry and 'updated_parsed' in entry:
            metadata['published'] = datetime.datetime(*entry.published_parsed[0:7])
            updated = datetime.datetime(*entry.updated_parsed[0:7])
            if not metadata['published'] == updated:
                metadata['time_ago'] = updated - metadata['published']
        elif 'published_parsed' in entry:
            metadata['published'] = datetime.datetime(*entry.published_parsed[0:7])
        elif 'updated_parsed' in entry:
            metadata['published'] = datetime.datetime(*entry.updated_parsed[0:7])
        metadata['published_date'] = metadata['published'].strftime("%A, %B %d %I:%Mp")
        entry_variables.update(metadata)
        return (entry, entry_variables)