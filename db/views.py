# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from db.models import Country, City, Traveltype, Travel
from db.serializers import *
from rest_framework import generics

class CountryList(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CountryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class CityList(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class TraveltypeList(generics.ListCreateAPIView):
    queryset = Traveltype.objects.all()
    serializer_class = TraveltypeSerializer

class TraveltypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Traveltype.objects.all()
    serializer_class = TraveltypeSerializer

class TravelList(generics.ListCreateAPIView):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer

class TravelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer
