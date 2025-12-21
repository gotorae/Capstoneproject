# models.py
from decimal import Decimal
from datetime import date
from django.db import models, transaction
from django.utils import timezone
from django.db.models import Sum
from .validators import proposal_sign_date, validate_first_day
from agents.models import Agent
from clients.models import Client
from paypoints.models import Paypoint
from django.core.exceptions import ValidationError
from access.models import Administrator
from django.conf import settings




class Policy(models.Model):
    contract_id = models.CharField(max_length=10, unique=True, db_index=True, editable=False)

    class product_naming(models.TextChoices):
        AFFINITY = "AFFINITY", "Affinity"
        FUNERAL = "FUNERAL", "Funeral"
        

    product_name = models.CharField(max_length=30, choices=product_naming.choices)
    product_code = models.CharField(max_length=4, editable=False)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='policies', null=True, editable=False)

    
    proposal_sign_date = models.DateField(validators=[proposal_sign_date])

    # 2) Attach the correct validator
    start_date = models.DateField(validators=[validate_first_day])

    agent = models.ForeignKey('agents.Agent', on_delete=models.PROTECT, related_name='policies')
    paypoint = models.ForeignKey('paypoints.Paypoint', on_delete=models.PROTECT, related_name='policies')
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='policies')
    current_month = models.DateField(default=timezone.localdate, editable=False)
    duration = models.PositiveIntegerField(editable=False, null=True, help_text="Elapsed months since start_date")
            
    #calculate the tota premiums required by the policy to date
    total_premium_due = models.DecimalField(max_digits=12, editable=False, decimal_places=2, null=True)
    total_premium_arrears = models.DecimalField(max_digits=12, editable=False, decimal_places=2, null=True)
    # ... keep your existing fields like contract_id, cover, etc.
    total_premium_received = models.DecimalField(max_digits=12, decimal_places=2,
                                                 default=Decimal('0.00'), editable=False)
    
    contract_premium = models.DecimalField(max_digits=6, decimal_places=2,
                                           editable=False, null=True)
    # Remove months_paid, months_in_arrears, policy_status from DB fields

    # Dynamic properties:

    
    @property
    def total_premium_arrears(self):
        if self.total_premium_due and self.total_premium_received:
            return self.total_premium_due - self.total_premium_received
        return Decimal('0.00')


    @property
    def months_paid(self):
        if self.contract_premium and self.total_premium_received:
            return round(self.total_premium_received / self.contract_premium, 2)
        return 0

    @property
    def months_in_arrears(self):
        if self.contract_premium and self.total_premium_due and self.total_premium_received:
            arrears = self.total_premium_due - self.total_premium_received
            return round(arrears / self.contract_premium, 2)
        return 0

    @property
    def policy_status(self):
        if self.months_in_arrears > 2 and self.months_paid >= 1:
            return "Policy Lapsed"
        elif self.months_in_arrears <= 2 and self.months_paid >= 1:
            return "Policy Active"
        elif self.months_in_arrears > 2 and self.months_paid < 1:
            return "NTU Non Payment"
        else:
            return "Policy Accepted"



       

    class PolicyFrequency(models.TextChoices):
        MONTHLY = 'M', 'Monthly'
        QUARTERLY = 'Q', 'Quarterly'
        HALF_YEARLY = 'H', 'Half-yearly'
        YEARLY = 'Y', 'Yearly'

    frequency = models.CharField(max_length=1, choices=PolicyFrequency.choices,
                                 default=PolicyFrequency.MONTHLY, db_index=True)

    class Cover(models.IntegerChoices):
        BASIC = 500, "$500"
        STANDARD = 1000, "$1000"
        PREMIA = 2000, "$2000"

    cover = models.PositiveIntegerField(choices=Cover.choices)

    

    
    def clean(self):
        if self.start_date and self.proposal_sign_date and self.start_date <= self.proposal_sign_date:
            raise ValidationError({"start_date": "Start date must be later than the proposal sign date."})
        

    
    
    @staticmethod
    def _first_of_month(d: date) -> date:
        return date(d.year, d.month, 1)


    def save(self, *args, **kwargs):
        # Normalize dates to day 1
        if self.start_date:
            self.start_date = self._first_of_month(self.start_date)

        cm = self.current_month or timezone.localdate()
        self.current_month = self._first_of_month(cm)

        # Months elapsed (non-negative)
        if self.start_date and self.current_month:
            months = (self.current_month.year - self.start_date.year) * 12 + \
                     (self.current_month.month - self.start_date.month)
            self.duration = max(months, 0)
        else:
            self.duration = 0

        # Premium per month by cover (use Decimal)
        cover_to_monthly = {
            self.Cover.BASIC:   Decimal('0.50'),
            self.Cover.STANDARD: Decimal('1.00'),
            self.Cover.PREMIA:  Decimal('2.00'),
        }
        monthly_rate = cover_to_monthly.get(self.cover)
        if monthly_rate is None:
            raise ValidationError({"cover": "Invalid cover amount."})

        # Period length and premium per period
        freq_to_months = {'M': 1, 'Q': 3, 'H': 6, 'Y': 12}
        period_len = freq_to_months[self.frequency]
        self.contract_premium = (monthly_rate * Decimal(str(period_len))).quantize(Decimal('0.01'))

        # Completed periods elapsed
        periods_elapsed = (self.duration // period_len)

        # Total premium due up to current_month
        self.total_premium_due = (self.contract_premium * Decimal(str(periods_elapsed))).quantize(Decimal('0.01'))

       

        # generate policy number
  
        if not self.contract_id:
            last_contract = Policy.objects.order_by('-contract_id').first()

            if last_contract:
                last_number = int(last_contract.contract_id[1:])  # remove 'P'
                new_number = last_number + 1
            else:
                new_number = 1

            self.contract_id = f"P{new_number:05d}"  # A0001 format



      #product code validations
        if self.product_name == self.product_naming.AFFINITY:
            self.product_code = "200"
        elif self.product_name == self.product_naming.FUNERAL:
            self.product_code = "300"
        else:
            raise ValidationError("Invalid product selected")

    


           



        super().save(*args, **kwargs)

    def __str__(self):
        return self.contract_id






