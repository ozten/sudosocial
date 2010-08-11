""" WARNING: This plugin API is subject to change.
"""
import re

from plugins.basic import BasicPlugin

class HostnameCssPlugin(BasicPlugin):
    """
        Part of the plugins module. Take the hostname of the permalink and
        creates legal CSS classes out of it
    """
    def __init__(self, log):
        self.log = log
        self.hostnameRE = re.compile('http.?://([^/]*)/.*')
        
    def modify_entry_variables(self, entry, entry_variables):
        """ Callback before rendering templates, should return a Dict of
            items used in templated views """
        cssName = ''
        if 'permalink' in entry_variables:
            re_match = self.hostnameRE.match(entry_variables['permalink'])
        
            if re_match and len(re_match.groups()) > 0:
                cssName = (re_match.groups()[0]).replace('.', '-')
        
        entry_variables['hostname_css_class'] = cssName
        return (entry, entry_variables)
        
    
