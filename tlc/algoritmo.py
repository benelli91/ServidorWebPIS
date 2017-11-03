from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime,timedelta
from .models import *
from django.db.models import F
import sys
import requests
from bs4 import BeautifulSoup
import re
import time
import ipdb

def sortVectores(travel_list, travels_price_list, quantity_travels):
    i = 0
    float_price_list = [0]
    x = 0
    for x in xrange(len(travels_price_list)):
        if x == 0:
            float_price_list[0] = float(travels_price_list[x])
        else :
            float_price_list.append(float(travels_price_list[x]))

    while i < quantity_travels[0] :
        actual_price = float_price_list[i]
        actual_element = travel_list[i]
        actual_duration = 0
        for t in actual_element:
            actual_duration += t.duration
        minimal_price = actual_price
        minimal_duration = actual_duration
        j = i
        while j <= quantity_travels[0] -1:
            if float_price_list[j] <= minimal_price:
                duration_aux = 0
                for t in travel_list[j]:
                    duration_aux += t.duration
                if float_price_list[j] == minimal_price:
                    if duration_aux < minimal_duration:
                        minimal_price = float_price_list[j]
                        minimal_duration = duration_aux
                        index_of_minimal = j
                else:
                    minimal_price = float_price_list[j]
                    minimal_duration = duration_aux
                    index_of_minimal = j
            j += 1
        if minimal_price < actual_price or minimal_duration < actual_duration:
            aux_precio = float_price_list[i]
            aux_elemento = actual_element
            float_price_list[i] = float_price_list[index_of_minimal]
            travel_list[i] = travel_list[index_of_minimal]
            float_price_list[index_of_minimal] = actual_price
            travel_list[index_of_minimal] = actual_element
        i += 1
    x = 0
    travels_price_list= []
    for x in xrange(len(float_price_list)):
        travels_price_list.append(str(float_price_list[x]))

    return (travel_list,travels_price_list)

def have_i_passed(t,list_trips_traveled):
    passed = False
    for i in range (0,len(list_trips_traveled)):
        if t.destination_city.id == list_trips_traveled[i].origin_city.id:
            passed = True
    return passed

def verifyBestOption(list_trips_traveled,cost,travel_list,travels_price_list):

    exists_better_option = False
    exist_same_condition = False
    index_same_condition = 0
    duration = 0
    for t in list_trips_traveled:
        duration += t.duration
    first_travel = list_trips_traveled[0]
    origin_city = first_travel.origin_city
    departure = first_travel.departure
    cont = 0

    for travels in travel_list:
        travel_ini = travels[0]
        if origin_city.id == travel_ini.origin_city.id and str(departure) == str(travel_ini.departure) and str(cost) == str(travels_price_list[cont]):
            duration_aux = 0
            for t in travels:
                duration_aux += t.duration

            if duration < duration_aux:
                exists_better_option = False
                exist_same_condition = True
                index_same_condition = cont
                return exists_better_option,exist_same_condition,index_same_condition
            else :
                exists_better_option = True

        cont +=1

    return exists_better_option,exist_same_condition,index_same_condition

