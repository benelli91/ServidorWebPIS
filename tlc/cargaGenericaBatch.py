from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import bs4
from bs4 import BeautifulSoup
from datetime import datetime,timedelta,tzinfo
from .models import *
import time
import sys
import os
import json
from django.db import transaction
import unicodedata
from citiesDistanceMatrix import DISTANCE_MATRIX
from parameterOptions import *
import re
import calendar

DEFAULT_SPAN = 30
TRIPLE_QUOTES = '\"\"\"'

def timedGenericLoader():
    config_directory = 'tlc/config_files/'
    raw_files = [pos_json for pos_json in os.listdir(config_directory) if pos_json.endswith('.json')]
    files = []
    for conf_file in raw_files:
        with open(config_directory + conf_file) as data_file:
            files += [json.load(data_file)]

    timers = []
    for f in files:
        t = Timer(f["webpage"]["reload_time"]*3600, loadWebpage(f))
        t.start()
        timers += [t]

    while True:
        for t in timers:
            if not t.is_alive():
                t.start()

def genericLoader():
    config_directory = 'tlc/config_files/'
    raw_files = [pos_json for pos_json in os.listdir(config_directory) if pos_json.endswith('.json')]
    for conf_file in raw_files:
        with open(config_directory + conf_file) as data_file:
            data = json.load(data_file)
        loadWebpage(data)

def BuquebusLoader():
    config_directory = 'tlc/config_files/'
    with open(config_directory + "Buquebus.json") as data_file:
        data = json.load(data_file)
        loadWebpage(data)

def GoogleFlightsLoader():
    config_directory = 'tlc/config_files/'
    with open(config_directory + "GoogleFlights.json") as data_file:
        data = json.load(data_file)
        loadWebpage(data)

def CopayLoader():
    config_directory = 'tlc/config_files/'
    with open(config_directory + "Copay.json") as data_file:
        data = json.load(data_file)
        loadWebpage(data)

def TresCrucesLoader():
    config_directory = 'tlc/config_files/'
    with open(config_directory + "TresCruces.json") as data_file:
        data = json.load(data_file)
        loadWebpage(data)

def AgenciaCentralLoader():
    config_directory = 'tlc/config_files/'
    with open(config_directory + "AgenciaCentral.json") as data_file:
        data = json.load(data_file)
        loadWebpage(data)

def ColoniaExpressLoader():
    config_directory = 'tlc/config_files/'
    with open(config_directory + "ColoniaExpress.json") as data_file:
        data = json.load(data_file)
        loadWebpage(data)

