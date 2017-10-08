from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.support.ui import Select
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
from dataParameterOptions import dataParameterOptions
import re
import calendar

DEFAULT_SPAN = 30
TRIPLE_QUOTES = '\"\"\"'


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
    with open(config_directory + "GoogleFlights.json") as data_file:
        data = json.load(data_file)
        loadWebpage(data)

def ColoniaExpressLoader():
    config_directory = 'tlc/config_files/'
    with open(config_directory + "ColoniaExpress.json") as data_file:
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

    if(conf_file["webpage"]["date_span_start"] >= conf_file["webpage"]["date_span_finish"]):
        span = DEFAULT_SPAN
    else:
        span = conf_file["webpage"]["date_span_finish"] - conf_file["webpage"]["date_span_start"]
    dates = [datetime.today().date() + timedelta(days=conf_file["webpage"]["date_span_start"])]

    for i in range(1, span):
        dates.append(dates[-1] + timedelta(days=1))
    print dates

    travels = []
    url = conf_file["webpage"]["uri_start"]
    page_type = conf_file["webpage"]["page_type"]

    if(page_type == 1): #URL type pages
        for origin_city in cities:
            for destination_city in cities:
                if(origin_city.id != destination_city.id):
                    if(conf_file["webpage"]["frequency_format"] == []):
                        for departure in dates:
                            output_HTML = createURL(conf_file, origin_city, destination_city, departure)
                            travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city,departure,dates)
                    else:
                        output_HTML = createURL(conf_file, origin_city, destination_city, datetime.today().date())
                        travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city, datetime.today().date(), dates)

    elif(page_type == 2): #Javascript type pages
        for origin_city in cities:
            for destination_city in cities:
                if(origin_city.id != destination_city.id):
                    if(conf_file["webpage"]["frequency_format"] == []):
                        for departure in dates:
                            output_HTML = executeJavaScript(conf_file, origin_city, destination_city, departure)
                            travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city, departure, dates)
                    else:
                        output_HTML = executeJavaScript(conf_file, origin_city, destination_city, datetime.today().date())
                        travels = travels + extractData(conf_file, output_HTML, origin_city, destination_city, datetime.today().date(), dates)
                    print output_HTML
    elif(page_type == 3): #Simple type pages
        origin_cities = []
        destination_cities = []
        HTML_blocks = extractBlocks(conf_file, origin_cities, destination_cities)
        print len(origin_cities)
        print len(destination_cities)
        print len(HTML_blocks)
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
            print travel.idtravel
            travel.save()

def createURL(conf_file, origin_city, destination_city, departure):
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
    print url
    phantom = webdriver.PhantomJS()
    phantom.get(url)
    aux_sleep =conf_file["webpage"]["sleep_time"]
    time.sleep(aux_sleep)
    soup = BeautifulSoup(phantom.page_source, "html.parser")
    return soup

def executeJavaScript(conf_file, origin_city, destination_city, departure):
    #TODO: ejecutar el javascript de la pagina usando del archivo de configuracion, ciudad de origen,
    #ciudad de destino y fecha de partida
    phantom = webdriver.PhantomJS()
    phantom.get(conf_file["webpage"]["uri_start"])
    time.sleep(conf_file["webpage"]["sleep_time"])
    for line in conf_file["webpage"]["inputs"]["buttons"]:
        data = dataParameterOptions(line, conf_file, origin_city, destination_city, departure)
        if(data[0] == "invalid"):
            return ""
        if line["field_type"] == "select":
            element = Select(phantom.find_element_by_id(line["id"]))
            options = []
            for option in element.options:
                options += [option.text]
            if data[0] in options:
                element.select_by_visible_text(data[0])
            else:
                return ""
        elif line["field_type"] == "input":
            element = phantom.find_element_by_id(line["id"])
            if data[0] == "click":
                element.click()
            else:
                element.send_keys(data[0])
        elif line["field_type"] == "script":
            fun = line["id"] + "("
            counter = 0
            for d in data:
                fun += "'" + d + "'"
                if(counter < len(data) - 1):
                    fun += ", "
                counter += 1
            fun += ");"
            phantom.execute_script(fun)
        elif line["field_type"] == "attribute": #ESTA ES LA PARTE QUE NO FUNCIONA
            elem = phantom.find_element_by_id(line["id"])
            print elem.get_attribute('data_date')
            attribute = line["attribute"]
            fun = "arguments[0]['" + attribute + "'] = arguments[1]; return arguments[0];"
            elem = phantom.execute_script(fun, elem, data[0])
            print elem.get_attribute('data_date')

        time.sleep(conf_file["webpage"]["inputs"]["wait"])
    output_HTML = BeautifulSoup(phantom.page_source, "html.parser")
    return output_HTML

