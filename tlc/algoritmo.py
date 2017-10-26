from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime,timedelta
from .models import *
from django.db.models import F
import sys
import requests
from bs4 import BeautifulSoup
import re
import ipdb

def ordenarVectores(list_travels, list_precios_travels, cant_travels):
    i = 0
    list_precio_int = [0]
    x = 0
    for x in xrange(len(list_precios_travels)):
        if x == 0:
            list_precio_int[0] = float(list_precios_travels[x])
        else :
            list_precio_int.append(float(list_precios_travels[x]))

    while i < cant_travels[0] :
        precio_actual = list_precio_int[i]
        elemento_actual = list_travels[i]
        minimo = precio_actual
        j = i
        while j <= cant_travels[0] -1:
            if list_precio_int[j] < minimo:
                minimo = list_precio_int[j]
                indice_minimo = j
            j += 1
        if minimo < precio_actual:
            #print(precio_actual)
            #print(minimo)
            aux_precio = list_precio_int[i]
            aux_elemento = elemento_actual
            list_precio_int[i] = list_precio_int[indice_minimo]
            list_travels[i] = list_travels[indice_minimo]
            list_precio_int[indice_minimo] = precio_actual
            list_travels[indice_minimo] = elemento_actual
        i += 1
    x = 0
    list_precios_travels= []
    for x in xrange(len(list_precio_int)):
        list_precios_travels.append(str(list_precio_int[x]))

    return (list_travels,list_precios_travels)

def find_max(list_precios_travels):
    to_remove = 0
    new_max = 0
    index_to_remove = 0
    index = 0

    for n in list_precios_travels:
        aux = float(n)
        if aux > to_remove:
            new_max = to_remove
            to_remove = aux
            index_to_remove = index
        index += 1
    return (new_max,to_remove,index_to_remove)

def have_i_passed(t,recorrido):
    passed = False
    for i in range (0,len(recorrido)):
        if t.destination_city.id == recorrido[i].origin_city.id:
            return True

#######################################
# Recursion de Backtracking
#######################################
def recursion(origin_city, destination_city, cost, fecha_comienzo, fecha_actual, fecha_maxima, list_travels, list_precios_travels, lista_recorridos, cant_travels, max_escalas, max_cost, ciudades_analizadas, cotizaciones):
    max_escalas += 1

    # [ Identificador de la ciudad destino es unico ]
    key_destino = str(destination_city)

    # Se chequea si la ciudad de origen fue procesada en otra iteracion:
    if ciudades_analizadas.has_key(origin_city):
        from_origin_city_travels = ciudades_analizadas.get(origin_city)
        print 'ENTRO EN IF DE CIUDADES ANALIZADAS'
    else:
        # De lo contrario se realiza la consulta a la base:
        from_origin_city_travels = Travel.objects.filter(
            origin_city = origin_city,
            departure__gte = fecha_actual,
            departure__lte = fecha_maxima - timedelta(minutes=1)*F("duration")
        ).order_by('price','-departure')

        # Se agrega la ciudad de origen actual al conjunto de ciudades procesadas
        ciudades_analizadas[origin_city] = from_origin_city_travels
    #import ipdb; ipdb.set_trace()
    lista_a_recorrer = []
    lista_precios = []

    # Para todas las parejas de destinos que tengo partiendo de la ciudad actual:
    for t in from_origin_city_travels:

        # Se modifica el precio para los travels con monedas distintas a USD
        if t.currency != 'USD':
            divisor = cotizaciones[t.currency]
            t.price = round(t.price / divisor,2)
            t.currency = 'USD'
        print t
        # Si es la primer iteracion
        # => Se verifica que el viaje comience en la fecha de comienzo (en timezone 0)
        if fecha_actual == fecha_comienzo:
            date_condition = fecha_comienzo <= t.departure and t.departure <= (fecha_comienzo + timedelta(days=1))
        else:
            date_condition= t.departure >= fecha_actual

        # Si se cumple condicion para la fecha:
        if date_condition:

            key_travel_destination = str(t.destination_city.id)

            # Conversion a horas Y minutos de la duracion del travel
            minutos  = t.duration % 60
            horas = (t.duration - minutos) / 60

            # Se actualiza la fecha actual
            fecha_actual_aux = t.departure + timedelta(hours=horas, minutes = minutos, seconds = 0)

            if t not in lista_recorridos and not have_i_passed(t,lista_recorridos):

                # Para cada ciudadDestino que tengo a partir del nodo que estoy parado,
                # me fijo si tengo algun camino para llegar al destino final
                index = 0
                cost += t.price
                lista_recorridos[len(lista_recorridos):] = [t]

                if cost < max_cost[0] or cant_travels[0] < 10:
                    # Si el destino del Travel es el final,
                    # agrego el camino recorrido a la lista de viajes
                    if key_travel_destination == key_destino:
                        # Se realiza la siguiente copia de lista_recorridos,
                        # para evitar compartir memoria entre listas.
                        lista2 = []
                        x = 0

                        for x in xrange(len(lista_recorridos)):
                            lista2.append(lista_recorridos[x])

                        list_travels[len(list_travels):]= [lista2]
                        list_precios_travels[len(list_precios_travels):]= [str(cost)]

                        if cant_travels[0] >= 10:
                            max_cost[0],to_delete,index_to_remove = find_max(list_precios_travels)
                            list_precios_travels.remove(str(to_delete))
                            string_to_remove = list_travels[index_to_remove]
                            list_travels.remove(string_to_remove)
                        else:
                            cant_travels[0] += 1

                        if cost > max_cost[0]:
                            max_cost[0] = cost

                    # Si no se llega a destino, continua la recursion
                    else:
                        # El destino del travel procesado,
                        # pasa a ser el origen de la siguiente iteracion
                        origin_city = key_travel_destination
                        recursion(origin_city, destination_city, cost,fecha_comienzo,fecha_actual_aux,fecha_maxima,list_travels,list_precios_travels,lista_recorridos,cant_travels,max_escalas,max_cost,ciudades_analizadas,cotizaciones)
                lista_recorridos.pop()
                cost -= t.price

