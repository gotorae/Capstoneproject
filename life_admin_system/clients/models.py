# models.py

from django.db import models, transaction
from django.utils import timezone
from .validators import id_number_validator, phone_regex


class Client(models.Model):
    client_code = models.CharField(max_length=10, unique=True, db_index=True, editable=False)
    client_name = models.CharField(max_length=200)
    client_surname = models.CharField(max_length=200)
    id_number = models.CharField(max_length=12, unique=True, validators=[id_number_validator])
    dob = models.DateField()
    email= models.EmailField(unique=True)
    phone_number = models.CharField(max_length=16, validators=[phone_regex])
    street_address = models.CharField(max_length=30, null=True, blank=True)
    location_address = models.CharField(max_length=30, null=True, blank=True)
    city_address = models.CharField(max_length=30, null=True, blank=True)

       

    #generate a custom client code
    def save(self, *args, **kwargs):
        if not self.client_code:
            last_client = Client.objects.order_by('-client_code').first()

            if last_client:
                last_number = int(last_client.client_code[2:])  # 
                new_number = last_number + 1
            else:
                new_number = 1

            self.client_code = f"CC{new_number:08d}"  # A000000001 format

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_name} {self.client_surname}"
    
    
    
