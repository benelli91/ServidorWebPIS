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
    countU = [[0]*(len(cities)+1) for i in range(len(countries))]
    B.append([[start_city], 0])
    while len(B) > 0 and countU[countries.index(destination_country)][destination_city] < k:
        Pu = B[0]
        for b in B:
            if b[1] < Pu[1]:
                Pu = b
        B.remove(b)
        countU[countries.index(Pu[0][-1].country)][Pu[0][-1].id] = countU[countries.index(Pu[0][-1].country)][Pu[0][-1].id] + 1
        if Pu[0][-1].country == destination_country and Pu[0][-1].id == destination_city:
            print("llegue aqui")
            P.append(Pu)
        if countU[countries.index(Pu[0][-1].country)][Pu[0][-1].id] <= k:
            neighbors = []
            if Pu[0][-1].country == origin_country and Pu[0][-1].id == origin_city:
                neighbors = Travel.objects.raw('''SELECT * FROM travel WHERE origin_country = %s AND origin_city = %s AND departure > %s AND departure + duration < %s''', [Pu[0][-1].country, Pu[0][-1].id, start_date, finish_date])
            else:
                last_travel = Pu[0][-2]
                arrival_interval = datetime.combine(last_travel.departure, last_travel.duration) - start_date
                arrival = int(arrival_interval.total_seconds() // 3600)
                neighbors = Travel.objects.raw('''SELECT * FROM travel WHERE origin_country = %s AND origin_city = %s AND departure > %s AND departure + duration < %s''', [Pu[0][-1].country, Pu[0][-1].id, start_date + timedelta(hours = arrival), finish_date])

            for n in neighbors:
                flag = False
                counter = 1
                while (counter < len(Pu[0])) and (not flag):
                    if Pu[0][counter].idtravel == n.idtravel:
                        flag = True
                    counter += 2
                if not flag:
                    Pv = [[]]
                    middle_city = City.objects.filter(country = n.destination_country, id = n.destination_city)[0]
                    for i in range(0, len(Pu[0])):
                        Pv[0].append(Pu[0][i])
                    Pv[0].append(n)
                    Pv[0].append(middle_city)
                    Pv.append(Pu[1] + n.price)
                    print("Pu: \n")
                    print(Pu)
                    print("Pv: \n")
                    print(Pv)
                    B.append(Pv)

    print(len(B))
    result = []
    counter = 0
    for p_aux in P:
        for i in range(1, len(p_aux[0])//2):
            result[counter].append(p_aux[0][i*2 - 1])
        counter+=1
    return P


def index(request):
    start_date = datetime.strptime('2017-09-01  00:00:00', '%Y-%m-%d %H:%M:%S')
    finish_date = datetime.strptime('2017-09-04  00:00:00', '%Y-%m-%d %H:%M:%S')
    vOrigin_country = 'URU'
    vOrigin_city = 6
    vDestination_country = 'ARG'
    vDestination_city = 29
    k = 5
    print(str(datetime.now()) + '  --inicio' )
    list_travels = Eppstein(vOrigin_country, vOrigin_city, vDestination_country, vDestination_city, start_date, finish_date, k)
    print(str(datetime.now())+ '  --fin')
    print(len(list_travels))


    context = {
    'latest_question_list': list_travels}
    return render(request, 'db/index.html', context)
