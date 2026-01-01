from rest_framework import serializers
from .models import Paypoint

class PaypointSerializers(serializers.ModelSerializer):
    class Meta:
        model = Paypoint
        fields = ['paypoint_code', 'paypoint_name', 'date_joined']