from rest_framework import serializers
from db.models import Country, City, Traveltype, Travel

class CountrySerializer(serializers.ModelSerializer):
     class Meta:
         model = Country
         fields = ('id', 'name')

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'country', 'name')

class TraveltypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveltype
        fields = ('traveltype', 'travelname')

class TravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = ('idtravel', 'departure', 'origin_country', 'origin_city', 'destination_country', 'destination_city', 'price', 'duration', 'traveltype', 'description')
