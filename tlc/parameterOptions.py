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
import unicodedata

def dataParameterOptions(line, conf_file, origin_city, destination_city, departure):
    local_codes_directory = 'tlc/local_city_codes/'
    data = str(line["data"])
    date_format = conf_file["webpage"]["date_format"]
    #total_result = []
    total_result = ''
    counter = 1
    #Special case for scripts
    if isinstance(line,dict):
        if line.has_key("field_type"):
            if(line["field_type"] == "script"):
                total_result += '('
                for data in line["data"]:
                    new_line = json.loads('{"field_type":"", "id":"", "data":["' + data + '"]}')
                    total_result += "'"
                    total_result += dataParameterOptions(new_line, conf_file, origin_city, destination_city, departure)
                    total_result += "'"
                    if(counter < len(line["data"])):
                        total_result += ", "
                    counter += 1
                total_result += ')'
                return total_result

    for data in line["data"]:
        #CASE for each posible value of the "data" attribute of the configuration file
        if(data == "origin_country"):
            result = origin_country.name
        elif(data == "destination_country"):
            result = destination_country.name
        elif(data == "origin_country_alias"):
            result = str(origin_city.country)
        elif(data == "destination_country_alias"):
            result = str(destination_city.country)
        elif(data == "origin_city"):
            result = str(origin_city.name)
        elif(data == "destination_city"):
            result = str(destination_city.name)
        elif(data == "origin_alias"):
            if(conf_file["webpage"]["travel_type"] == 1):
                result = str(origin_city.alias_flight)
            elif(conf_file["webpage"]["travel_type"] == 2):
                result = str(origin_city.alias_port)
            elif(conf_file["webpage"]["travel_type"] == 3):
                result = str(origin_city.alias_bus)
        elif(data == "destination_alias"):
            if(conf_file["webpage"]["travel_type"] == 1):
                result = str(destination_city.alias_flight)
            elif(conf_file["webpage"]["travel_type"] == 2):
                result = str(destination_city.alias_port)
            elif(conf_file["webpage"]["travel_type"] == 3):
                result = str(destination_city.alias_bus)
        elif(data == "departure"):
            result = departure.strftime(date_format)
        elif(data == "actual_date"):
            today = datetime.today().date()
            result = today.strftime(date_format)
        elif(data == "click"):
            result = "click"
        elif(data == "remove"):
            result = "remove"
        elif(data == "origin_local_code"):
            raw_files = [pos_json for pos_json in os.listdir(local_codes_directory) if pos_json.endswith('.json')]
            for local_file in raw_files:
                with open(local_codes_directory + local_file) as data_file:
                    codes = json.load(data_file)
                    if(conf_file["webpage"]["name"] == codes["name"]):
                        if(origin_city.name in codes["codes"]):
                            result = codes["codes"][origin_city.name]
                        else:
                            return "invalid"
        elif(data == "destination_local_code"):
            raw_files = [pos_json for pos_json in os.listdir(local_codes_directory) if pos_json.endswith('.json')]
            for local_file in raw_files:
                with open(local_codes_directory + local_file) as data_file:
                    codes = json.load(data_file)
                    if(conf_file["webpage"]["name"] == codes["name"]):
                        if(destination_city.name in codes["codes"]):
                            result = codes["codes"][destination_city.name]
                        else:
                            return "invalid"
        #UpperCase option
        elif(data == "origin_country_upper"):
            result = origin_country.name
            result = result.upper()
        elif(data == "destination_country_upper"):
            result = destination_country.name
            result = result.upper()
        elif(data == "origin_country_alias_upper"):
            result = str(origin_city.country)
            result = result.upper()
        elif(data == "destination_country_alias_upper"):
            result = str(destination_city.country)
            result = result.upper()
        elif(data == "origin_city_upper"):
            result = str(origin_city.name)
            result = result.upper()
        elif(data == "destination_city_upper"):
            result = str(destination_city.name)
            result = result.upper()
        elif(data == "origin_alias_upper"):
            if(conf_file["webpage"]["travel_type"] == 1):
                result = str(origin_city.alias_flight)
            elif(conf_file["webpage"]["travel_type"] == 2):
                result = str(origin_city.alias_port)
            elif(conf_file["webpage"]["travel_type"] == 3):
                result = str(origin_city.alias_bus)
            result = result.upper()
        elif(data == "destination_alias_upper"):
            if(conf_file["webpage"]["travel_type"] == 1):
                result = str(destination_city.alias_flight)
            elif(conf_file["webpage"]["travel_type"] == 2):
                result = str(destination_city.alias_port)
            elif(conf_file["webpage"]["travel_type"] == 3):
                result = str(destination_city.alias_bus)
            result = result.upper()
        #LowerCase option
        elif(data == "origin_country_lower"):
            result = origin_country.name
            result = result.lower()
        elif(data == "destination_country_lower"):
            result = destination_country.name
            result = result.lower()
        elif(data == "origin_country_alias_lower"):
            result = str(origin_city.country)
            result = result.lower()
        elif(data == "destination_country_alias_lower"):
            result = str(destination_city.country)
            result = result.lower()
        elif(data == "origin_city_lower"):
            result = str(origin_city.name)
            result = result.lower()
        elif(data == "destination_city_lower"):
            result = str(destination_city.name)
            result = result.lower()
        elif(data == "origin_alias_lower"):
            if(conf_file["webpage"]["travel_type"] == 1):
                result = str(origin_city.alias_flight)
            elif(conf_file["webpage"]["travel_type"] == 2):
                result = str(origin_city.alias_port)
            elif(conf_file["webpage"]["travel_type"] == 3):
                result = str(origin_city.alias_bus)
            result = result.lower()
        elif(data == "destination_alias_lower"):
            if(conf_file["webpage"]["travel_type"] == 1):
                result = str(destination_city.alias_flight)
            elif(conf_file["webpage"]["travel_type"] == 2):
                result = str(destination_city.alias_port)
            elif(conf_file["webpage"]["travel_type"] == 3):
                result = str(destination_city.alias_bus)
            result = result.lower()
        else:
            result = ""

        #total_result += [result]
        total_result += str(result)

    return total_result

