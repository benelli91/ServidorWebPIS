# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

class Country(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'country'


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.ForeignKey(Country, models.DO_NOTHING, db_column='country')
    name = models.TextField()
    alias_flight = models.CharField(max_length=3, blank=True, null=True)
    alias_port = models.TextField()
    alias_bus = models.TextField()
    airport = models.BooleanField()
    port = models.BooleanField()
    bus_station = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'city'

    def __str__(self):
        return str(self.id) +'-' +self.name + '\n'


class Travel(models.Model):
    departure = models.DateTimeField()
    origin_city = models.ForeignKey(City, models.DO_NOTHING, related_name='origin_city', db_column='origin_city')
    destination_city = models.ForeignKey(City, models.DO_NOTHING, related_name='destination_city', db_column='destination_city')
    price = models.FloatField()
    duration = models.IntegerField()
    traveltype = models.ForeignKey('Traveltype', models.DO_NOTHING, db_column='traveltype')
    webpage = models.TextField()
    travel_agency = models.IntegerField(blank=True, null=True)
    currency = models.TextField()
    updated = models.BooleanField()
    description = models.TextField()
    idtravel = models.BigAutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'travel'

    def __str__(self):
        return str(self.idtravel) +'-'+str(self.departure) + '\n' +str(self.origin_city) +  '-' +str(self.destination_city) +  '-' +str(self.price) +  '-' +str(self.currency) + '\n'


class Travelagency(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    reference = models.TextField()
    traveltype = models.ForeignKey('Traveltype', models.DO_NOTHING, db_column='traveltype')

    class Meta:
        managed = False
        db_table = 'travelagency'


class Traveltype(models.Model):
    traveltype = models.IntegerField(primary_key=True)
    travelname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'traveltype'



class Currency(models.Model):
    cod = models.CharField(primary_key=True, max_length=3)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'currency'
