""" WARNING: This plugin API is subject to change.
"""
class BasicPlugin(object):
    """
        Part of the plugins module. Gives default behaviors to plugins
    """
    def __init__(self, log):
        self.log = log
        
    def observe_stream_entry(self, entry, entry_variables):
        """ Callback for inspecting an entry or it's
            post-hook variables """
        pass

    def post_observe_stream_entries(self):
        """ Callback after observe_stream_entry has been called
            with every entry """        
        pass
    
    def modify_entry_variables(self, entry, entry_variables):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        return (entry, entry_variables)
    
    def template_variables(self):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        return {}