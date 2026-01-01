from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import date


# 1) Field-level validator that accepts a *value*
def validate_first_day(value):
    if value.day != 1:
        raise ValidationError("Start date must be the first day of the month.")
    

def policy_status(self):
        if self.months_in_arrears > 2 and self.months_paid >= 1:
            return "Policy Lapsed"
        elif self.months_in_arrears <= 2 and self.months_paid >= 1:
            return "Policy Active"
        elif self.months_in_arrears > 2 and self.months_paid < 1:
            return "NTU Non Payment"
        else:
            return "Policy Accepted"
        
def proposal_sign_date(value):
    if value > date.today():
        raise ValidationError("proposal sign date cannot be in the future")
