from .models import *
from rest_framework import serializers

class TravelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Travel
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'

class CitySearchSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    class Meta:
        model = City
        fields = ('id', 'value','label')

    def get_label(self, obj):
        if obj.country:
            return obj.name + ', ' + obj.country.name
        else:
            return obj.name

    def get_value(self, obj):
        if obj.country:
            return obj.name + ', ' + obj.country.name
        else:
            return obj.name



class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'

class TravelAgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Travelagency
        fields = '__all__'

class TravelTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Traveltype
        fields = '__all__'
