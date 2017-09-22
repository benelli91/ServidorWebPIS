import heapq
from .models import *
import sys
from utils import draw_graph
from utils import querys

"""
LA IDEA ES, EN UNA PRIMER VERSION DEVOLVER UNA LISTA DE NODOS QUE SON EL MENOR CAMINO DE UNA CIUDAD A OTRA
DEL GRAFO CON ARISTAS AGREGADAS


la salida es una lista de idCity con el menor camino de A a B


"""

def dijkstra(adj, costs, s, t):
    ''' Return predecessors and min distance if there exists a shortest path
        from s to t; Otherwise, return None '''
    Q = []     # priority queue of items; note item is mutable.
    d = {s: 0} # vertex -> minimal distance
    Qd = {}    # vertex -> [d[v], parent_v, v]
    p = {}     # predecessor
    visited_set = set([s])

    for v in adj.get(s, []):
        d[v] = costs[s, v]
        item = [d[v], s, v]
        heapq.heappush(Q, item)
        Qd[v] = item

    while Q:
        print Q
        cost, parent, u = heapq.heappop(Q)
        if u not in visited_set:
            print 'visit:', u
            p[u]= parent
            visited_set.add(u)
            if u == t:
                return p, d[u]
            for v in adj.get(u, []):
                if d.get(v):
                    if d[v] > costs[u, v] + d[u]:
                        d[v] =  costs[u, v] + d[u]
                        Qd[v][0] = d[v]    # decrease key
                        Qd[v][1] = u       # update predecessor
                        heapq._siftdown(Q, 0, Q.index(Qd[v]))
                else:
                    d[v] = costs[u, v] + d[u]
                    item = [d[v], u, v]
                    heapq.heappush(Q, item)
                    Qd[v] = item

    return None

def make_undirected(cost):
    ucost = {}
    for k, w in cost.iteritems():
        ucost[k] = w
        ucost[(k[1],k[0])] = w
    return ucost

def estimate_path(ady,cost):
    """
    toma un grafo dirigido y devuelve el camino de menor costo
    adj = { 1: [2,3,6],2: [1,3,4],3: [1,2,4,6], 4: [2,3,5,7], 5: [4,6,7], 6: [1,3,5,7],7: [4,5,6]}
    cost = { (1,2):7,(1,3):9,(1,6):14,(2,3):10,(2,4):15,(3,4):11,(3,6):2,(4,5):6,(5,6):9,(4,7):2,(5,7):1,(6,7):12}
    """
    print 'estimate_path'
    print 'adj2'
    print adj
    # adjacent list
    # edge costs

    print cost

    cost = make_undirected(cost)

    s, t = 1, 2
    predecessors, min_cost = dijkstra(adj, cost, s, t)
    c = t
    path = [c]
    print 'min cost:', min_cost
    while predecessors.get(c):
        path.insert(0, predecessors[c])
        c = predecessors[c]

    print 'shortest path:', path
    #querys()

#retriev_graph()
#draw_graph()
