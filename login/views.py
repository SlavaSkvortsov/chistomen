from rest_social_auth.views import SocialTokenOnlyAuthView
from urllib.parse import urlparse
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status


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

    def post(self, request, *args, **kwargs):
        idinfo = id_token.verify_oauth2_token(
            request.data['code'], requests.Request()
        )
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return Response({'error': 'Wrong issuer.'}, status=status.HTTP_400_BAD_REQUEST)

        email = idinfo['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(username=idinfo['name'], email=email)
            user.first_name = idinfo['given_name']
            user.last_name = idinfo['family_name']
            user.save()

        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)

        return Response({'token': token.key})