#######################################
# Recursion de Backtracking
#######################################
def recursion_NR(origin_city, destination_city, cost, start_date, current_date, maximum_date, travel_list, travels_price_list, list_trips_traveled, quantity_travels, max_scales, max_cost, cotizaciones):
    """inicializo todas las variables"""
    origin_city_ini = origin_city
    found_trip = False
    found_trip_in_recurrence = False
    key_destination = str(destination_city)
    ciudades_alcanzables = {}
    indice_ciudades_alcanzables = {}
    termino = False
    cost = 0
    viajes_posibles = {}
    indice_viajes_posibles = {}
    ciudades_recorridas = []
    ciudades_recorridas[len(ciudades_recorridas):] = [origin_city_ini]

    cotizaciones = {'UYU':29.65,'ARS':13}

    i = 1
    aux_current_date = current_date
    ant_cost = 0
    ant_current_date = start_date
    list_ant_current_date_traveled = []
    list_ant_cost = []

    max_cost = 0
    while (not termino):
        """mientras tenga iteraciones posibles
        tomo la ultima ciudad que tengo agregada en la lista  de ciudades_recorridas
        si es la primer iteracion es la ciudad origen, sino es la ultima escala que es en la que estoy parado
        """
        origin_city = ciudades_recorridas[len(ciudades_recorridas) -1]
        """en el dic ciudades_alcanzables, con que ciudades esta conectada la origin_city que estoy actualmente
        esta consulta la hago una sola vez por cada ciudad"""
        if not ciudades_alcanzables.has_key(origin_city):
            ciudades_alcanzables[origin_city] = []
            from_origin_city_travels = Travel.objects.filter(
                origin_city = origin_city,
                departure__gte = start_date,
                departure__lte = maximum_date - timedelta(minutes=1)*F("duration")
            ).distinct('destination_city')
            """la consulta anterior me devuelve un travel por cada ciudad distinta
            en el for de abajo saco la ciudad destino y las guardo en el dic"""
            aux_list_destinations = []
            for item in from_origin_city_travels:
                aux_list_destinations[len(aux_list_destinations):] = [item.destination_city.id]
            ciudades_alcanzables[origin_city] = aux_list_destinations
            indice_ciudades_alcanzables[origin_city] = len(aux_list_destinations)

        """en el diccionario viajes_posibles, para cada ciudad origen, tengo un diccionario con los viajes a cada destino posible
        es decir, por cada combinacion origen-destino posible, tengo un diccionario con todos los viajes"""
        if not viajes_posibles.has_key(origin_city):
            lista_aux = ciudades_alcanzables[origin_city]
            viajes_to = {}
            indice_viajes_to = {}
            for destino in lista_aux:
                viajes_to[destino] = list(Travel.objects.filter(
                                                origin_city = origin_city,
                                                destination_city = destino,
                                                departure__gte = start_date,
                                                departure__lte = maximum_date - timedelta(minutes=1)*F("duration")
                                            ).order_by('departure').distinct('departure','price','duration'))
                indice_viajes_to[destino] = len(viajes_to[destino])

            viajes_posibles[origin_city] = viajes_to
            indice_viajes_posibles[origin_city] = indice_viajes_to

        """ en el diccionario indice_ciudades_alcanzables  voy guardando el indice que estoy recorriendo en el dic ciudades_alcanzables"""
        """analogo para el dic indice_viajes_posibles """

        """me fijo el indice de la ciudad alcanzable que tengo que recorrer"""
        max_destino = indice_ciudades_alcanzables[origin_city]
        if max_destino > 0 and len(ciudades_recorridas) < 6:
            """si me queda alguna por recorrer
            me quedo con el viaje que indica el indice"""
            element = ciudades_alcanzables[origin_city][max_destino-1]
            """si la ciudad que queiro recorrer, no esta en la lista de las que ya visite, entonces sigo"""
            max_viaje = indice_viajes_posibles[origin_city][element]
            if str(element) not in ciudades_recorridas:
                if max_viaje > 0:
                    """si me queda algun viaje por recorrer"""
                    t = viajes_posibles[origin_city][element][max_viaje -1]

                    """una vez que tomo el travel, disminuyo el indice"""
                    indice_viajes_posibles[origin_city][element] -= 1
                    key_travel_destination = str(t.destination_city.id)
                    """ de aca en adelante es la misma logica que el recursivo con algunas excepciones en los else"""
                    # If is the first iteration
                    # => Verify that the trip starts on the start date
                    if aux_current_date == start_date:
                        date_condition = start_date <= t.departure and t.departure <= (start_date + timedelta(days=1))
                    else:
                        date_condition= t.departure >= current_date

                    # If for the date the condition is true:
                    if date_condition:
                        # Conversion to hours and minutes of the duration of travel
                        minutes  = t.duration % 60
                        hours = (t.duration - minutes) / 60
                        # The current_date is updated

                        """guardo los valores aneriores de la fecha y el precio """
                        ant_current_date = aux_current_date
                        ant_cost = cost

                        """actualizo precio y hora"""
                        aux_current_date = t.departure + timedelta(hours=hours + 1, minutes = minutes)
                        cost += t.price
                        if cost <= max_cost or quantity_travels[0] < 10:
                            # If the destination of the trip is the city you are looking for,
                            # Add the way traveled to the travel list
                            if key_travel_destination == key_destination:
                                """si cumple con las condiciones de precio y fecha, agrego el destino como escala, y
                                guardo el precio y la hora que tenia antes de entrar a este viaje"""
                                list_trips_traveled[len(list_trips_traveled):] = [t]
                                list_ant_current_date_traveled[len(list_ant_current_date_traveled):] = [aux_current_date]
                                list_ant_cost[len(list_ant_cost):] = [cost]
                                # Check if there is a trip with the same departure time and the same price,
                                # If it exists, I'll take the shortest one
                                exists_better_option,exist_same_condition,index_same_condition = verifyBestOption(list_trips_traveled,cost,travel_list,travels_price_list)
                                if not exists_better_option:
                                    # Made a copy from list_trips_traveled,
                                    # to avoid sharing memory between lists.
                                    aux_list = []
                                    x = 0
                                    for x in xrange(len(list_trips_traveled)):
                                        aux_list.append(list_trips_traveled[x])

                                    if exist_same_condition:
                                        travel_list.remove(travel_list[index_same_condition])
                                        travels_price_list.remove(travels_price_list[index_same_condition])
                                        travel_list[len(travel_list):]= [aux_list]
                                        travels_price_list[len(travel_list):]= [str(cost)]
                                    else:
                                        travel_list[len(travel_list):]= [aux_list]
                                        travels_price_list[len(travels_price_list):]= [str(cost)]

                                        if quantity_travels[0] >= 10:
                                            float_price_list = [float(i) for i in travels_price_list]
                                            index = float_price_list.index(max(float_price_list))
                                            travels_price_list.remove(travels_price_list[index])
                                            travel_list.remove(travel_list[index])
                                            max_cost = max([float_price_list])
                                        else:
                                            quantity_travels[0] += 1

                                        if cost > max_cost:
                                            max_cost = cost

                                    found_trip = True

                                """una vez que procese la conmbinacion de viajes, vuelvo el precio y hora hacia atras"""
                                cost = ant_cost
                                aux_current_date = ant_current_date
                                list_ant_cost.pop()
                                list_ant_current_date_traveled.pop()
                                list_trips_traveled.pop()
                            else:
                                """Si la ciudad no es el destino final, la agrego como escala y la proceso en la siguiente iteracion"""
                                ciudades_recorridas[len(ciudades_recorridas):] = [str(t.destination_city.id)]
                        else:
                            """si el costo ya es mayor que el mas caro de los 10 resultados, podo el BT y vuelvo hacia atras el costo y la hora"""
                            cost = ant_cost
                            aux_current_date = ant_current_date
                else:
                    """si no me quedan mas viajes que conecten la ciudad origen con la que indica el indice de alcanzables
                    disminuyo el indice para iterar sobre otro destino"""
                    indice_ciudades_alcanzables[origin_city] -= 1

                    """la linea de abajo que  esta comentada provoca un loop que todavia no entiendo porque"""
                    """la logica para poner esa linea seria que, si ya termine de procesar un destino vuelvo a reiniciar el contador de ciudades alcanzalbes"""
                    """por si otra escala llega hacia el"""
                    indice_viajes_posibles[origin_city][element] = len(viajes_posibles[origin_city][element])
            else:
                indice_ciudades_alcanzables[origin_city] -= 1
        else:
            if len(list_ant_cost) > 1:
                list_ant_cost.pop()
                cost = list_ant_cost[len(list_ant_cost) -1]
                list_ant_current_date_traveled.pop()
                aux_current_date = list_ant_current_date_traveled[len(list_ant_current_date_traveled) -1]
                list_trips_traveled.pop()
            else:
                cost = 0
                aux_current_date = start_date
                if len(list_ant_cost) > 0 :
                    list_ant_cost.pop()
                    list_ant_current_date_traveled.pop()
                    list_trips_traveled.pop()

            """si ya no me quedan mas ciudades alcanzables por analizar
            reinicio el contador de ciudades alcanzalbes por si otra escala llega hacia el
            ademas reinicio el contador de viajes que conectan la ciudad
            Ademas de eso, saco la ciudad de la recorridas y vuelvo un paso atras """
            indice_ciudades_alcanzables[origin_city] = len(ciudades_alcanzables[origin_city])
            ciudades_recorridas.pop()


        """si ya no me quedan ciudades por recorrer, termino todas las iteraciones"""
        if len(ciudades_recorridas) == 0 :
            termino = True

        print 'recorridos', ciudades_recorridas



