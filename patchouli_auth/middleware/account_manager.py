class AccountManagerMiddleware(object):
    def process_response(self, request, response):        
        response['Link'] = "<http://patchouli.ubuntu/static/.well-known/host-meta>; rel=\"account-mgmt\""
        return response