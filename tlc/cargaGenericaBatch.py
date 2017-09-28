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
import unicodedata

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
    aux_origin_cities = [BeautifulSoup(phantom.page_source, "html.parser")]
    aux_destination_cities = [BeautifulSoup(phantom.page_source, "html.parser")]
    HTML_blocks = [BeautifulSoup(phantom.page_source, "html.parser")]

    #We extract the travel blocks
    for tag in conf_file["webpage"]["iterators"]["travel_block"]:
        sub_blocks = []
        for block in HTML_blocks:
            if block != "\n":
                if((tag["field_type"] == "") and ("position" not in tag)):
                    sub_blocks += block.find_all(tag["tag_type"])
                elif((tag["field_type"] == "") and ("position" in tag)):
                    if len(block.find_all(tag["tag_type"])) > tag["position"]:
                        sub_blocks += block.find_all(tag["tag_type"])[tag["position"]]
                elif(tag["field_type"] != "") and ("position" not in tag):
                    sub_blocks += block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
                elif(tag["field_type"] != "") and ("position" in tag):
                    if len(block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})) > tag["position"]:
                        sub_blocks += block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})[tag["position"]]
        HTML_blocks = sub_blocks[:]

    #We extract the origin city of each travel block
    for tag in conf_file["webpage"]["iterators"]["origin_city"]["fields"]:
        sub_blocks = []
        for block in aux_origin_cities:
            if block != "\n":
                if((tag["field_type"] == "") and ("position" not in tag)):
                    sub_blocks += block.find_all(tag["tag_type"])
                elif((tag["field_type"] == "") and ("position" in tag)):
                    if len(block.find_all(tag["tag_type"])) > tag["position"]:
                        sub_blocks += block.find_all(tag["tag_type"])[tag["position"]]
                elif(tag["field_type"] != "") and ("position" not in tag):
                    sub_blocks += block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
                elif(tag["field_type"] != "") and ("position" in tag):
                    if len(block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})) > tag["position"]:
                        sub_blocks += block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})[tag["position"]]
        aux_origin_cities = sub_blocks[:]

    for aux_origin_city in aux_origin_cities:
        if (aux_origin_city != "\n"):
            raw_text = aux_origin_city.getText()
            origin_cities += [unicodedata.normalize('NFKD', raw_text).encode('ascii','ignore')]

    #We extract the destination city of each travel block
    for tag in conf_file["webpage"]["iterators"]["destination_city"]["fields"]:
        sub_blocks = []
        for block in aux_destination_cities:
            if block != "\n":
                if((tag["field_type"] == "") and ("position" not in tag)):
                    sub_blocks += block.find_all(tag["tag_type"])
                elif((tag["field_type"] == "") and ("position" in tag)):
                    if len(block.find_all(tag["tag_type"])) > tag["position"]:
                        sub_blocks += block.find_all(tag["tag_type"])[tag["position"]]
                elif(tag["field_type"] != "") and ("position" not in tag):
                    sub_blocks += block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
                elif(tag["field_type"] != "") and ("position" in tag):
                    if len(block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})) > tag["position"]:
                        sub_blocks += block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})[tag["position"]]
        aux_destination_cities = sub_blocks[:]

    for aux_destination_city in aux_destination_cities:
        if (aux_destination_city != "\n"):
            raw_text = aux_destination_city.getText()
            destination_cities += [unicodedata.normalize('NFKD', raw_text).encode('ascii','ignore')]

def extractData(conf_file, html_file, origin_city, destination_city):
    #TODO: extraer los datos del HTML con el archivo de configuracion, transformarlos en instancias de
    #Travel y devolverlos

    if(conf_file["webpage"]["simple_page"] == False):
        #departure extraction_tags
        departure_fields = conf_file["webpage"]["extraction_tags"]["departure"]["fields"]
        departure_format = conf_file["webpage"]["extraction_tags"]["departure"]["format"]
        departure_formula = conf_file["webpage"]["extraction_tags"]["departure"]["formula"]
        #price extraction_tags
        price_fields = conf_file["webpage"]["extraction_tags"]["price"]["fields"]
        price_format = conf_file["webpage"]["extraction_tags"]["price"]["format"]
        price_formula = conf_file["webpage"]["extraction_tags"]["price"]["formula"]
        #duration extraction_tags
        duration_fields = conf_file["webpage"]["extraction_tags"]["duration"]["fields"]
        duration_format = conf_file["webpage"]["extraction_tags"]["duration"]["format"]
        duration_formula = conf_file["webpage"]["extraction_tags"]["duration"]["formula"]
        #travel_agency extraction_tags
        travel_agency_fields = conf_file["webpage"]["extraction_tags"]["travel_agency"]["fields"]
        travel_agency_format = conf_file["webpage"]["extraction_tags"]["travel_agency"]["format"]
        travel_agency_formula = conf_file["webpage"]["extraction_tags"]["travel_agency"]["formula"]
        #frequency extraction_tags
        frequency_agency_fields = conf_file["webpage"]["extraction_tags"]["frequency"]["fields"]
        frequency_agency_format = conf_file["webpage"]["extraction_tags"]["frequency"]["format"]
        frequency_agency_formula = conf_file["webpage"]["extraction_tags"]["frequency"]["formula"]

        departure_list = get_data_list(departure_fields,html_file)
        price_list = get_data_list(price_fields,html_file)
        duration_list = get_data_list(duration_fields,html_file)
        travel_agency_list = get_data_list(travel_agency_fields,html_file)
        frequency_agency_list = get_data_list(frequency_agency_fields,html_file)

        for xx in range(len(departure_list)):
            print departure_list[xx]
            print price_list[xx].contents
            #print duration_list[xx].contents
            #print travel_agency_list[xx].contents
            #print frequency_agency_list[xx]
    else:
        a = 1
    return []

def get_data_list(fields_list,html_file):
    #print html_file
    result = None
    aux_html = html_file
    first = True
    for item in fields_list: #for each item in the field list in the config_file
        if not first: #the first time i have the defaul value in "html_file"
            aux_html = result #In the following times I have to work with the previous result
        first = False

        find_tag = ''
        find_field = ''
        find_name  = ''
        find_position = 999999999999 #invalid position value
        #check if the item in the config_file has the tag
        if item.has_key("tag_type"):
            find_tag = item["tag_type"]
        if item.has_key("field_type"):
            find_field = item["field_type"]
        if item.has_key("name"):
            find_name = item["name"]
        if item.has_key("position"):
            find_position = item["position"]

        if find_position != 999999999999: #if i need to find a particular child
            text_result = ''
            for child in aux_html:
                soup = BeautifulSoup(TRIPLE_QUOTES + str(child) + TRIPLE_QUOTES,"html.parser")
                aux_result = soup.find_all(find_tag,{find_field:find_name})
                actual_position = 0
                for litle_child in aux_result:
                    if actual_position == find_position:
                        text_result += str(litle_child)
                    actual_position += 1
            result = BeautifulSoup(TRIPLE_QUOTES + text_result + TRIPLE_QUOTES,"html.parser").find_all()
        else:
            soup = BeautifulSoup(TRIPLE_QUOTES + str(aux_html) + TRIPLE_QUOTES,"html.parser")
            result =soup.find_all(find_tag,{find_field:find_name})
    return result
