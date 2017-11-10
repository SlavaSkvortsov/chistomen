from rest_social_auth.views import SocialTokenOnlyAuthView
from urllib.parse import urlparse
import copy


class TokenAuthView(SocialTokenOnlyAuthView):
    def get(self, request, provider):
        # Making from get request - post request and send to lib
        if isinstance(self.request.GET['code'], list):
            self.request.data.update({'code': self.request.GET['code'][0]})
        else:
            self.request.data.update({'code': self.request.GET['code']})
        uri = urlparse(self.request.build_absolute_uri())
        self.request.data.update({'redirect_uri': uri.scheme + '://' + uri.netloc + uri.path})
        return self.post(request)