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
    countU = [[]]
    for ci in cities:
        for hour in range(0, 71):
            countU[countries.index(ci.country)][ci.id] = 0




    for ci in cities:
        for hour in range(0, 71):
            gScore[countries.index(ci.country)][ci.id][hour] = float('inf')
            fScore[countries.index(ci.country)][ci.id][hour] = float('inf')

    gScore[countries.index(origin_country)][origin_city][0] = 0
    fScore[countries.index(origin_country)][origin_city][0] = heuristic(start_city, final_city)

    cameFrom[1][29][15] = ['basura', 'basura', 'basura', 'basura']
    while len(openSet) > 0:
        current = [openSet[0][0], openSet[0][1], openSet[0][2]]
        for i in range(0, len(openSet)-1):
            if fScore[countries.index(openSet[i][0])][openSet[i][1]][openSet[i][2]] < fScore[countries.index(current[0])][current[1]][current[2]]:
                current = openSet[i]

        if current[0] == destination_country and current[1] == destination_city:
            return reconstruct_path(cameFrom, current, countries, origin_country, origin_city)

        current_city = City.objects.filter(country = current[0], id  = current[1])[0]
        closedSet.append([current[0], current[1], current[2]])
        openSet.remove([current[0], current[1], current[2]])


        neighbors = Travel.objects.raw('''SELECT * FROM travel WHERE origin_country = %s AND origin_city = %s AND departure > %s AND departure + duration < %s''', [current[0], current[1], start_date + timedelta(hours = current[2]), finish_date])
        for n in neighbors:
            arrival_interval = datetime.combine(n.departure, n.duration) - start_date
            arrival = int(arrival_interval.total_seconds() // 3600)
            if not [n.destination_country, n.destination_city, arrival] in closedSet:
                if not [n.destination_country, n.destination_city, arrival] in openSet:
                    openSet.append([n.destination_country, n.destination_city, arrival])

                current_gScore = gScore[countries.index(current[0])][current[1]][current[2]]
                tentative_gScore = current_gScore + n.price
                if tentative_gScore < gScore[countries.index(n.destination_country)][n.destination_city][arrival]:
                    cameFrom[countries.index(n.destination_country)][n.destination_city][arrival] = [current[0], current[1], current[2], n]
                    gScore[countries.index(n.destination_country)][n.destination_city][arrival] = tentative_gScore
                    destiny = cities[0]
                    for ci in cities:
                        if ci.country == n.destination_country and ci.id == n.destination_city:
                            destiny = ci
                    fScore[countries.index(n.destination_country)][n.destination_city][arrival] + heuristic(destiny, final_city)
    return []


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
