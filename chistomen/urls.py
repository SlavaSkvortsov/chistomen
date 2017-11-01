"""chistomen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from login.views import TokenAuthView

EXAMPLE_URI_FOR_AUTH = 'https://oauth.vk.com/authorize?client_id=6073463&redirect_uri=http://localhost:8010/login/social/token/vk-oauth2/'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/social/token/(?:(?P<provider>[a-zA-Z0-9_-]+)/?)?$', TokenAuthView.as_view(), name='login_social_token'),
    url(r'^', include('garbage.urls'))
]