def loadWebpage(conf_file):
    webpage_name = conf_file["webpage"]["name"]
    phantom = webdriver.Firefox()

    aux_cities = []
    cities = []

    config_directory = 'tlc/local_city_codes/'
    raw_files = [pos_json for pos_json in os.listdir(config_directory) if pos_json.endswith('.json')]
    for files in raw_files:
        with open(config_directory + files) as data_file:
            data = json.load(data_file)
            if(data["name"] == webpage_name):
                local_codes = data

    if(conf_file["webpage"]["travel_type"] == 1):
        aux_cities = City.objects.filter(airport = True)
    elif(conf_file["webpage"]["travel_type"] == 2):
        aux_cities = City.objects.filter(port = True)
    elif(conf_file["webpage"]["travel_type"] == 3):
        aux_cities = City.objects.filter(bus_station = True)

    for city in aux_cities:
        if(city.name in local_codes["codes"]):
            cities += [city]

    cities = aux_cities
    if(conf_file["webpage"]["date_span_start"] >= conf_file["webpage"]["date_span_finish"]):
        span = DEFAULT_SPAN
    else:
        span = conf_file["webpage"]["date_span_finish"] - conf_file["webpage"]["date_span_start"]
    dates = [datetime.today().date() + timedelta(days=conf_file["webpage"]["date_span_start"])]

    for i in range(1, span):
        dates.append(dates[-1] + timedelta(days=1))
    #print dates

    travels = []
    url = conf_file["webpage"]["uri_start"]
    page_type = conf_file["webpage"]["page_type"]

    if(page_type == 1): #URL type pages
        for origin_city in cities:
            for destination_city in cities:
                if(origin_city.id != destination_city.id):
                    if(conf_file["webpage"]["frequency_format"] == []):
                        for departure in dates:
                            output_HTML = createURL(conf_file, origin_city, destination_city, departure, phantom)
                            travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city,departure,dates)
                    else:
                        output_HTML = createURL(conf_file, origin_city, destination_city, datetime.today().date(), phantom)
                        travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city, datetime.today().date(), dates)

    elif(page_type == 2): #Javascript type pages
        for origin_city in cities:
            for destination_city in cities:
                if(origin_city.id != destination_city.id):
                    if(conf_file["webpage"]["frequency_format"] == []):
                        for departure in dates:
                            output_HTML = executeJavaScript(conf_file, origin_city, destination_city, departure, phantom)
                            travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city, departure, dates)
                    else:
                        output_HTML = executeJavaScript(conf_file, origin_city, destination_city, datetime.today().date(), phantom)
                        travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city, datetime.today().date(), dates)
                    #print output_HTML
    elif(page_type == 3): #Simple type pages
        origin_cities = []
        destination_cities = []
        HTML_blocks = extractBlocks(conf_file, origin_cities, destination_cities, phantom)
        #print len(origin_cities)
        #print len(destination_cities)
        #print len(HTML_blocks)
        block_number = 0
        for block in HTML_blocks:
            counter = 0
            counter_o = -1
            counter_d = -1
            for city in cities:
                if(city.name.lower() == origin_cities[block_number].lower()):
                    counter_o = counter
                if(city.name.lower() == destination_cities[block_number].lower()):
                    counter_d = counter
                counter += 1
            if(counter_o != -1 and counter_d != -1):
                travels += extractData(conf_file, block, cities[counter_o], cities[counter_d], datetime.today().date(), dates)
            block_number += 1

    """with transaction.atomic():
        Travel.objects.filter(webpage = webpage_name).delete()
        for travel in travels:
            travel.save()"""

    if len(travels) > 0 :
        if conf_file["webpage"]["extraction_tags"]["travel_agency"]["format"] != "":
            travel_agency_to_delete = Travelagency.objects.get(name=conf_file["webpage"]["extraction_tags"]["travel_agency"]["format"])
            to_delete = Travel.objects.filter(travel_agency = travel_agency_to_delete.id)
            to_delete.delete()
        for travel in travels:
            #print travel.idtravel
            travel.save()
    #else:
        #print 'no hay nadie pariente'

    phantom.quit()

def createURL(conf_file, origin_city, destination_city, departure, phantom):
    #TODO: generar la URL de la que extraer los datos dados el archivo de configuracion, ciudad de origen,
    #ciudad de destino y fecha de partida
    url = conf_file["webpage"]["uri_start"]
    separator = conf_file["webpage"]["header_parameters"]["separator"]
    total_parameters = len(conf_file["webpage"]["header_parameters"]["parameters"])
    counter = 0
    origin_country = Country.objects.filter(id = origin_city.country)[0]
    destination_country = Country.objects.filter(id = destination_city.country)[0]
    for line in conf_file["webpage"]["header_parameters"]["parameters"]:
        url += line["parameter"]
        url += dataParameterOptions(line, conf_file, origin_city, destination_city, departure)
        if(counter < total_parameters - 1):
            url += separator
        counter += 1

    url += conf_file["webpage"]["uri_end"]
    #print url
    phantom.get(url)
    aux_sleep =conf_file["webpage"]["sleep_time"]
    time.sleep(aux_sleep)
    soup = BeautifulSoup(phantom.page_source, "html.parser")
    return soup