def javascriptParameterOptions(line, phantom):
    element = ""
    if(line["tag_type"] == "id"):
        element = phantom.find_element_by_id(line["id"])
    elif(line["tag_type"] == "multiple_id"):
        element = phantom.find_elements_by_id(line["id"])
    elif(line["tag_type"] == "class_name"):
        element = phantom.find_element_by_class_name(line["id"])
    elif(line["tag_type"] == "multiple_class_name"):
        element = phantom.find_elements_by_class_name(line["id"])
    elif(line["tag_type"] == "name"):
        element = phantom.find_element_by_name(line["id"])
    elif(line["tag_type"] == "multiple_name"):
        element = phantom.find_elements_by_name(line["id"])
    elif(line["tag_type"] == "xpath"):
        element = phantom.find_element_by_xpath(line["id"])
    elif(line["tag_type"] == "multiple_xpath"):
        element = phantom.find_elements_by_xpath(line["id"])
    elif(line["tag_type"] == "link_text"):
        element = phantom.find_element_by_link_text(line["id"])
    elif(line["tag_type"] == "multiple_link_text"):
        element = phantom.find_elements_by_link_text(line["id"])
    elif(line["tag_type"] == "partial_link_text"):
        element = phantom.find_element_by_partial_link_text(line["id"])
    elif(line["tag_type"] == "multiple_partial_link_text"):
        element = phantom.find_elements_by_partial_link_text(line["id"])
    elif(line["tag_type"] == "tag_name"):
        element = phantom.find_element_by_class(line["tag_name"])
    elif(line["tag_type"] == "multiple_tag_name"):
        element = phantom.find_elements_by_class(line["tag_name"])
    elif(line["tag_type"] == "css_selector"):
        element = phantom.find_element_by_css_selector(line["id"])
    elif(line["tag_type"] == "multiple_css_selector"):
        element = phantom.find_elements_by_css_selector(line["id"])
    return element
