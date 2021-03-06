from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'travels', views.TravelViewSet, base_name='travel')
router.register(r'citys', views.CityViewSet, base_name='city')
router.register(r'countrys', views.CountryViewSet, base_name='country')
router.register(r'travelagencys', views.TravelAgencyViewSet, base_name='travelagency')
router.register(r'traveltypes', views.TravelTypeViewSet, base_name='traveltype')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^doSearch/$', views.doSearch, name='doSearch'),
    url(r'^rest/tlc/', include(router.urls)),
]
