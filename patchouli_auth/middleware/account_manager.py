class AccountManagerMiddleware(object):
    def process_response(self, request, response):        
        response['Link'] = "<http://%s:%s/static/.well-known/host-meta>; rel=\"account-mgmt\"" % (request.META['HTTP_HOST'], request.META['SERVER_PORT'])
        return response