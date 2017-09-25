from .models import *
import random
import networkx as nx
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.pyplot as plt
import cooler

def populate():
    citys = City.objects.all()
    ids=[n for n in citys]
    filas = 10

    for i in range(100):
        average = AverageCosts(city1=random.choice(ids), city2=random.choice(ids),cost=random.randint(1, 30))
        average.save()
        print 'hola'



def draw_graph(graph=None, labels=None, graph_layout='shell',
               node_size=200, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='red', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):


    Avg = AverageCosts.objects.all()
    graph = [(n.city1.id,n.city2.id) for n in Avg]
    #graph = [(0, 1), (1, 5),(3,2), (1, 7), (4, 5), (4, 8), (1, 6), (3, 7), (5, 9),
    #         (2, 4), (0, 4), (2, 5), (3, 6), (8, 9),
    #         (10,11)
    #         ]
    # you may name your edge labels
    labels = [n.cost for n in Avg]
    #print labels
    #draw_graph(graph, labels)




    # create networkx graph
    G=nx.DiGraph()

    # add edges
    for edge in graph:
        G.add_edge(edge[0], edge[1])

    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)

    # draw graph
    nx.draw_networkx_nodes(G,graph_pos,node_size=node_size,
                           alpha=node_alpha, node_color=node_color)
    nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    nx.draw_networkx_labels(G, graph_pos,font_size=node_text_size,
                            font_family=text_font)

    if labels is None:
        labels = range(len(graph))
    print graph
    print labels

    edge_labels = dict(zip(graph, labels))
    print edge_labels
    nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labels,
                                 label_pos=edge_text_pos)

    # show graph
    plt.show()

def querys(): #llando a esta funcion se genera un archivo en tlc/tmp que te muestra todas las querys hechas en la ejecucion

    from django.db import connection
    import csv

    #f = open('tlc/tmp/querys', 'w')
    #print connection.queries.encode("ascii")

    #print connection.queries[0]['time']
    data = [(n['time'].encode("ascii").replace('\"',''),n['sql'].encode("ascii").replace('\"','')) for n in connection.queries]
    print data
    with open('tlc/tmp/querys','wb') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['tiempo','consulta'])
        for row in data:
            csv_out.writerow(row)

def load_a_cost_unigraph(city1,city2,cost): #la idea es que cada vez que se carguen datos para un par de ciudades, se ejecute esta funcion
    average = AverageCosts(city1=city1, city2=city2,cost=cost)
    average.save()

def load_all_costs_unigraph():

    citys = City.objects.all()
    ids=[n for n in citys]
    for i in ids:
        for j in ids:
            if i != j:
                travel = Travel.objects.filter(origin_city=i, destination_city=j).order_by('price').first()
                print travel
                if travel:
                    print i.id,j.id,travel.price
                    average = AverageCosts(city1=i, city2=j,cost=travel.price)
                    average.save()