def extractBlocks(conf_file, origin_cities, destination_cities):
    phantom = webdriver.PhantomJS()
    phantom.get(conf_file["webpage"]["uri_start"])
    time.sleep(conf_file["webpage"]["sleep_time"])
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

    aux_blocks = []
    for block in HTML_blocks:
        if(block != "\n"):
            aux_blocks += [[block, "", ""]]

    for aux_sub_block in aux_blocks:
        aux_origin_cities = [aux_sub_block[0]]
        aux_destination_cities = [aux_sub_block[0]]
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
                aux_sub_block[1] = [unicodedata.normalize('NFKD', raw_text).encode('ascii','ignore')]


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
                aux_sub_block[2] = [unicodedata.normalize('NFKD', raw_text).encode('ascii','ignore')]

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

    departure_with_time = datetime(year=departure.year,month=departure.month,day=departure.day)
    number_traveltype = int(conf_file["webpage"]["travel_type"])
    page_traveltype = Traveltype.objects.get(traveltype = number_traveltype)
    #departure extraction_tags
    departure_fields = conf_file["webpage"]["extraction_tags"]["departure"]["fields"]
    departure_format = conf_file["webpage"]["extraction_tags"]["departure"]["format"]
    departure_formula = conf_file["webpage"]["extraction_tags"]["departure"]["formula"]
    departure_list = get_data_list(departure_fields,html_file)

    #arrival extraction_tags
    arrival_fields = conf_file["webpage"]["extraction_tags"]["arrival"]["fields"]
    arrival_format = conf_file["webpage"]["extraction_tags"]["arrival"]["format"]
    arrival_formula = conf_file["webpage"]["extraction_tags"]["arrival"]["formula"]
    arrival_list = get_data_list(arrival_fields,html_file)

    #price extraction_tags
    price_fields = conf_file["webpage"]["extraction_tags"]["price"]["fields"]
    price_format = conf_file["webpage"]["extraction_tags"]["price"]["format"]
    price_formula = conf_file["webpage"]["extraction_tags"]["price"]["formula"]
    price_list = get_data_list(price_fields,html_file)

    #duration extraction_tags
    duration_fields = conf_file["webpage"]["extraction_tags"]["duration"]["fields"]
    duration_format = conf_file["webpage"]["extraction_tags"]["duration"]["format"]
    duration_formula = conf_file["webpage"]["extraction_tags"]["duration"]["formula"]
    duration_list = get_data_list(duration_fields,html_file)

    #travel_agency extraction_tags
    travel_agency_fields = conf_file["webpage"]["extraction_tags"]["travel_agency"]["fields"]
    travel_agency_format = conf_file["webpage"]["extraction_tags"]["travel_agency"]["format"]
    travel_agency_formula = conf_file["webpage"]["extraction_tags"]["travel_agency"]["formula"]
    travel_agency_list = get_data_list(travel_agency_fields,html_file)

    #frequency extraction_tags
    if conf_file["webpage"]["frequency_format"] != []:
        frequency_fields = conf_file["webpage"]["extraction_tags"]["frequency"]["fields"]
        frequency_format = conf_file["webpage"]["extraction_tags"]["frequency"]["format"]
        frequency_formula = conf_file["webpage"]["extraction_tags"]["frequency"]["formula"]
        frequency_list = get_data_list(frequency_fields,html_file)

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
        str_departure = str(departure_list[x].string)
        result_format = processRawText(conf_file,str_departure,departure_format,departure_formula,origin_city,destination_city)
        new_travel_departure = departure_with_time + timedelta(hours=int(result_format[0]), minutes = int(result_format[1]), seconds = 0)

        #Extract or calculare duration
        if duration_list != None : #if have data of duration then i extract it
            str_duration = str(duration_list[x].string)
            result_format = processRawText(conf_file,str_duration,duration_format,duration_formula,origin_city,destination_city)
            aux_new_travel_duration = departure_with_time - departure_with_time + timedelta(hours=int(result_format[0]), minutes = int(result_format[1]), seconds = 0)
        else: #otherwise calculate
            str_arrival = str(arrival_list[x].string)
            result_format = processRawText(conf_file,str_arrival,arrival_format,arrival_formula,origin_city,destination_city)
            new_travel_arrival = departure_with_time + timedelta(hours=int(result_format[0]), minutes = int(result_format[1]), seconds = 0)
            aux_new_travel_duration = new_travel_arrival - new_travel_departure

        if aux_new_travel_duration != None: #convert timedelta in minutes
            new_travel_duration = aux_new_travel_duration.seconds // 60
        #Extract price
        #the format must be (non digit or empty) (all digits price's) (non digit or empty)
        str_price = str(price_list[x].string)
        result_format = processRawText(conf_file,str_price,price_format,price_formula,origin_city,destination_city)
        new_travel_price = str(result_format[0])
        print new_travel_price

        #Extract travel_agency
        if travel_agency_list != None : #from HTML
            new_travel_agency = Travelagency.objects.get(name=travel_agency_list[x].string)
        else: #from json
            new_travel_agency  = Travelagency.objects.get(name=travel_agency_format)

        #if all of data is not empty, then create the travel object
        print "departure"
        print new_travel_departure
        print "duration"
        print new_travel_duration
        print "price"
        print new_travel_price
        print "agency"
        print new_travel_agency
        if str(new_travel_departure) != '' and str(new_travel_duration) != '' and str(new_travel_price) != '0' and str(new_travel_price) != '' and str(new_travel_agency) != '' :
            print "holaaaaaa"
            if conf_file["webpage"]["frequency_format"] == []: #if the departure does not depend on the days of the week
                #print(str(new_travel_departure),str(new_travel_arrival),str(new_travel_duration),new_travel_price,new_travel_agency)
                print "llegue"
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
                print "la cague"
                for date in dates:#para cada fecha en el rengo de consulta, si la fecha pertenece a la frecuencia, creo el travel
                    if verifyFrequency(conf_file,date,frequency_list[x].string):
                        departure_with_time = datetime(year=date.year,month=date.month,day=date.day)
                        result_format = processRawText(conf_file,str_departure,departure_format,departure_formula,origin_city,destination_city)
                        new_travel_departure = departure_with_time + timedelta(hours=int(result_format[0]), minutes = int(result_format[1]), seconds = 0)
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

