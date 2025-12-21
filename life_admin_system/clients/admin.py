from django.contrib import admin
from .models import  Client
from django.db import models




class ClientAdminModel(admin.ModelAdmin):
    list_display = ['client_code', 'client_name','client_surname',
                    'id_number','dob','email','phone_number',
                    'street_address', 'location_address', 'city_address']
    list_filter = ['client_code', 'client_name','client_surname','id_number','phone_number']
    search_fields = ['client_code', 'client_name','client_surname','id_number','phone_number']

admin.site.register(Client, ClientAdminModel)
