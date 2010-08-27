""" Used by the Stream Editor to show all optional attributes
    of an entry
"""
from datetime import datetime
import urlparse

from plugins.basic import BasicPlugin

class StreamEditorPlugin(BasicPlugin):
    """
        Plugin controls behaviors related to the stream editor
    """
    def modify_entry_variables(self, entry, entry_variables):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        
        metadata = {'published': None, 'time_ago': None,
                    'show_everything': True}        
        if 'link' in entry:
            urlparts = urlparse.urlparse(entry.link)
            metadata['website_name'] = urlparts.netloc
        if 'published_parsed' in entry and 'updated_parsed' in entry:
            metadata['published'] = datetime(*entry.published_parsed[0:7])
            updated = datetime(*entry.updated_parsed[0:7])
            if not metadata['published'] == updated:
                metadata['time_ago'] = updated - metadata['published']
        elif 'published_parsed' in entry:
            metadata['published'] = datetime(*entry.published_parsed[0:7])
        elif 'updated_parsed' in entry:
            metadata['published'] = datetime(*entry.updated_parsed[0:7])
        format = "%A, %B %d %I:%Mp"
        if metadata['published']:
            metadata['published_date'] = metadata['published'].strftime(format)
        entry_variables.update(metadata)
        return (entry, entry_variables)
        
    def template_variables(self):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        return {'stream_editor_mode': True}
