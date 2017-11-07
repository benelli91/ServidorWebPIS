from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime,timedelta
from .models import *
from django.db.models import F, Q
import sys
import requests
from bs4 import BeautifulSoup
import re
import time
import ipdb
from lxml import html


def load_exchanges():
    #loads exchanges from database
    base = Currency.objects.filter(base = True).first()
    cotizaciones = [(c.cod,c.divisor) for c in Currency.objects.all() if c.cod != base.cod ]
    cotizaciones = dict(cotizaciones)
    return cotizaciones

def load_travels(origin_city, start_date):

    start_time = time.clock()
    processed_cities[origin_city] = {}

    first_travels_day_1 = Travel.objects.filter(
        origin_city = origin_city,
        departure__gte = start_date,
        departure__lte = start_date + timedelta(hours=12)
    ).order_by('departure').distinct('departure','destination_city','price','duration','traveltype')

    last_travels_day_1 = Travel.objects.filter(
        origin_city = origin_city,
        departure__gte = start_date + timedelta(hours=12),
        departure__lte = start_date + timedelta(hours=24)
    ).order_by('departure').distinct('departure','destination_city','price','duration','traveltype')

    first_travels_day_2 = Travel.objects.filter(
        origin_city = origin_city,
        departure__gte = start_date + timedelta(hours=24),
        departure__lte = start_date + timedelta(hours=36)
    ).order_by('departure').distinct('departure','destination_city','price','duration','traveltype')

    last_travels_day_2 = Travel.objects.filter(
        origin_city = origin_city,
        departure__gte = start_date + timedelta(hours=36),
        departure__lte = start_date + timedelta(hours=48)
    ).order_by('departure').distinct('departure','destination_city','price','duration','traveltype')


    first_travels_day_3 = Travel.objects.filter(
        Q(origin_city = origin_city) &
        Q(departure__gte = start_date + timedelta(hours=48)) &
        Q(departure__lte = start_date + timedelta(hours=60)) &
        Q(departure__lte = start_date + (timedelta(minutes=1) * F("duration")))
    ).order_by('departure').distinct('departure','destination_city','price','duration','traveltype')

    last_travels_day_3 = Travel.objects.filter(
        Q(origin_city = origin_city) &
        Q(departure__gte = start_date + timedelta(hours=48)) &
        Q(departure__lte = start_date + (timedelta(minutes=1) * F("duration")))
    ).order_by('departure').distinct('departure','destination_city','price','duration','traveltype')

    count_time['sql_time'] += time.clock() - start_time

    # The current origin_city is added to the set of processed cities
    processed_cities[origin_city]['first_travels_d1'] = list(first_travels_day_1)
    processed_cities[origin_city]['last_travels_d1'] = list(last_travels_day_1)

    processed_cities[origin_city]['first_travels_d2'] = list(first_travels_day_2)
    processed_cities[origin_city]['last_travels_d2'] = list(last_travels_day_2)

    processed_cities[origin_city]['first_travels_d3'] = list(first_travels_day_3)
    processed_cities[origin_city]['last_travels_d3'] = list(last_travels_day_3)

def get_travels_for_origin_city(origin_city, current_date, start_date):
    start_time = time.clock()

    time_diff = current_date - start_date

    if time_diff == timedelta(seconds=0):
        from_origin_city_travels = ( processed_cities[origin_city]['first_travels_d1'] +
                                     processed_cities[origin_city]['last_travels_d1'] )

    elif time_diff <= timedelta(hours=12):
        from_origin_city_travels = ( processed_cities[origin_city]['first_travels_d1'] +
                                     processed_cities[origin_city]['last_travels_d1'] +
                                     processed_cities[origin_city]['first_travels_d2'] +
                                     processed_cities[origin_city]['last_travels_d2'] +
                                     processed_cities[origin_city]['first_travels_d3'] +
                                     processed_cities[origin_city]['last_travels_d3'] )

    elif time_diff <= timedelta(hours=24):
        from_origin_city_travels = ( processed_cities[origin_city]['last_travels_d1'] +
                                     processed_cities[origin_city]['first_travels_d2'] +
                                     processed_cities[origin_city]['last_travels_d2'] +
                                     processed_cities[origin_city]['first_travels_d3'] +
                                     processed_cities[origin_city]['last_travels_d3'] )
    elif time_diff <= timedelta(hours=36):
        from_origin_city_travels = ( processed_cities[origin_city]['first_travels_d2'] +
                                     processed_cities[origin_city]['last_travels_d2'] +
                                     processed_cities[origin_city]['first_travels_d3'] +
                                     processed_cities[origin_city]['last_travels_d3'] )
    elif time_diff <= timedelta(hours=48):
        from_origin_city_travels = ( processed_cities[origin_city]['last_travels_d2'] +
                                    processed_cities[origin_city]['first_travels_d3'] +
                                    processed_cities[origin_city]['last_travels_d3'] )

    elif time_diff <= timedelta(hours=60):
        from_origin_city_travels = ( processed_cities[origin_city]['first_travels_d3'] +
                                    processed_cities[origin_city]['last_travels_d3'] )

    else:
        from_origin_city_travels = processed_cities[origin_city]['last_travels_d3']

    count_time['armar_lista_travels_time'] += time.clock() - start_time
    return from_origin_city_travels

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
    aux_time = time.clock()
    passed = t.destination_city.id in [travel.origin_city.id for travel in list_trips_traveled]
    count_time['check_ciclos_time'] += time.clock() -aux_time
    return passed

