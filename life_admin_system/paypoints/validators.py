from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date


def validate_date_paypoint(value):
    if value > date.today():
        raise ValidationError("Date joining cannot be in the future.")
    
paypoint_code_validator = RegexValidator(
    regex=r'^pps[a-z]*$',
    message="Paypoint code must start with 'pps' followed by lowercase letters only."
)
