import requests
from bs4 import BeautifulSoup
import re
from .models import *
from django.shortcuts import render


def currency_masive_update(): #actualiza  toda la bd a dolares
    response = requests.get("http://query.yahooapis.com/v1/public/yql?q=select%20Name,Rate%20from%20yahoo.finance.xchange%20where%20pair%20in%20%28%22USDEUR%22,%20%22USDUYU%22,%20%22USDARS%22,%20%22USDBRL%22%29&env=store://datatables.org/alltableswithkeys")
    bs = BeautifulSoup(response.content,"xml")
    currencies = [c.cod for c in Currency.objects.all() if c.cod != 'USD']
    arr_before = []
    arr_after = []
    for currency in currencies:
        travels = Travel.objects.filter(currency = currency)
        divide = float(bs.find(text=re.compile(currency)).parent.parent.find("Rate").text)
        for travel in travels:
            arr_before.append([travel.currency,travel.price,travel.idtravel]) #para debug
            travel.price = round(travel.price / divide , 2)
            travel.currency = "USD"
            arr_after.append([travel.currency,travel.price]) #para debug
            travel.save()
    debug = {"debug":  zip(arr_before,arr_after)}
    return debug

def currency_update_specific(currency,webpage): #recibe dos strings, actualiza la bd a dolares, para esa pagina y esa moneda
    response = requests.get("http://query.yahooapis.com/v1/public/yql?q=select%20Name,Rate%20from%20yahoo.finance.xchange%20where%20pair%20in%20%28%22USDEUR%22,%20%22USDUYU%22,%20%22USDARS%22,%20%22USDBRL%22%29&env=store://datatables.org/alltableswithkeys")
    bs = BeautifulSoup(response.content,"xml")
    travels = Travel.objects.filter(currency = currency,webpage = webpage)
    divide = float(bs.find(text=re.compile(currency)).parent.parent.find("Rate").text)
    for travel in travels:
        travel.price = round(travel.price / divide , 2)
        travel.currency = "USD"
        travel.save()
