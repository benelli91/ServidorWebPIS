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
    for conf_file in raw_files:
        with open(config_directory + conf_file) as data_file:
            data = json.load(data_file)
        loadWebpage(data)

def loadWebpage(conf_file):
    webpage_name = conf_file["webpage"]["name"]
    print webpage_name

    cities = []
    if(conf_file["webpage"]["travel_type"] == 1):
        cities = City.objects.filter(airport = True)
    elif(conf_file["webpage"]["travel_type"] == 2):
        cities = City.objects.filter(port = True)
    elif(conf_file["webpage"]["travel_type"] == 3):
        cities = City.objects.filter(bus_station = True)

    span = conf_file["webpage"]["date_span"]
    if(span == 0):
        span = DEFAULT_SPAN
    dates = [datetime.today().date()]
    for i in range(1, span):
        print dates[-1]
        dates.append(dates[-1] + timedelta(days=1))


    travels = []
    url = conf_file["webpage"]["uri_start"]

    for origin_city in cities:
        for destination_city in cities:
            if(origin_city.id != destination_city.id):
                if(conf_file["webpage"]["frecuency_format"] == ""):
                    for departure in dates:
                        if(conf_file["webpage"]["javascript"] == False):
                            url = createURL(conf_file, origin_city, destination_city, departure)
                            print url
                        travels = travels + extractData(conf_file, url)
                else:
                    if(conf_file["webpage"]["javascript"] == False):
                        url = createURL(conf_file, origin_city, destination_city, datetime.today().date())
                    travels = travels + extractData(conf_file, url)

    """with transaction.atomic():
        Travel.objects.filter(webpage = webpage_name).delete()
        for travel in travels:
            travel.save()"""

def createURL(conf_file, origin_city, destination_city, departure):
    url = conf_file["webpage"]["uri_start"]
    separator = conf_file["webpage"]["header_parameters"]["separator"]
    data = ""
    date_format = conf_file["webpage"]["header_parameters"]["date_format"]
    total_parameters = len(conf_file["webpage"]["header_parameters"]["parameters"])
    counter = 0
    while counter < total_parameters:
        parameter = conf_file["webpage"]["header_parameters"]["parameters"][counter]
        url += parameter["parameter"]
        data = str(parameter["data"])
        #explosion = conf_file["webpage"]["header_parameters"]["parameters"][900]
        #CASE for each posible value of the "data" attribute of the configuration file
        if(data == u"origin_country"):
            url += str(origin_city.country)
        elif(data == u"destination_country"):
            url += str(destination_city.country)
        elif(data == u"origin_city"):
            url += str(origin_city.name)
        elif(data == u"destination_city"):
            print "llegue aca"
            url += str(destination_city.name)
        elif(data == u"alias_origin"):
            url += str(origin_city.alias_flight)
        elif(data == u"alias_destination"):
            url += str(destination_city.alias_flight)
        elif(data == u"departure"):
            url += departure.strftime(date_format)
        elif(data == u"actual_date"):
            today = datetime.today().date()
            url += today.strftime(date_format)

        if(counter < total_parameters - 1):
            url += separator
        counter += 1

    url += conf_file["webpage"]["uri_end"]

    return url

def extractData(conf_file, url):
    #TODO: extraer los datos de la url con el archivo de configuracion, transformarlos en instancias de
    #Travel y devolverlos
    #TODO: dividir en dos casos, extraer los datos con javascript y sin javascript
    return []