def verifyBestOption(list_trips_traveled,cost,travel_list,travels_price_list):

    exists_better_option = False
    exist_same_condition = False
    index_same_condition = 0
    # duration = 0
    # for t in list_trips_traveled:
    #     duration += t.duration
    # first_travel = list_trips_traveled[0]
    # origin_city = first_travel.origin_city
    # departure = first_travel.departure
    # cont = 0
    #
    # for travels in travel_list:
    #     travel_ini = travels[0]
    #     if origin_city.id == travel_ini.origin_city.id and str(departure) == str(travel_ini.departure) and str(cost) == str(travels_price_list[cont]):
    #         duration_aux = 0
    #         for t in travels:
    #             duration_aux += t.duration
    #
    #         if duration < duration_aux:
    #             exists_better_option = False
    #             exist_same_condition = True
    #             index_same_condition = cont
    #             return exists_better_option,exist_same_condition,index_same_condition
    #         else :
    #             exists_better_option = True
    #
    #     cont +=1

    return exists_better_option,exist_same_condition,index_same_condition

#######################################
# Recursion de Backtracking
#######################################
def recursion(origin_city, destination_city, cost, start_date, current_date, maximum_date, travel_list, travels_price_list, list_trips_traveled, quantity_travels, max_scales, max_cost, cotizaciones):
    count_time['recursion_time'] += time.clock() - count_time['aux_recursion_time']

    max_scales += 1
    found_trip = False
    found_trip_in_recurrence = False

    if max_scales <= 4:

        # [ Identification of the destination city is unique ]
        key_destination = str(destination_city)

        # Check if the city of origin was processed in another iteration:
        if not processed_cities.has_key(origin_city):
            # Otherwise, the query is made in the database:
            load_travels(origin_city, start_date)

        from_origin_city_travels = get_travels_for_origin_city(origin_city,current_date, start_date)

        # For all trips that exist starting from the current city:
        for t in from_origin_city_travels:

            # The price is modified for travels with currencies other than USD
            if t.currency != 'USD':
                divider = cotizaciones[t.currency]
                t.price = round(t.price / divider,2)
                t.currency = 'USD'


            # If is the first iteration
            # => Verify that the trip starts on the start date
            if current_date == start_date:
                date_condition = start_date <= t.departure and t.departure <= (start_date + timedelta(days=1))
            else:
                date_condition= t.departure >= current_date

            # If for the date the condition is true:
            if date_condition:

                key_travel_destination = str(t.destination_city.id)

                # Conversion to hours and minutes of the duration of travel
                minutes  = t.duration % 60
                hours = (t.duration - minutes) / 60

                # The current_date is updated
                aux_current_date = t.departure + timedelta(hours=hours, minutes = minutes)

                #lo separo para poder tomar el tiempo de resolucion
                aux_time = time.clock()
                count_time['check_ciclos_time'] += time.clock() -aux_time
                
                #if not have_i_passed(t,list_trips_traveled):
                if not t.destination_city.id in cities_visited:
                    # If have not visited this city, look for a way to the destination
                    cost += t.price
                    #list_trips_traveled[len(list_trips_traveled):] = [t]
                    list_trips_traveled.append(t)
                    
                    # cities_visited[len(cities_visited):] = [t.destination_city.id]
                    if t.destination_city.id not in cities_visited:
                        cities_visited.append(t.destination_city.id)

                    if cost <= max_cost[0] or quantity_travels[0] < 10:
                        # If the destination of the trip is the city you are looking for,
                        # Add the way traveled to the travel list
                        if key_travel_destination == key_destination:
                            # Check if there is a trip with the same departure time and the same price,
                            # If it exists, I'll take the shortest one
                            exists_better_option,exist_same_condition,index_same_condition = verifyBestOption(list_trips_traveled,cost,travel_list,travels_price_list)
                            if not exists_better_option:
                                # Made a copy from list_trips_traveled,
                                # to avoid sharing memory between lists.
                                
                                # aux_list = []
                                # x = 0
                                # for x in xrange(len(list_trips_traveled)):
                                #     aux_list.append(list_trips_traveled[x])
                                
                                aux_list = list_trips_traveled[:]
                                
                                if exist_same_condition:
                                    # travel_list.remove(travel_list[index_same_condition])
                                    # travels_price_list.remove(travels_price_list[index_same_condition])
                                    del travel_list[index_same_condition]
                                    del travels_price_list[index_same_condition]
                                    # travel_list[len(travel_list):]= [aux_list]
                                    travel_list += aux_list
                                    #travels_price_list[len(travel_list):]= [str(cost)]
                                    travels_price_list.append(str(cost))
                                else:
                                    # travel_list[len(travel_list):]= [aux_list]
                                    travel_list += aux_list
                                    #travels_price_list[len(travel_list):]= [str(cost)]
                                    travels_price_list.append(str(cost))

                                    if quantity_travels[0] >= 10:
                                        float_price_list = [float(i) for i in travels_price_list]
                                        index = float_price_list.index(max(float_price_list))
                                        travels_price_list.remove(travels_price_list[index])
                                        travel_list.remove(travel_list[index])
                                        max_cost[0] = max([float_price_list])
                                    else:
                                        quantity_travels[0] += 1

                                    if cost > max_cost[0]:
                                        max_cost[0] = cost

                                found_trip = True
                        # If the destination of the trip isn't the city you are looking for,
                        else:
                            # The destination of the processed trip becomes the origin of the next iteration
                            origin_city = key_travel_destination
                            count_time['aux_recursion_time'] = time.clock()
                            aux_encontro_recursion = recursion(origin_city, destination_city, cost,start_date,aux_current_date,maximum_date,travel_list,travels_price_list,list_trips_traveled,quantity_travels,max_scales,max_cost,cotizaciones)
                            count_time['recursion_time'] += time.clock() - count_time['aux_recursion_time']
                            found_trip_in_recurrence = found_trip_in_recurrence or aux_encontro_recursion

                            if not aux_encontro_recursion and 1 == 2:
                                # list_to_delete = []
                                # if processed_cities.has_key(origin_city):
                                #     for aux_travel in processed_cities.get(origin_city):
                                #         if aux_travel.departure >= aux_current_date:
                                #             list_to_delete[len(list_to_delete):] = [aux_travel]
                                #
                                #     for travel_to_remove in list_to_delete:
                                #         processed_cities.get(origin_city).remove(travel_to_remove)
                                if processed_cities[origin_city]['first_travels_d1'].count(t):
                                    processed_cities[origin_city]['first_travels_d1'].remove(t)

                                if processed_cities[origin_city]['last_travels_d1'].count(t):
                                    processed_cities[origin_city]['last_travels_d1'].remove(t)

                                if processed_cities[origin_city]['first_travels_d2'].count(t):
                                    processed_cities[origin_city]['first_travels_d2'].remove(t)

                                if processed_cities[origin_city]['last_travels_d2'].count(t):
                                    processed_cities[origin_city]['last_travels_d2'].remove(t)

                                if processed_cities[origin_city]['first_travels_d3'].count(t):
                                    processed_cities[origin_city]['first_travels_d3'].remove(t)

                                if processed_cities[origin_city]['last_travels_d3'].count(t):
                                    processed_cities[origin_city]['last_travels_d3'].remove(t)


                    list_trips_traveled.pop()
                    cities_visited.pop()
                    cost -= t.price
    count_time['aux_recursion_time'] = time.clock()
    return found_trip or found_trip_in_recurrence