def executeJavaScript(conf_file, origin_city, destination_city, departure, phantom):
    #TODO: ejecutar el javascript de la pagina usando del archivo de configuracion, ciudad de origen,
    #ciudad de destino y fecha de partida
    phantom.get(conf_file["webpage"]["uri_start"])
    time.sleep(conf_file["webpage"]["sleep_time"])
    for line in conf_file["webpage"]["inputs"]["buttons"]:
        data = dataParameterOptions(line, conf_file, origin_city, destination_city, departure)
        if(data == "invalid"):
            return ""
        if line["field_type"] == "select":
            element = Select(javascriptParameterOptions(line, phantom))
            options = []
            for option in element.options:
                options += [option.text]
            if data in options:
                element.select_by_visible_text(data)
            else:
                return ""
        elif line["field_type"] == "input":
            element = javascriptParameterOptions(line, phantom)
            if data == "click":
                element.click()
            else:
                element.clear()
                element.send_keys(data)
        elif line["field_type"] == "script":
            fun = line["id"] + data
            phantom.execute_script(fun)
        elif line["field_type"] == "attribute": #ESTA ES LA PARTE QUE NO FUNCIONA
            element = javascriptParameterOptions(line, phantom)
            attribute = line["attribute"]
            fun = "arguments[0].setAttribute('" + attribute + "', arguments[1]);"
            phantom.execute_script(fun, element, data)
            #print phantom.page_source

        time.sleep(conf_file["webpage"]["inputs"]["wait"])
    time.sleep(conf_file["webpage"]["inputs"]["loading_time"])
    output_HTML = BeautifulSoup(phantom.page_source, "html.parser")
    #print output_HTML
    return output_HTML

def extractBlocks(conf_file, origin_cities, destination_cities, phantom):
    phantom.get(conf_file["webpage"]["uri_start"])
    time.sleep(conf_file["webpage"]["sleep_time"])
    HTML_blocks = BeautifulSoup(phantom.page_source, "html.parser")

    #We extract the travel blocks
    raw_blocks = get_data_list(conf_file["webpage"]["iterators"]["travel_block"], HTML_blocks, False)
    aux_blocks = []
    for block in raw_blocks:
        aux_blocks += [[block, "", ""]]

    for aux_sub_block in aux_blocks:
        #We extract the origin city of each travel block
        aux_origin_cities = get_data_list(conf_file["webpage"]["iterators"]["origin_city"], aux_sub_block[0], True)
        for aux_origin_city in aux_origin_cities:
            aux_sub_block[1] = [aux_origin_city]

        #We extract the destination city of each travel block
        aux_destination_cities = get_data_list(conf_file["webpage"]["iterators"]["destination_city"], aux_sub_block[0], True)
        for aux_destination_city in aux_destination_cities:
            aux_sub_block[2] = [aux_destination_city]

    result = []
    for block in aux_blocks:
        if(block[1] != "" and block[2] != ""):
            result += [block[0]]
            origin_cities += block[1]
            destination_cities += block[2]
    return result