################################################
# Inicializacion para backtracking
################################################
def do_search(origin_city, destination_city, date, timezone):

    # Se lleva la fecha solicitada a Timezone 0 (Date - timezone offset)
    initial_date = datetime.strptime(date+' 12:00AM', '%m/%d/%Y %I:%M%p') + timedelta(minutes=-timezone)

    # Carga de cotizaciones
    response = requests.get("http://query.yahooapis.com/v1/public/yql?q=select%20Name,Rate%20from%20yahoo.finance.xchange%20where%20pair%20in%20%28%22USDEUR%22,%20%22USDUYU%22,%20%22USDARS%22,%20%22USDBRL%22%29&env=store://datatables.org/alltableswithkeys")
    bs = BeautifulSoup(response.content,"xml")
    currencies = [c.cod for c in Currency.objects.all() if c.cod != 'USD']
    divisores = [float(bs.find(text=re.compile(currency)).parent.parent.find("Rate").text) for currency in currencies]
    cotizaciones = dict(zip(currencies,divisores))

    # LLamado al algoritmo
    result = backtracking(origin_city, destination_city, initial_date, cotizaciones, timezone)

    return result

################################################
# Backtracking - Primer Iteracion
################################################
def backtracking(vOrigin_city, vDestination_city, initial_date, cotizaciones, timezone):
    # Inicializacion de variables para backtracking
    list_travels = []
    list_precios_travels = []
    lista_recorridos = []
    cant_travels = [0]
    cost = 0
    max_cost = [0]

    ciudades_analizadas = {}

    # Se determina la duracion minima y maxima de un viaje
    fecha_actual = initial_date
    fecha_maxima= initial_date + timedelta(days=3)

    # Llamados recursivos de Backtracking
    recursion(vOrigin_city,
        vDestination_city,
        cost,
        initial_date,
        fecha_actual,
        fecha_maxima,
        list_travels,
        list_precios_travels,
        lista_recorridos,
        cant_travels,
        0, # max_escalas :O
        max_cost,
        ciudades_analizadas,
        cotizaciones
    )

    # Se ordenan los resultados de la recursion
    list_travels,list_precios_travels = ordenarVectores(list_travels, list_precios_travels, cant_travels)

    # Resultados a retornar
    context = {
        'list_travels': list_travels,
        'no_results': len(list_travels) == 0,
        'list_paises' : Country.objects.all(),
        'ciudadOrigen' : City.objects.get(id=vOrigin_city),
        'ciudadDestino' : City.objects.get(id=vDestination_city),
        'timezoneOffset': timezone
    }

    return context
