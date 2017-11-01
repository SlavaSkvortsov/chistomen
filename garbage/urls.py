from django.conf.urls import url
from django.contrib import admin
from login.views import TokenAuthView
from .views import GarbageCreate, GarbageDetail

urlpatterns = [
    url(r'^garbage/$', GarbageCreate.as_view()),
    url(r'^garbage/(?P<pk>[0-9]+)/$', GarbageDetail.as_view()),
]
