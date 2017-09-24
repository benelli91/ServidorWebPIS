from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime,timedelta,tzinfo
from .models import *
import time
import sys
import os
import json
from django.db import transaction

DEFAULT_SPAN = 30

def genericLoader():
    config_directory = 'tlc/config_files/'
    raw_files = [pos_json for pos_json in os.listdir(config_directory) if pos_json.endswith('.json')]
    Travel.objects.all().delete()
    for conf_file in raw_files:
        with open(config_directory + conf_file) as data_file:
            data = json.load(data_file)
        loadWebpage(data)

def loadWebpage(conf_file):
    print str(conf_file["webpage"]["name"])

    cities = []
    if(conf_file["webpage"]["travel_type"] == 1):
        cities = City.objects.filter(airport = true)
    elif(conf_file["webpage"]["travel_type"] == 2):
        cities = City.objects.filter(port = true)
    elif(conf_file["webpage"]["travel_type"] == 3):
        cities = City.objects.filter(bus_station = true)

    span = conf_file["webpage"]["date_span"]
    if(span == 0):
        span = DEFAULT_SPAN
    dates = [datetime.date.today()]
    for i in range(1, span):
        dates.append(dates[-1] + datetime.timedelta(days=1))

    travels = []

    for origin_city in cities:
        for destination_city in cities:
            if(origin_city != destination_city):
                if(conf_file["webpage"]["frecuency_format"] == ""):
                    for departure in dates:
                        url = createURL(conf_file, origin_city, destination_city, departure)
                        travels = travels + extractData(conf_file, url)
                else:
                    url = createURL(conf_file, origin_city, destination_city, None)
                    travels = travels + extractData(conf_file, url)

    with transaction.atomic():
        for travel in travels:
            travel.save()

def createURL(conf_file, origin_city, destination_city, departure):
    #TODO: crear y devolver una url a partir del archivo de configuracion, la ciudad de origen,
    #la ciudad de destino y la fecha de partida (la fecha puede ser None si los viajes de la pagina
    # tienen frecuencia)
    #TODO: dividir en dos casos, si se usa javascript para obtener los datos obtener la url es
    #trivial, simplemente se devuelve la url_start del archivo de configuracion, sino hay que generarla
    return ""

def extractData(conf_file, url):
    #TODO: extraer los datos de la url con el archivo de configuracion, transformarlos en instancias de
    #Travel y devolverlos
    #TODO: dividir en dos casos, extraer los datos con javascript y sin javascript
    return []
