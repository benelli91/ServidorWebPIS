# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    country = models.ForeignKey('Country', models.DO_NOTHING, db_column='country')
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'city'
        unique_together = (('id', 'country'),)

    def __str__(self):
        return str(self.id) + '-' + str(self.country) + '-' + self.name


class Country(models.Model):
    id = models.CharField(primary_key=True, max_length=3)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'country'

    def __str__(self):
        return str(self.id) + '-' + self.name



class Travel(models.Model):
    idtravel = models.IntegerField(primary_key=True)
    departure = models.DateTimeField()
    origin_country = models.CharField(max_length=3)                #ForeignKey(City, models.DO_NOTHING, db_column='origin_country')
    origin_city = models.IntegerField()
    destination_country = models.CharField(max_length=3)                #ForeignKey(City, models.DO_NOTHING, db_column='destination_country')
    destination_city = models.IntegerField()
    price = models.IntegerField()
    duration = models.TimeField()
    traveltype = models.ForeignKey('Traveltype', models.DO_NOTHING, db_column='traveltype')
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'travel'

    def __str__(self):
        return str(self.idtravel) + '*' + str(self.departure) + '*' + str(self.price) +'-' + str(self.duration) + '-' + self.traveltype.travelname + '-' + self.description


class Traveltype(models.Model):
    traveltype = models.IntegerField(primary_key=True)
    travelname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'traveltype'

    def __str__(self):
        return str(self.traveltype) + '-' + self.travelname
