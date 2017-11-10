from django.conf.urls import url
from django.contrib import admin
from login.views import TokenAuthView
from .views import GarbageView, GarbageDetail, GarbagePhoto, DelPhoto, GarbageDescriptionView, DelDescription, ChangeStatus

urlpatterns = [
    url(r'^garbage/$', GarbageView.as_view()),
    url(r'^garbage/(?P<pk>[0-9]+)/$', GarbageDetail.as_view()),
    url(r'^garbage/(?P<pk>[0-9]+)/photo/$', GarbagePhoto.as_view()),
    url(r'^garbage/(?P<pk>[0-9]+)/photo/(?P<pk_photo>[0-9]+)/$', DelPhoto.as_view()),
    url(r'^garbage/(?P<pk>[0-9]+)/description/$', GarbageDescriptionView.as_view()),
    url(r'^garbage/(?P<pk>[0-9]+)/description/(?P<pk_description>[0-9]+)/$', DelDescription.as_view()),
    url(r'^garbage/(?P<pk>[0-9]+)/status/$', ChangeStatus.as_view()),
]