################################################
# Do_Search [Backtracking First call]
################################################
def do_search(origin_city, destination_city, date, timezone):
    # Initialization of variables for backtracking
    # The requested date is returned to TimeZone 0 (Date - timezone offset)

    global count_time
    count_time = {'sql_time':0,'total_time':time.clock(),'recursion_time':0,'check_ciclos_time':0,'armar_lista_travels_time' : 0 }


    initial_date = datetime.strptime(date+' 12:00AM', '%m/%d/%Y %I:%M%p') + timedelta(minutes=-timezone)
    cotizaciones = load_exchanges()

    travel_list = []
    travels_price_list = []
    list_trips_traveled = []
    quantity_travels = [0]
    cost = 0
    max_cost = [0]

    global processed_cities
    processed_cities = {}

    global cities_visited
    cities_visited = [origin_city]

    # The minimum and maximum duration of a trip is determined
    current_date = initial_date
    maximum_date= initial_date + timedelta(days=3)

    count_time['aux_recursion_time'] = time.clock()
    # Recursive calls of Backtracking
    recursion(origin_city,
        destination_city,
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
    count_time['recursion_time'] += time.clock() - count_time['aux_recursion_time']
    # The results of the recursion are sorted
    travel_list,travels_price_list = sortVectores(travel_list, travels_price_list, quantity_travels)


    count_time['total_time'] = time.clock() - count_time['total_time']

    print 'SQL' , count_time['sql_time']
    print 'llamado recursivo', count_time['recursion_time']
    print 'armar_lista_travels_time', count_time['armar_lista_travels_time']
    print 'check_ciclos_time', count_time['check_ciclos_time']
    print 'total', count_time['total_time']



    # Results to return
    context = {
        'list_travels': travel_list,
        'no_results': len(travel_list) == 0,
        'list_paises' : Country.objects.all(),
        'ciudadOrigen' : City.objects.get(id=origin_city),
        'ciudadDestino' : City.objects.get(id=destination_city),
        'timezoneOffset': timezone
    }

    return context