def extractData(conf_file, html_file, origin_city, destination_city,departure,dates):
    #TODO: extraer los datos del HTML con el archivo de configuracion, transformarlos en instancias de
    #Travel y devolverlos
    travels_to_add = []
    departure_list = []
    duration_list = []
    arrival_list = []
    price_list = []
    travel_agency_list = []
    frequency_list = []
    UTC = conf_file["webpage"]["UTC"]
    STATUS = origin_city.name.upper() +'-'+destination_city.name.upper()
    #print '------', STATUS
    departure_with_time = datetime(year=departure.year,month=departure.month,day=departure.day)
    number_traveltype = int(conf_file["webpage"]["travel_type"])
    page_traveltype = Traveltype.objects.get(traveltype = number_traveltype)
    #departure extraction_tags
    departure_fields = conf_file["webpage"]["extraction_tags"]["departure"]["fields"]
    departure_format = conf_file["webpage"]["extraction_tags"]["departure"]["format"]
    departure_formula = conf_file["webpage"]["extraction_tags"]["departure"]["formula"]
    #print 'departure'
    departure_list = get_data_list(departure_fields,html_file, True)
    #departure_list = get_data_list2(arrival_fields,html_file, True,STATUS)
    #for q in departure_list:
    #    print q

    #arrival extraction_tags
    arrival_fields = conf_file["webpage"]["extraction_tags"]["arrival"]["fields"]
    arrival_format = conf_file["webpage"]["extraction_tags"]["arrival"]["format"]
    arrival_formula = conf_file["webpage"]["extraction_tags"]["arrival"]["formula"]
    if arrival_fields != []:
        #print ('arrival')
        arrival_list = get_data_list(arrival_fields,html_file, True)
        #for q in arrival_list:
        #    print q
    #price extraction_tags
    price_fields = conf_file["webpage"]["extraction_tags"]["price"]["fields"]
    price_format = conf_file["webpage"]["extraction_tags"]["price"]["format"]
    price_formula = conf_file["webpage"]["extraction_tags"]["price"]["formula"]
    price_list = get_data_list(price_fields,html_file, True)

    #duration extraction_tags

    duration_fields = conf_file["webpage"]["extraction_tags"]["duration"]["fields"]
    duration_format = conf_file["webpage"]["extraction_tags"]["duration"]["format"]
    duration_formula = conf_file["webpage"]["extraction_tags"]["duration"]["formula"]
    if duration_fields != []:
        duration_list = get_data_list(duration_fields,html_file, True)

    #travel_agency extraction_tags

    travel_agency_fields = conf_file["webpage"]["extraction_tags"]["travel_agency"]["fields"]
    travel_agency_format = conf_file["webpage"]["extraction_tags"]["travel_agency"]["format"]
    travel_agency_formula = conf_file["webpage"]["extraction_tags"]["travel_agency"]["formula"]
    if travel_agency_fields != []:
        travel_agency_list = get_data_list(travel_agency_fields,html_file, True)

    #frequency extraction_tags

    frequency_fields = conf_file["webpage"]["extraction_tags"]["frequency"]["fields"]
    frequency_format = conf_file["webpage"]["extraction_tags"]["frequency"]["format"]
    frequency_formula = conf_file["webpage"]["extraction_tags"]["frequency"]["formula"]
    if frequency_format != []:
        frequency_list = get_data_list(frequency_fields,html_file, True)

    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    #||Ver que pasa si las listas tienen distinta cantidad de elementos||
    #||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    for x in range(len(departure_list)):
        new_travel_departure = ''
        new_travel_arrival = ''
        new_travel_duration = None
        new_travel_price = ''
        new_travel_agency = ''
        aux_new_travel_duration = departure_with_time

        #Extract departure
        str_departure = departure_list[x]
        result_format = processRawText(conf_file,str_departure,departure_format,departure_formula,origin_city,destination_city)
        if len(result_format) == 0 :
            new_travel_departure = None
        else:
            new_travel_departure = departure_with_time + timedelta(hours=int(result_format[0]) + UTC, minutes = int(result_format[1]), seconds = 0)

        #Extract or calculate duration
        if duration_list != [] : #if I have duration data then I extract it
            str_duration = duration_list[x]
            result_format = processRawText(conf_file,str_duration,duration_format,duration_formula,origin_city,destination_city)
            if len(result_format) == 0 :
                new_travel_duration = None
            else:
                new_travel_duration =  int(result_format[0]) * 60 + int(result_format[1])
        else: #otherwise calculate
            str_arrival = arrival_list[x]
            result_format = processRawText(conf_file,str_arrival,arrival_format,arrival_formula,origin_city,destination_city)
            if len(result_format) == 0 :
                aux_new_travel_duration = None
            else:
                new_travel_arrival = departure_with_time + timedelta(hours=int(result_format[0]) + UTC, minutes = int(result_format[1]), seconds = 0)
                if new_travel_arrival < new_travel_departure:
                    new_travel_arrival = new_travel_arrival + timedelta(days = 1)
                aux_new_travel_duration = new_travel_arrival - new_travel_departure

            if aux_new_travel_duration != None: #convert timedelta in minutes
                new_travel_duration = aux_new_travel_duration.seconds // 60
        #Extract price
        #the format must be (non digit or empty) (all digits price's) (non digit or empty)
        if price_formula != "":
            str_price = '0'
        else:
            str_price = price_list[x]
        result_format = processRawText(conf_file,str_price,price_format,price_formula,origin_city,destination_city)
        if len(result_format) == 0 :
            new_travel_price = None
        else:
            new_travel_price = str(result_format[0])

        #Extract travel_agency
        if travel_agency_list != []: #from HTML
            new_travel_agency = Travelagency.objects.get(name=travel_agency_list[x])
        else: #from json
            new_travel_agency  = Travelagency.objects.get(name=travel_agency_format)

        #if none of the data fields are empty, then create the travel object
        if new_travel_departure != None and new_travel_duration != None and new_travel_price != None and str(new_travel_price) != '0' and str(new_travel_price) != '' and str(new_travel_agency) != '' :
        #if str(new_travel_departure) != '' and str(new_travel_duration) != '' and str(new_travel_price) != '0' and str(new_travel_price) != '' and str(new_travel_agency) != '' :
            if conf_file["webpage"]["frequency_format"] == []: #if the departure does not depend on the days of the week
                new_travel = Travel(departure = new_travel_departure, \
                                        origin_city = origin_city, \
                                        destination_city = destination_city, \
                                        price = new_travel_price, \
                                        duration = new_travel_duration, \
                                        traveltype = page_traveltype, \
                                        webpage = new_travel_agency.reference, \
                                        travel_agency = new_travel_agency.id, \
                                        description = '')
                #add the travel to result list
                travels_to_add[len(travels_to_add):] = [new_travel]
            else: #otherwise check the frequency in the dates span
                for date in dates:#para cada fecha en el rengo de consulta, si la fecha pertenece a la frecuencia, creo el travel
                    #print date.weekday,1
                    if verifyFrequency(conf_file,date,frequency_list[x]):
                        #print date.weekday,2
                        #print('TAMO RE ACTIVO')
                        departure_with_time = datetime(year=date.year,month=date.month,day=date.day)
                        result_format = processRawText(conf_file,str_departure,departure_format,departure_formula,origin_city,destination_city)
                        new_travel_departure = departure_with_time + timedelta(hours=int(result_format[0]), minutes = int(result_format[1]), seconds = 0)
                        """print "departure"
                        print new_travel_departure
                        print "origen"
                        print origin_city.name
                        print "destino"
                        print destination_city.name
                        print "precio"
                        print new_travel_price
                        print "duracion"
                        print new_travel_duration
                        print "travel type"
                        print page_traveltype
                        print "webpage"
                        print new_travel_agency.reference
                        print "agencia"
                        print new_travel_agency.id"""
                        new_travel = Travel(departure = new_travel_departure, \
                                                origin_city = origin_city, \
                                                destination_city = destination_city, \
                                                price = new_travel_price, \
                                                duration = new_travel_duration, \
                                                traveltype = page_traveltype, \
                                                webpage = new_travel_agency.reference, \
                                                travel_agency = new_travel_agency.id, \
                                                description = '')

                        travels_to_add[len(travels_to_add):] = [new_travel]

    return travels_to_add

