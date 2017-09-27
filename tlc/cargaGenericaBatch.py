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
import unidecode

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
    phantom = webdriver.PhantomJS()

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
    page_type = conf_file["webpage"]["page_type"]

    if(page_type == 1): #URL type pages
        for origin_city in cities:
            for destination_city in cities:
                if(origin_city.id != destination_city.id):
                    if(conf_file["webpage"]["frecuency_format"] == ""):
                        for departure in dates:
                            output_HTML = createURL(conf_file, origin_city, destination_city, departure)
                            travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city)
                    else:
                        output_HTML = createURL(conf_file, origin_city, destination_city, datetime.today().date())
                        travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city)
    elif(page_type == 2): #Javascript type pages
        for origin_city in cities:
            for destination_city in cities:
                if(origin_city.id != destination_city.id):
                    if(conf_file["webpage"]["frecuency_format"] == ""):
                        for departure in dates:
                            output_HTML = executeJavaScript(conf_file, origin_city, destination_city, departure)
                            travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city)
                    else:
                        output_HTML = output_HTML = executeJavaScript(conf_file, origin_city, destination_city, datetime.today().date())
                        travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city)
    elif(page_type == 3): #Simple type pages
        origin_cities = []
        destination_cities = []
        HTML_blocks = []
        extractBlocks(conf_file, origin_cities, destination_cities, HTML_blocks)
        for block in HTML_blocks:
            travels += extractData(conf_file, block, origin_cities[counter], destination_cities[counter])

        print origin_cities
        print "\n"
        print destination_cities
        print "\n"
        print HTML_blocks

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
    origin_country = Country.objects.filter(id = origin_city.country)[0]
    destination_country = Country.objects.filter(id = destination_city.country)[0]
    for line in conf_file["webpage"]["header_parameters"]["parameters"]:
        url += line["parameter"]
        data = str(line["data"])
        #CASE for each posible value of the "data" attribute of the configuration file
        if(data == "origin_country"):
            url += origin_country.name
        elif(data == "destination_country"):
            url += destination_country.name
        elif(data == "origin_country_alias"):
            url += str(origin_city.country)
        elif(data == "destination_country_alias"):
            url += str(destination_city.country)
        elif(data == "origin_city"):
            url += str(origin_city.name)
        elif(data == "destination_city"):
            url += str(destination_city.name)
        elif(data == "origin_alias"):
            url += str(origin_city.alias_flight)
        elif(data == "destination_alias"):
            url += str(destination_city.alias_flight)
        elif(data == "departure"):
            url += departure.strftime(date_format)
        elif(data == "actual_date"):
            today = datetime.today().date()
            url += today.strftime(date_format)

        if(counter < total_parameters - 1):
            url += separator
        counter += 1

    url += conf_file["webpage"]["uri_end"]
    phantom = webdriver.PhantomJS()
    phantom.get(url)
    time.sleep(conf_file["webpage"]["sleep_time"])
    soup = BeautifulSoup(phantom.page_source, "html.parser")
    return soup

def executeJavaScript(conf_file, origin_city, destination_city, departure):
    #TODO: ejecutar el javascript de la pagina usando del archivo de configuracion, ciudad de origen,
    #ciudad de destino y fecha de partida
    return ""

def extractBlocks(conf_file, origin_cities, destination_cities, HTML_blocks):
    phantom = webdriver.PhantomJS()
    phantom.get(conf_file["webpage"]["uri_start"])
    time.sleep(conf_file["webpage"]["sleep_time"])
    soup = BeautifulSoup(phantom.page_source, "html.parser")

    HTML_blocks = [soup]
    aux_origin_cities = [soup]
    aux_destination_cities = [soup]

    #We extract the travel blocks
    for tag in conf_file["webpage"]["iterators"]["travel_block"]:
        sub_blocks = []
        for block in HTML_blocks:
            if((tag["field_type"] == "") and ("position" not in tag)):
                sub_blocks += block.find_all(tag["tag_type"])
            elif((tag["field_type"] == "") and ("position" in tag)):
                sub_blocks += block.find_all(tag["tag_type"])[tag["position"]]
            elif(tag["field_type"] != "") and ("position" not in tag):
                sub_blocks += soup.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
            elif(tag["field_type"] != "") and ("position" in tag):
                sub_blocks += soup.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})[tag["position"]]
        HTML_blocks = sub_blocks[:]

    #We extract the origin city of each travel block
    for tag in conf_file["webpage"]["iterators"]["origin_city"]["fields"]:
        sub_blocks = []
        for block in aux_origin_cities:
            if((tag["field_type"] == "") and ("position" not in tag)):
                sub_blocks += block.find_all(tag["tag_type"])
            elif((tag["field_type"] == "") and ("position" in tag)):
                sub_blocks += block.find_all(tag["tag_type"])[tag["position"]]
            elif(tag["field_type"] != "") and ("position" not in tag):
                sub_blocks += soup.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
            elif(tag["field_type"] != "") and ("position" in tag):
                sub_blocks += soup.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})[tag["position"]]
        aux_origin_cities = sub_blocks[:]

    for aux_origin_city in aux_origin_cities:
        if (aux_origin_city != "\n"):
            origin_cities += [unidecode(aux_origin_city.getText())]

    #We extract the destination city of each travel block
    for tag in conf_file["webpage"]["iterators"]["destination_city"]["fields"]:
        sub_blocks = []
        for block in aux_destination_cities:
            if((tag["field_type"] == "") and ("position" not in tag)):
                sub_blocks += block.find_all(tag["tag_type"])
            elif((tag["field_type"] == "") and ("position" in tag)):
                sub_blocks += block.find_all(tag["tag_type"])[tag["position"]]
            elif(tag["field_type"] != "") and ("position" not in tag):
                sub_blocks += soup.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
            elif(tag["field_type"] != "") and ("position" in tag):
                sub_blocks += soup.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})[tag["position"]]
        aux_destination_cities = sub_blocks[:]

    for aux_destination_city in aux_destination_cities:
        if (aux_destination_city != "\n"):
            destination_cities += [unidecode(aux_destination_city.getText())]

    print explosion[900]

def extractData(conf_file, html_file, origin_city, destination_city):
    #TODO: extraer los datos del HTML con el archivo de configuracion, transformarlos en instancias de
    #Travel y devolverlos
    return []