################################################
# Initialization to backtracking
################################################
def do_search(origin_city, destination_city, date, timezone):

    # The requested date is returned to TimeZone 0 (Date - timezone offset)
    initial_date = datetime.strptime(date+' 12:00AM', '%m/%d/%Y %I:%M%p') + timedelta(minutes=-timezone)

    # Carga de cotizaciones
    """response = requests.get("http://query.yahooapis.com/v1/public/yql?q=select%20Name,Rate%20from%20yahoo.finance.xchange%20where%20pair%20in%20%28%22USDEUR%22,%20%22USDUYU%22,%20%22USDARS%22,%20%22USDBRL%22%29&env=store://datatables.org/alltableswithkeys")
    bs = BeautifulSoup(response.content,"xml")
    currencies = [c.cod for c in Currency.objects.all() if c.cod != 'USD']
    dividers = [float(bs.find(text=re.compile(currency)).parent.parent.find("Rate").text) for currency in currencies]
    cotizaciones = dict(zip(currencies,dividers))"""

    # Call to the algorithm
    result = backtracking(origin_city, destination_city, initial_date, None, timezone)

    return result

################################################
# Backtracking - First iteration
################################################
def backtracking(vOrigin_city, vDestination_city, initial_date, cotizaciones, timezone):
    # Initialization of variables for backtracking
    travel_list = []
    travels_price_list = []
    list_trips_traveled = []
    quantity_travels = [0]
    cost = 0
    max_cost = 0

    global processed_cities
    processed_cities = {}

    global cant_processed_cities
    cant_processed_cities = {}

    # The minimum and maximum duration of a trip is determined
    current_date = initial_date
    maximum_date= initial_date + timedelta(days=3)

    # Recursive calls of Backtracking
    recursion_NR(vOrigin_city,
        vDestination_city,
        cost,
        initial_date,
        current_date,
        maximum_date,
        travel_list,
        travels_price_list,
        list_trips_traveled,
        quantity_travels,
        0, # max_scales :O
        max_cost,
        cotizaciones
    )

    # The results of the recursion are sorted
    travel_list,travels_price_list = sortVectores(travel_list, travels_price_list, quantity_travels)

    asd = processed_cities.keys()

    for arr in asd:
        print arr , cant_processed_cities[arr] , '-->' , len(processed_cities[arr])
    # Results to return
    context = {
        'list_travels': travel_list,
        'no_results': len(travel_list) == 0,
        'list_paises' : Country.objects.all(),
        'ciudadOrigen' : City.objects.get(id=vOrigin_city),
        'ciudadDestino' : City.objects.get(id=vDestination_city),
        'timezoneOffset': timezone
    }

    return context