def get_data_list(fields_list,html_file, get_text):
    HTML_blocks = [html_file]
    for tag in fields_list:
        sub_blocks = []
        for block in HTML_blocks:
            if block != "\n":
                if((tag["field_type"] == "") and ("position" not in tag)):
                    sub_blocks += block.find_all(tag["tag_type"])
                elif((tag["field_type"] == "") and ("position" in tag)):
                    if tag["position"] < 0:
                        if(len(block.find_all(tag["tag_type"])) + tag["position"] >= 0):
                            sub_blocks += block.find_all(tag["tag_type"])[len(block.find_all(tag["tag_type"])) + tag["position"]]
                    elif len(block.find_all(tag["tag_type"])) > tag["position"]:
                        aux_block = block.find_all(tag["tag_type"])
                        sub_blocks += aux_block[tag["position"]]
                elif(tag["field_type"] != "") and ("position" not in tag):
                    sub_blocks += block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
                elif(tag["field_type"] != "") and ("position" in tag):
                    if tag["position"] < 0:
                        if(len(block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})) + tag["position"] >= 0):
                            aux_block = block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
                            sub_blocks += [aux_block[len(aux_block) + tag["position"]]]
                    elif len(block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})) > tag["position"]:
                        aux_block = block.find_all(tag["tag_type"],{tag["field_type"]: tag["name"]})
                        sub_blocks += [aux_block[tag["position"]]]
        HTML_blocks = sub_blocks[:]

    result = []
    for block in HTML_blocks:
        if(block != "\n"):
            if(get_text == True):
                if not isinstance(block, bs4.element.NavigableString):
                    raw_text = block.getText()
                    result += [str(unicodedata.normalize('NFKD', raw_text).encode('ascii','ignore'))]
                else:
                    result += [str(block.encode('ascii','ignore'))]
            else:
                result += [block]
    return result

