#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from collections import defaultdict
eng = create_engine('postgresql://jalvez:pis2017...@localhost/pis_db')

def getUniGraph():
    """
    devuelve dos parametros:
    1)devuelve un grafo de adyacencia, ejecuta una sola query
    el grafo es un diccionario {idCity1: [ady1, ady2, ..], idCity2: [ady3,...]}

    2)devuelve un diccionario de costos
    ejemplo: {(1, 2): 7, (4, 7): 20 .. }
    """
    with eng.connect() as con:

        rs = con.execute('SELECT * FROM Average_costs')
        rs =  ([r[0],r[1],r[2]] for r in rs)
        ady = defaultdict(list)
        costs = defaultdict(list)
        for c1,c2,cost in rs:
            ady[c1].append(c2)
            costs[c1,c2]=cost


        return ady,costs