def get_data_list(fields_list,html_file):
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
        for i in range(1, len(matches.groups()) + 1):

            output_text += [matches.group(i)]
        #else:   #if there's a constant as format we return the constant
        #    output_text = [raw_format_aux]
    else:
        if(raw_format_aux == "city_distance"):  #if we find the special format city_distance we calculate it and return it
            final_formula = str.replace(raw_formula_aux, "city_distance", str(DISTANCE_MATRIX[origin_city.id][destination_city.id]))
            output_text = [str(round(eval(final_formula), 0))]
        else:   #if there's a format and a formula we retrieve the data and execute the formula
            matches = re.search(raw_format_aux, raw_text_aux)
            final_formula = raw_formula_aux
            for i in range(1, len(matches.groups()) + 1):
                final_formula = str.replace(final_formula, "$" + str(i), matches.group(i))
            output_text = [str(round(eval(final_formula), 2))]

    return output_text

def verifyFrequency(conf_file,date,frequency_data):
    #TODO funcion que retorne un boolean dependiendo si la fecha es una fecha de la frecuencia o no
    if(len(conf_file["webpage"]["frequency_format"]) == 9):
        frequencies = frequency_data.split(conf_file["webpage"]["frequency_format"][9])
        daily = conf_file["webpage"]["frequency_format"][7]
        span = conf_file["webpage"]["frequency_format"][8]
        for raw_freq in frequencies:
            freq = unicodedata.normalize('NFKD', raw_freq).encode('ascii','ignore')
            if(re.search(daily, freq)):
                return True
            elif(re.search(conf_file["webpage"]["frequency_format"][date.weekday()], freq)):
                return True
            elif(re.search(span, frequency_data)):
                matches = re.search("(.)*" + span + "(.)*", frequency_data)
                counter = 0
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
