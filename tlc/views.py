# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .forms import NameForm
from .forms import NameForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from algoritmo import do_search
from cargaGoogleBatch import cargaGoogleB

from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from .serializers import TravelSerializer, TravelTypeSerializer, \
    TravelAgencySerializer, CountrySerializer, CitySerializer, \
    CitySearchSerializer

from .models import Travel, Traveltype, Travelagency, City, Country

class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer
    
    @list_route(methods=['get'])
    def do_search(self, request, pk=None):
        from_city = request.data.get('from', None)
        to_city = request.data.get('to', None)
        date = request.data.get('date', None)
        if from_city is not None and to_city is not None and date is not None:
            resultado = do_search(str(from_city), str(to_city), str(date))
            return Response(status=status.HTTP_200_OK, data=resultado)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid blank input data")

class TravelAgencyViewSet(viewsets.ModelViewSet):
    queryset = Travelagency.objects.all()
    serializer_class = TravelAgencySerializer

class TravelTypeViewSet(viewsets.ModelViewSet):
    queryset = Traveltype.objects.all()
    serializer_class = TravelTypeSerializer
    
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = TravelSerializer
    
    @list_route(methods=['get'])
    def autocomplete_search(self, request, pk=None):
        search = request.query_params.get('search', '')
        cities = City.objects.filter(name__startswith=search)[:5]
        return Response(status=status.HTTP_200_OK, data=CitySearchSerializer(cities, many=True).data)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

def index(request):
    # if this is a POST request we need to process the form data
    resultado = {}
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        #if form.is_valid(): //FALTA CHEQUEAR QUE SEA VALIDO EL FORM
            #redirect('tlc.views.index')
        data = request.POST
        resultado = do_search(str(data.get("from", "")),str(data.get("to")),str(data.get("date")))
        print resultado
    	# if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'index.html',  resultado)

def cargaGoogle(request):
    resultado = {}
    #if request.method == 'POST':
    #    resultado = do_search(str(data.get("from", "")),str(data.get("to")),str(data.get("date")))
    cargaGoogleB()

    return render(request, 'scraping.html',  resultado)
