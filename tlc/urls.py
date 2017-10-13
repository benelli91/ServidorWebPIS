from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^/$', views.cargaGoogle, name='cargaGoogle'),
    ##url(r'^your-name$', views.get_name, name='get_name')
    url(r'^loader$', views.cargaGenerica, name='cargaGenerica'),
    url(r'^Buquebus$', views.cargaBuquebus, name='cargaBuquebus'),
    url(r'^GoogleFlights$', views.cargaGoogleFlights, name='cargaGoogleFlights'),
    url(r'^Copay$', views.cargaCopay, name='cargaCopay'),
    url(r'^AgenciaCentral$', views.cargaAgenciaCentral, name='cargaAgenciaCentral'),
    url(r'^ColoniaExpress$', views.cargaColoniaExpress, name='cargaColoniaExpress'),
    url(r'^TresCruces$', views.cargaTresCruces, name='cargaTresCruces'),
    url(r'^Greyhound$', views.cargaGreyhound, name='cargaGreyhound'),
]