def processRawText(conf_file, raw_text, raw_format, raw_formula, origin_city, destination_city):
    output_text = []
    raw_format_aux = str.replace(unicodedata.normalize('NFKD', raw_format).encode('ascii','ignore'), "\\\\", "\\")
    raw_formula_aux = unicodedata.normalize('NFKD', raw_formula).encode('ascii','ignore')
    decimal = unicodedata.normalize('NFKD', conf_file["webpage"]["decimal_mark"]).encode('ascii','ignore')
    thousands = unicodedata.normalize('NFKD', conf_file["webpage"]["thousands_mark"]).encode('ascii','ignore')
    raw_text_aux = raw_text
    raw_text_aux = str.replace(raw_text_aux, str(thousands), "")
    raw_text_aux = str.replace(raw_text_aux, decimal, ".")
    if(raw_format_aux == ""):   #if there's no format specified we return the given text without modifications
        output_text = [raw_text_aux]
    elif(raw_formula_aux == ""):
        #if(re.search("\(", raw_format)):    #if there's a regular expression as format and no formula we parse it and return the result
        matches = re.search(raw_format_aux, raw_text_aux)
        if matches != None:
            for i in range(1, len(matches.groups()) + 1):
                output_text += [matches.group(i)]
        #else:   #if there's a constant as format we return the constant
        #    output_text = [raw_format_aux]
    else:
        if(raw_format_aux == "city_distance"):  #if we find the special format city_distance we calculate it and return it
            final_formula = str.replace(raw_formula_aux, "city_distance", str(DISTANCE_MATRIX[origin_city.id][destination_city.id]))
            #print final_formula,'formula'
            exec(final_formula)
            output_text = str(round(x, 0))
        else:   #if there's a format and a formula we retrieve the data and execute the formula
            matches = re.search(raw_format_aux, raw_text_aux)
            final_formula = raw_formula_aux
            for i in range(1, len(matches.groups()) + 1):
                final_formula = str.replace(final_formula, "$" + str(i), matches.group(i))
            exec(final_formula)
            for i in x:
                output_text += [str(round(i, 2))]

    return output_text

def verifyFrequency(conf_file,date,frequency_data):
    #TODO funcion que retorne un boolean dependiendo si la fecha es una fecha de la frecuencia o no
    if(len(conf_file["webpage"]["frequency_format"]) == 10):
        frequencies = frequency_data.split(conf_file["webpage"]["frequency_format"][9])
        daily = conf_file["webpage"]["frequency_format"][7]
        span = conf_file["webpage"]["frequency_format"][8]
        for raw_freq in frequencies:
            freq = unicodedata.normalize('NFKD', raw_freq).encode('ascii','ignore')
            if(re.search(daily, freq)):
                return True
            elif(re.search(conf_file["webpage"]["frequency_format"][date.weekday()], freq)):
                return True
            elif(re.search(span, freq)):
                matches = re.search("(.+)" + span + "(.+)", freq)
                counter = 0
                beginning_day = -1
                end_day = -1
                for i in range(0, 6):
                    if(re.search(conf_file["webpage"]["frequency_format"][counter], matches.group(1))):
                        beginning_day = counter
                    if(re.search(conf_file["webpage"]["frequency_format"][counter], matches.group(2))):
                        end_day = counter
                    counter += 1
                if((beginning_day < end_day) and (date.weekday() > beginning_day) and (date.weekday() < end_day)):
                    return True
                if((beginning_day > end_day) and ((date.weekday() > beginning_day) or (date.weekday() < end_day))):
                    return True
    return False
