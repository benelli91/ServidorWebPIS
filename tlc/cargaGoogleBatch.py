
from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime,timedelta,tzinfo
from .models import *
import time
import sys
import os

def obtenerValor(valAux):
    str1 = valAux.split('>')
    atributo = str1[0].split('<')[1]
    valor = str1[1].split('<')[0]
    return valor

def cargaGoogleB():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    ciudades = ['MVD','BUE','MIA','NYK']
    MVD = City.objects.get(id = 11)
    BUE = City.objects.get(id = 20)
    MIA = City.objects.get(id = 30)
    NYK = City.objects.get(id = 36)
    codCiudades = [MVD,BUE,MIA,NYK]
    avion = Traveltype.objects.get(traveltype = 1)
    aeropuertos = {'MVD' : ['MVD'] , 'BUE':['AEP','EZE'], 'MIA' : ['MIA'] , 'NYC' : ['JFK','EWR','LGA']  }
    meses = {'enero' : '1' , 'febrero': '2', 'marzo' : '3' , 'abril' : '4', 'mayo' : '5', 'junio' : '6' , 'julio' : '7' ,\
                'agosto' : '8' , 'septiembre' : '9' ,  'octubre' : '10', 'noviembre' : '11', 'diciembre' : '12'   }

    #t = datetime_object.time()
    t = datetime.strptime('9 1 2017  2:33:20', '%m %d %Y %I:%M:%S')
    #t = datetime.time() 12, 10, 30)
    HTMLfile = open('tlc/templates/scraping.html', 'w')

    phantom = webdriver.PhantomJS()

    Travel.objects.filter(traveltype = 1).delete()
    #Para cargar un solo dia hay que modificar la variable dia para la fecha que quieran, y en el range poner 0,1
    dia = 1
    for d in range(0,1):
        dia += d
        charDia = str(dia)
        if dia < 10:
            charDia = '0' + charDia
        for i in range(0,3):
            for j in range(0,3):
                if i != j:
                    origen = ''
                    destino = ''
                    aux = aeropuertos.get(ciudades[i])
                    for z in range(len(aux)):
                        if z == 0:
                            origen = aux[z]
                        else :
                            origen = origen + ',' + aux[z]

                    aux = aeropuertos.get(ciudades[j])
                    for z in range(len(aux)):
                        if z == 0:
                            destino = aux[z]
                        else :
                            destino = destino + ',' + aux[z]

                    url = 'https://www.google.es/flights/?curr=USD#search;f=' + origen +';t=' + destino+';d=2017-10-'+charDia+';r=2017-10-'+charDia+';tt=o;eo=e'
                    phantom.get(url)
                    time.sleep(2)

                    # let's parse our html
                    soup = BeautifulSoup(phantom.page_source, "html.parser")
                    precios = soup.find_all('div',{'class': 'DQX2Q1B-d-Ab'})
                    horarios = soup.find_all('div',{'class': 'DQX2Q1B-d-Zb'})
                    compania = soup.find_all('div',{'class': 'DQX2Q1B-d-j'})
                    duracion = soup.find_all('div',{'class': 'DQX2Q1B-d-E'})
                    info = soup.find_all('div',{'class': 'DQX2Q1B-d-Qb'})

                    # and print out the html for first game
                    HTMLfile.write('<div>' + url+ '</div>')
                    for ix in range(len(precios)):
                        HTMLfile.write('precio ' +str(precios[ix]))
                        HTMLfile.write('horario ' +str(horarios[ix]))
                        HTMLfile.write('compania ' +str(compania[ix]))
                        HTMLfile.write('duracion ' +str(duracion[ix]))
                        HTMLfile.write('info ' + str(info[ix]))
                        HTMLfile.write('<div> </div>')

                        auxPrecie = ''.join(str(precios[ix].contents[0])[:-3].split(','))
                        auxPrecie = str.replace(auxPrecie,".","")
                        valPrecio = int(auxPrecie)
                        valDuracion = str(duracion[ix].contents[0])
                        valInfo = str(info[ix].contents[0]).encode('utf-8') #+ '; empresa ' + ''.join(str(compania[ix])).split('span')[1]

                        auxDeparture = ''.join(str(horarios[ix])).split('span')[1].split('"')[1].split(' ')
                        datetime_object = datetime.strptime(meses.get(auxDeparture[7]) + ' ' + auxDeparture[5] + ' ' + auxDeparture[9] + ' ' + auxDeparture[2], '%m %d %Y %H:%M')
                        #print (auxDeparture[0],auxDeparture[3],auxDeparture[5],auxDeparture[7])
                        #print(datetime_object)

                        hora  = str(duracion[ix].contents[0]).split('h ')[0]
                        minuto = str(duracion[ix].contents[0]).split('h ',1)[1].split('m')[0]
                        valDuracion = int(hora) * 60 + + int(minuto)
                        #valDuracion = datetime.strptime('9 1 2017  '+hora+':'+minuto+':00', '%m %d %Y %I:%M:%S')
                        #valDuracion = datetime,timedelta(minutes = int(minuto),hours = int(hora))
                        #print(valDuracion)


                        newTravel = Travel.objects.create(duration = valDuracion,traveltype = avion,origin_city = codCiudades[i],destination_city=codCiudades[j],price = valPrecio,description = valInfo,departure = datetime_object)



    HTMLfile.close()
    #print('fin')
