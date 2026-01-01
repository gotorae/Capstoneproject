

from import_export import resources
from .models import Client

class ClientResource(resources.ModelResource):
    class Meta:
        model = Client
        fields = (
            'client_name', 'client_surname', 'id_number', 'dob', 'email',
            'phone_number', 'street_address', 'location_address', 'city_address'
        )
