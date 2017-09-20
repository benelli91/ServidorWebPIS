from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^/$', views.cargaGoogle, name='cargaGoogle'),
    ##url(r'^your-name$', views.get_name, name='get_name')

]
