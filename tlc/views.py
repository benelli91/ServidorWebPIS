# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from .forms import NameForm
from .forms import NameForm
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
# Create your views here.

#def index(request):
#    return render(request,'index.html')



def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #redirect('tlc.views.index')
            resultado = {
            'latest_question_list': list_travels,
            'list_paises' : list_paises,
            'paisOrigen' : aux_country_orig.name,
            'ciudadOrigen' : aux_city_orig.name,
            'paisDestino' : aux_country_dest.name,
            'ciudadDestino' : aux_city_des.name,
            'msg_err' : msg_err}

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'index.html', {'form': form})
