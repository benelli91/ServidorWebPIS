# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .forms import NameForm
from .forms import NameForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from cooler import estimate_path
from db_direct import getUniGraph
from util import load_all_costs_unigraph
# Create your views here.

ady,costs = getUniGraph()
load_all_costs_unigraph()

def index(request):
    # if this is a POST request we need to process the form data
    resultado = {}
    if request.method == 'POST':
        #form = NameForm(request.POST)

        #data = request.POST
        #resultado = estimate_path(ady,costs,int(data.get("from")),int(data.get("to")))
        #print 'resultado:'
        #print resultado
        1
    else:
        form = NameForm()

    return render(request, 'index.html',  resultado)
