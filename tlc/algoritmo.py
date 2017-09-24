from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime,timedelta
from .models import *
import sys
import ipdb

def ordenarVectores(list_travels,list_precios_travels,cant_travels):
    i = 0
    list_precio_int = [0]
    x = 0
    for x in xrange(len(list_precios_travels)):
        if x == 0:
            list_precio_int[0] = int(list_precios_travels[x])
        else :
            list_precio_int.append(int(list_precios_travels[x]))

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
        aux = int(n)
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


#recurcion
def recursion(origin_country,origin_city,destination_country,destination_city,cost,fecha_comienzo,fecha_actual,fecha_maxima,list_travels,list_precios_travels,lista_recorridos,cant_travels,max_escalas,max_cost,ciudades_Analizadas):
    #if max_escalas <= 9 :
    #antes se accedia a origin_country directo, ahora es Travel.origin_city.country.id
    max_escalas +=1
    string_destino = destination_country +'-' + str(destination_city)
    if ciudades_Analizadas.has_key(origin_city):
        list_aux = ciudades_Analizadas.get(origin_city)
    else:
        list_aux = Travel.objects.filter(origin_city = origin_city,departure__gte=  fecha_comienzo,departure__lte=  fecha_maxima).order_by('price','-departure')
        ciudades_Analizadas[origin_city] = list_aux


    lista_a_recorrer = []
    lista_precios = []
    aux_departure = None
    for t in list_aux: #me fijo todas las parejas de destinos que tengo partiendo de la ciudad que estoy parado
        #print t.destination_city.country.name
        if t.departure >= fecha_actual:
            #print(t.departure , fecha_actual , fecha_maxima)
            aux_string = t.destination_city.country.id + '-' +  str(t.destination_city.id)
            aux_duration = t.duration
            minutos  = aux_duration % 60
            horas = (aux_duration - minutos) / 60
            print( horas,minutos , aux_duration)
            aux_departure = t.departure

            fecha_actual_aux= aux_departure + timedelta(hours=horas, minutes = minutos, seconds = 0)
            if t not in lista_recorridos and not have_i_passed(t,lista_recorridos):
                #para cada par paisDestino-ciudadDestino que tengo a partir del nodo que estoy parado me fijo si tengo algun camino para llegar al destino final
                index = 0
                #for l in lista_a_recorrer:
                #cost += lista_precios[index]
                cost += t.price
                lista_recorridos[len(lista_recorridos):] = [t]
                if cost < max_cost[0] or cant_travels[0] < 10 :
                    #if l == string_destino:#si en el que estoy parado es el final, agrego el camino recorrido a la lista de viajes
                    if aux_string == string_destino:#si en el que estoy parado es el final, agrego el camino recorrido a la lista de viajes
                        lista2 = []
                        #Este for se hace por 2 morivos:
                        #si hago lista2 = lista_recorridos, comparten memoria y una vez que hago el pop al final pierdo tambien el valor en lista2
                        #pasa lo mismo si hago list_travels[len(list_travels):]= [lista_recorridos], comparten memoria y pierdo elementos en list_travels cuando hago el pop
                        #por eso creo una nueva lista y si me sirve la agrego a la lista final de viajes
                        x = 0
                        for x in xrange(len(lista_recorridos)):
                            lista2.append(lista_recorridos[x])

                        #list_travels[len(list_travels):]= [t.idtravel]
                        #list_travels[len(list_travels):]= [lista2]
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

                    else:#Sino, hago el paso recursivo
                        vOrigin_country,vOrigin_city = aux_string.split('-')
                        recursion(vOrigin_country,vOrigin_city,destination_country,destination_city,cost,fecha_comienzo,fecha_actual_aux,fecha_maxima,list_travels,list_precios_travels,lista_recorridos,cant_travels,max_escalas,max_cost,ciudades_Analizadas)
                lista_recorridos.pop()
                #cost -= lista_precios[index]
                cost -= t.price
            #index += 1

