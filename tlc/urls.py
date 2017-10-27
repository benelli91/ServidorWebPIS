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
    url(r'^cargaGoogle$', views.cargaGoogle, name='cargaGoogle'),
    url(r'^rest/tlc/', include(router.urls)),
    url(r'^loader$', views.cargaGenerica, name='cargaGenerica'),
    url(r'^Buquebus$', views.cargaBuquebus, name='cargaBuquebus'),
    url(r'^Buquebus2$', views.cargaBuquebus2, name='cargaBuquebus2'),
    url(r'^GoogleFlights$', views.cargaGoogleFlights, name='cargaGoogleFlights'),
    url(r'^Copay$', views.cargaCopay, name='cargaCopay'),
    url(r'^AgenciaCentral$', views.cargaAgenciaCentral, name='cargaAgenciaCentral'),
    url(r'^ColoniaExpress$', views.cargaColoniaExpress, name='cargaColoniaExpress'),
    url(r'^TresCruces$', views.cargaTresCruces, name='cargaTresCruces'),
    url(r'^Greyhound$', views.cargaGreyhound, name='cargaGreyhound'),
    url(r'^UruBus$', views.cargaUruBus, name='UruBus'),
]
