from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime,timedelta
from .models import *


#recurcion
def recursion(origin_country,origin_city,destination_country,destination_city,cost,datetime_object,list_travels,lista_recorridos,cant_travels,max_escalas):
    if max_escalas <= 3 :
        cost[0] += 1
        dAux=datetime_object+timedelta(days=3)
        max_escalas +=1
        string_destino = destination_country +'-' + str(destination_city)
        list_aux = Travel.objects.filter(origin_country=origin_country, origin_city = origin_city,departure__gte=  datetime_object,departure__lte=  dAux).order_by('origin_country','origin_city','destination_country','destination_city')
        lista_a_recorrer = []
        for t in list_aux: #me fijo todas las parejas de destinos que tengo partiendo de la ciudad que estoy parado
            aux_string = t.destination_country + '-' +  str(t.destination_city)
            if aux_string not in lista_a_recorrer :
                if aux_string not in lista_recorridos:
                    lista_a_recorrer.append(aux_string)


        #para cada par paisDestino-ciudadDestino que tengo a partir del nodo que estoy parado me fijo si tengo algun camino para llegar al destino final
        for l in lista_a_recorrer:
            lista2 = []
            lista_recorridos[len(lista_recorridos):] = [l]

            #Este for se hace por 2 morivos:
            #si hago lista2 = lista_recorridos, comparten memoria y una vez que hago el pop al final pierdo tambien el valor en lista2
            #pasa lo mismo si hago list_travels[len(list_travels):]= [lista_recorridos], comparten memoria y pierdo elementos en list_travels cuando hago el pop
            #por eso creo una nueva lista y si me sirve la agrego a la lista final de viajes
            x = 0
            for x in xrange(len(lista_recorridos)):
                lista2.append(lista_recorridos[x])

            if l == string_destino:#si en el que estoy parado es el final, agrego el camino recorrido a la lista de viajes
                list_travels[len(list_travels):]= [lista2]
                cant_travels[0] += 1
            else:#Sino, hago el paso recursivo
                vOrigin_country,vOrigin_city = l.split('-')
                recursion(vOrigin_country,vOrigin_city,destination_country,destination_city,cost,datetime_object,list_travels,lista_recorridos,cant_travels,max_escalas)
            lista_recorridos.pop()


def index(request):
    print(str(datetime.now()) + '  --inicio' )
    datetime_object = datetime.strptime('Sep 1 2017  2:33PM', '%b %d %Y %I:%M%p')
    vOrigin_country = 'URU'
    vOrigin_city = 6
    vDestination_country = 'ARG'
    vDestination_city = 29
    list_travels = []
    lista_recorridos = ['URU-6']
    cant_travels = [0]
    cost = [0]
    recursion(vOrigin_country,vOrigin_city,vDestination_country,vDestination_city,cost,datetime_object,list_travels,lista_recorridos,cant_travels,0)
    print(cost[0])
    context = {
    'latest_question_list': list_travels}
    print(str(datetime.now())+ '  --fin')
    return render(request, 'db/index.html', context)
