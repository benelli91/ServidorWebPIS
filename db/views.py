# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from db.models import Country, City, Traveltype, Travel
from db.serializers import *
from rest_framework import generics
import math
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime,timedelta

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

def heuristic(city1, city2):
    return pow((math.pi/180)*(city1.latitude - city2.latitude), 2) + pow(math.cos((math.pi/180)*(city1.latitude-city2.latitude)/2)*((math.pi/180)*(city1.longitude - city2.longitude)),2)

def reconstruct_path(cameFrom, current, countries, origin_country, origin_city):
    total_path = [cameFrom[countries.index(current[0])][current[1]][current[2]][3]]
    while not ((current[0] == origin_country) and (current[1] == origin_city)):
        current = cameFrom[countries.index(current[0])][current[1]][current[2]]
        if not(current[0] == origin_country and current[1] == origin_city):
            total_path.append(cameFrom[countries.index(current[0])][current[1]][current[2]][3])
    return total_path

def Eppstein(origin_country, origin_city, destination_country, destination_city, start_date, finish_date, k):
    start_city = City.objects.filter(country = origin_country, id = origin_city)[0]
    final_city = City.objects.filter(country = destination_country, id = destination_city)[0]
    aux_countries = Country.objects.all()
    cities = City.objects.all()
    countries = []
    for co in aux_countries:
        countries.append(co.id)

    P = []
    B = []
    countU = [[None]*len(cities)]*len(countries)
    for ci in cities:
        countU[countries.index(ci.country)][ci.id] = 0

    B.append([[start_city], 0])
    while len(B) > 0 and countFinal < k:
        Pu = B[0]
        for b in B:
            if b[1] < Pu[1]:
                Pu = b
        B.remove(b)
        countU[countries.index(Pu[0][-1].country)][Pu[0][-1].id] += 1
        if Pu[0][-1].country == destination_country and Pu[0][-1].id == destination_city:
            P.append(Pu)
        if countU[countries.index(Pu[0][-1].country)][Pu[0][-1].id] <= k:
            neighbors = []
            if Pu[0][-1].country == origin_country and Pu[0][-1].id == origin_city:
                neighbors = Travel.objects.raw('''SELECT * FROM travel WHERE origin_country = %s AND origin_city = %s AND departure > %s AND departure + duration < %s''', [Pu[0][-1].country, Pu[0][-1].id, start_date, finish_date])
            else:
                arrival_interval = datetime.combine(P[0][-2].departure, P[0][-2].duration) - start_date
                arrival = int(arrival_interval.total_seconds() // 3600)
                neighbors = Travel.objects.raw('''SELECT * FROM travel WHERE origin_country = %s AND origin_city = %s AND departure > %s AND departure + duration < %s''', [Pu[0][-1].country, Pu[0][-1].id, start_date + timedelta(hours = arrival]), finish_date])

            for n in neighbors:
                flag = False
                counter = 1
                while (counter < len(Pu[0])) and (not flag):
                    if Pu[0][counter].idtravel == n.idtravel:
                        flag = True
                    counter += 2
                if not flag:
                    Pv = Pu
                    middle_city = City.objects.filter(country = n.destination_country, id = n.destination_city)[0]
                    Pv[0].append(n)
                    Pv[0].append(middle_city)
                    Pv[1] += n.price
                    print(Pu, Pv)
                    B.append(Pv)
    result = [[]]
    counter = 0
    for p_aux in P:
        for i in range(1, len(p_aux[0])//2):
            result[counter].append(p_aux[0][i*2 - 1])
    return result


def index(request):
    start_date = datetime.strptime('2017-09-01  00:00:00', '%Y-%m-%d %H:%M:%S')
    finish_date = datetime.strptime('2017-09-04  00:00:00', '%Y-%m-%d %H:%M:%S')
    vOrigin_country = 'URU'
    vOrigin_city = 6
    vDestination_country = 'ARG'
    vDestination_city = 29
    print(str(datetime.now()) + '  --inicio' )
    list_travels = AAster(vOrigin_country, vOrigin_city, vDestination_country, vDestination_city, start_date, finish_date, 3)
    print(str(datetime.now())+ '  --fin')
    print len(list_travels)
    context = {
    'latest_question_list': list_travels}
    return render(request, 'db/index.html', context)
