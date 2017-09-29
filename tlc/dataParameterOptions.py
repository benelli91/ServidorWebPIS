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
    data = str(line["data"])
    date_format = conf_file["webpage"]["date_format"]
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

    return result
