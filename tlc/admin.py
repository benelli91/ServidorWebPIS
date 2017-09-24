# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import City, Country, Travel, Traveltype
# Register your models here.

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('id', 'name', 'country')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('id', 'name')

@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    search_fields = ('idtravel', )
    list_display = ('idtravel', 'departure', 'origin_city',
        'destination_city', 'price', 'duration', 'traveltype',
        'description')

@admin.register(Traveltype)
class TravelTypeAdmin(admin.ModelAdmin):
    search_fields = ( 'travelname', )
    list_display = ('traveltype', 'travelname')
