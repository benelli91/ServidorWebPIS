# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .forms import NameForm
from .forms import NameForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from algoritmo import do_search
from cargaGoogleBatch import cargaGoogleB

# Create your views here.

#def index(request):
#    return render(request,'index.html')



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
        resultado = do_search(str(data.get("from", "")),str(data.get("to")),str(data.get("date")))
        print resultado
    	# if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'index.html',  resultado)

def cargaGoogle(request):
    resultado = {}
    #if request.method == 'POST':
    #    resultado = do_search(str(data.get("from", "")),str(data.get("to")),str(data.get("date")))
    cargaGoogleB()

    return render(request, 'scraping.html',  resultado)
