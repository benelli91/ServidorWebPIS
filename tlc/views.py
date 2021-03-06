# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .forms import NameForm
from .forms import NameForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from algoritmo import do_search
from cargaGenericaBatch import *
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from .serializers import TravelSerializer, TravelTypeSerializer, \
    TravelAgencySerializer, CountrySerializer, CitySerializer, \
    CitySearchSerializer, CompleteTravelSerializer

from .models import Travel, Traveltype, Travelagency, City, Country

class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer

    @list_route(methods=['get'])
    def do_search(self, request, pk=None):
        from_city = request.GET.get('from', None)
        to_city = request.GET.get('to', None)
        date = request.GET.get('date', None)
        if from_city is not None and to_city is not None and date is not None:
            resultado = do_search(str(from_city), str(to_city), str(date))
            travels = {'list_travels':[]}
            for group in resultado['list_travels']:
                #print group
                travels['list_travels'].append(CompleteTravelSerializer(group, many=True).data)
            return Response(status=status.HTTP_200_OK, data=travels)
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
    serializer_class = CitySerializer

    @list_route(methods=['get'])
    def autocomplete_search(self, request, pk=None):
        search = request.query_params.get('term', '')
        cities = City.objects.filter(name__startswith=search)
        return Response(status=status.HTTP_200_OK, data=CitySearchSerializer(cities, many=True).data)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

def index(request):
    # if this is a POST request we need to process the form data

    resultado = {}
    if request.method == 'POST':
        #form = NameForm(request.POST)

        data = request.POST
        from_city = str(data.get("from", ""))
        to_city = str(data.get("to"))
        date = str(data.get("date"))
        timezone = int(data.get("timezoneOffset"))
        resultado = do_search(from_city, to_city, date, timezone)
        #return render(request, 'search_results.html',  resultado)
    else:
        form = NameForm()

    return render(request, 'index.html',  resultado)

def doSearch(request):
    # view used to call from javascript, for not reloading the page
    resultado = {}
    data = request.GET
    from_city = str(data.get("from", ""))
    to_city = str(data.get("to"))
    date = str(data.get("date"))
    timezone = int(data.get("timezoneOffset"))
    resultado = do_search(from_city, to_city, date, timezone)
    return render(request, 'search_results.html',  resultado)

def loadExchange(request):
    from exchange import loadExchange
    resultado = {}
    loadExchange()
    return redirect('/')

def cargaGenerica(request):
    genericLoader()
    resultado = {}
    return render(request, 'scraping.html', resultado)

def cargaTimed(request):
    timedGenericLoader()
    resultado = {}
    return render(request, 'scraping.html', resultado)