def do_search(origin_city,destination_city,date):

    #CON LAS 3 lineas COMENTADAS ABAJO TE TIRA DATOS Y ES BUENA PARA HACER EL FRONT-END
    vOrigin_country = City.objects.filter(id = origin_city)[0].country.id
    #vOrigin_city = 11
    vDestination_country = City.objects.filter(id = destination_city)[0].country.id
    #vDestination_city = 20
    #date = '08/24/2017'
    aux_time = datetime.strptime(date+' 01:00AM', '%m/%d/%Y %I:%M%p')

    return backtracking(vOrigin_country,origin_city,vDestination_country,destination_city,aux_time)



def backtracking(vOrigin_country,vOrigin_city,vDestination_country,vDestination_city,aux_time):
    context = {}
    #msg_err = ""
    list_travels = []
    list_precios_travels = []
    lista_recorridos = [] #['URU-6']
    cant_travels = [0]
    cost = 0
    max_cost = [0]
    list_paises = Country.objects.all()
    ciudades_Analizadas = {}
    aux_country_orig = Country.objects
    aux_city_orig = City.objects
    aux_country_dest = Country.objects
    aux_city_des = City.objects
    """if request.method == 'POST':
        ###datetime_object = datetime.strptime('9 1 2017  2:33PM', '%m %d %Y %I:%M%p')
        datetime_object_max=datetime_object+timedelta(days=3)
        vOrigin_country = 'URU'
        vOrigin_city = 6
        vDestination_country = 'ARG'
        vDestination_city = 25
        ###

        body = request.body.split('&')
        print(body)
        try:
            aux,vOrigin_country = body[0].split('=')
            aux,vOrigin_city = body[1].split('=')
            aux,vDestination_country = body[2].split('=')
            aux,vDestination_city = body[3].split('=')
            aux,aux_time = body[4].split('=')
            try:
                if aux_time != "":
                    aux_time2 = aux_time.split('-')
                    final_aux_time = aux_time2[0]+' '+aux_time2[1]+' '+aux_time2[2]+' '+aux_time2[3]+':'+aux_time2[4]
                    datetime_object = datetime.strptime(final_aux_time, '%m %d %Y %I:%M%p')
                    datetime_object_max=datetime_object+timedelta(days=3)
                else:
                    msg_err = "hora en formato incorrecto"
            except ValueError:
                msg_err = "hora en formato incorrecto"
        except ValueError:
            msg_err = "datos de formulario incorrectos"
        """
    try:
        aux_country_orig = Country.objects.get(id=vOrigin_country)
        try:
            aux_city_orig = City.objects.get(id=vOrigin_city,country=vOrigin_country)
            try:
                aux_country_dest = Country.objects.get(id=vDestination_country)
                try:
                    aux_city_des = City.objects.get(id=vDestination_city,country=vDestination_country)
                except ValueError:
                    print "la ciudad destino no es correcta"
            except ValueError:
                print "el pais destino no es correcto"
        except ValueError:
            print "la ciudad origen no es correcta"
    except ValueError:
        print "el pais origen no es correcto"

    fecha_comienzo = aux_time
    fecha_actual = aux_time
    #print datetime_object
    fecha_maxima=fecha_comienzo+timedelta(days=3)
    #print datetime_object_max

    recursion(vOrigin_country,vOrigin_city,vDestination_country,vDestination_city,cost,fecha_comienzo,fecha_actual,fecha_maxima,list_travels,list_precios_travels,lista_recorridos,cant_travels,0,max_cost,ciudades_Analizadas)
    #print(list_precios_travels)
    list_travels,list_precios_travels = ordenarVectores(list_travels,list_precios_travels,cant_travels)
    #print(list_precios_travels)
    context = {
    'list_travels': list_travels,
    'list_paises' : list_paises,
    'paisOrigen' : aux_country_orig.name,
    'ciudadOrigen' : aux_city_orig.name,
    'paisDestino' : aux_country_dest.name,
    'ciudadDestino' : aux_city_des.name}
    return context
