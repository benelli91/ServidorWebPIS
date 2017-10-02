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
    total_result = []
    counter = 1
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

        total_result += [result]


    return total_result
