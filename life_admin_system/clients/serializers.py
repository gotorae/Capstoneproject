from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['client_name', 'client_surname','id_number','dob', 'email',
                   'phone_number', 'street_address', 'location_address', 'city_address']
        read_only_fields = ['client_code']