# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .forms import NameForm
from .forms import NameForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from cooler import estimate_path
from db_direct import getUniGraph
# Create your views here.

ady,costs = getUniGraph()

def index(request):
    # if this is a POST request we need to process the form data
    resultado = {}
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        #if form.is_valid(): //FALTA CHEQUEAR QUE SEA VALIDO EL FORM
            #redirect('tlc.views.index')
        data = request.POST
        resultado = retriev_graph()
        print 'resultado:'
        print resultado
        print 'Travels:'
        print resultado.get('list_travels')[0][0].origin_city.country.id
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'index.html',  resultado)
