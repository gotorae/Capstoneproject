
from rest_framework import serializers
from .models import Administrator
import re

class AdministratorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = Administrator
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirmation',
            'profile_photo',
            'dob',
        ]

    def validate(self, data):
        # Check password confirmation
        if data.get('password') != data.get('password_confirmation'):
            raise serializers.ValidationError({"password_confirmation": "Password does not match"})
        return data

    def validate_password(self, value):
        # Minimum length handled by field, but we can re-assert and add more rules
        if len(value) < 8:
            raise serializers.ValidationError("Minimum characters must be at least 8")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        # Require at least three consecutive digits (keep if that’s intentional)
        if not re.search(r"\d{3}", value):
            raise serializers.ValidationError("Password must contain at least three consecutive digits")
        if not re.search(r"[\*@#$%^&*]", value):
            raise serializers.ValidationError("Password must contain at least one special character (* @ # $ % ^ & *)")
        return value

    
    def create(self, validated_data):
        # Remove confirmation—do not store it
        validated_data.pop('password_confirmation', None)
        password = validated_data.pop('password')
        user = Administrator(**validated_data)
        user.set_password(password)  # hash the password
        user.save()
