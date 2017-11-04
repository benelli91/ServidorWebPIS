#coding: latin1
import ipdb
from lxml import html
from .models import *
import requests

def loadExchange():
    #exchange currencies are taken from BROU
    page = requests.get('https://www.portal.brou.com.uy/cotizaciones')
    response = html.fromstring(page.content)
    base = Currency.objects.filter(base = True).first()
    currencies = [c for c in Currency.objects.all() if c.cod != base.cod ]
    print 'dólar'
    for currency in currencies:
        #if the currency is local, have to use "sell" exchange, else have to use arbitrage
        print currency.cod
        print base.name
        if currency.local:
            #ipdb.set_trace()
            context    = response.xpath('(//tbody)[1]/tr[contains(td, $mda)]',mda = base.name)[0]
            divPosition = base.tableposition
        else:
            context    = response.xpath('(//tbody)[1]/tr[contains(td, $mda)]',mda = currency.name)[0]
            divPosition = currency.tableposition
        div  = context.xpath('normalize-space(.//td['+str(divPosition)+'])')
        #replace comma to point
        div = div.replace(',', '.')
        div = float(div)
        Currency.objects.filter(cod=currency.cod).update(divisor=div)
    #convert currency objects to currency strings with the code for easy usage, and return a dictionary  --> currency:divider
    
