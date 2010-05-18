""" Used by the Stream Editor to show all optional attributes
    of an entry
"""

from patchouli.plugins.basic import BasicPlugin

class StreamEditorPlugin(BasicPlugin):
    """
        Plugin controls behaviors related to the stream editor
    """    
    
    def template_variables(self):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        return {'show_everything': True}