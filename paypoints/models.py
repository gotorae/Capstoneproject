# models.py
from decimal import Decimal
from datetime import date
from django.db import models, transaction
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .validators import validate_date_paypoint, paypoint_code_validator

class Paypoint(models.Model):
    paypoint_code = models.CharField(max_length=20, unique=True, editable=True, db_index=True, 
                                     validators=[paypoint_code_validator], 
                                     help_text="must start with pps")
    paypoint_name = models.CharField(max_length=200)
    date_joined = models.DateField(validators=[validate_date_paypoint])

    def save(self, *args, **kwargs):
        # enforce lowercase to avoid PPSZESA vs ppszesa duplicates
        self.paypoint_code = self.paypoint_code.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.paypoint_name}"



