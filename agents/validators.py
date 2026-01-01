from datetime import date
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def validate_date_joining(value):
    if value > date.today():
        raise ValidationError("Date joining cannot be in the future.")