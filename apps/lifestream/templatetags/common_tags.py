from django import template

register = template.Library()

class SecureUrlBlock(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        relative_path = self.nodelist.render(context).strip()
        req = template.Variable('request').resolve(context)
        hostname = req.get_host()
        url_parts = (hostname, relative_path)
        # Developers running on 8000
        if hostname.find(':'):
            return "http://%s%s" % url_parts
        else:
            return "https://%s%s" % url_parts
    
def secure_url_block(parser, token):
    """
    The Secure url block tag wraps the output of url tag in https.
    {% secure %}{% url path.to.some_view v1 v2 %} {% endsecure %}
    or named url:
    {% secure %}{% url login_url %} {% endsecure %}
    If login_url were '/auth/login then the secure url block will render
    https://example.com/auth/login
    as a convience to developers, running the server on a different port will render
    http://localhost:8000/auth/login
    
    Note: Requires TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.request',
          be in the list of processors in settings.py
    """
    nodelist = parser.parse(('endsecure'))
    parser.delete_first_token()
    return SecureUrlBlock(nodelist)
    
register.tag('secure', secure_url_block)