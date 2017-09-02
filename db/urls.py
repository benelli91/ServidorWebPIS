from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from db import views

urlpatterns = [
    url(r'^country/$', views.CountryList.as_view()),
    url(r'^country/(?P<pk>[0-9]+)/$', views.CountryDetail.as_view()),
    url(r'^city/$', views.CityList.as_view()),
    url(r'^city/(?P<pk>[0-9]+)/$', views.CityDetail.as_view()),
    url(r'^traveltype/$', views.TraveltypeList.as_view()),
    url(r'^traveltype/(?P<pk>[0-9]+)/$', views.TraveltypeDetail.as_view()),
    url(r'^travel/$', views.TravelList.as_view()),
    url(r'^travel/(?P<pk>[0-9]+)/$', views.TravelDetail.as_view())
]
