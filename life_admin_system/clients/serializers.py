
from rest_framework import serializers
from .models import Client, Upload


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'client_name', 'client_surname', 'id_number', 'dob', 'email',
            'phone_number', 'street_address', 'location_address', 'city_address'
        ]
        read_only_fields = ['client_code']


class UploadSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source='uploaded_by.username', read_only=True)
    approved_by = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = Upload
        fields = [
            'id', 'file', 'uploaded_by', 'uploaded_at',
            'is_approved', 'approved_by', 'approved_at',
            'is_rejected', 'reject_reason', 'created_at'
        ]
        read_only_fields = [
            'uploaded_by', 'uploaded_at',
            'is_approved', 'approved_by', 'approved_at',
            'is_rejected', 'reject_reason', 'created_at'
        ]


class UploadDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reject_reason = serializers.CharField(
        required=False, allow_blank=True
    )
