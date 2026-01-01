
# models.py
from decimal import Decimal
from datetime import date
from django.db import models, transaction
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum

class Agent(models.Model):
    agent_code = models.CharField(max_length=6, unique=True, db_index=True)
    agent_name = models.CharField(max_length=200, blank=False)
    agent_surname = models.CharField(max_length=200, blank=False)
    branch = models.CharField(max_length=100, blank=False)
    date_joining = models.DateField()

    def __str__(self):
        return f"{self.agent_code} : {self.agent_name} {self.agent_surname}"
    
class Paypoint(models.Model):
    paypoint_code = models.CharField(max_length=100, unique=True, db_index=True)
    paypoint_name = models.CharField(max_length=200)
    date_joined = models.DateField()

    def __str__(self):
        return self.paypoint_name
    

phone_regex = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="Phone number must be 7–15 digits and may start with +"
)
    

class Client(models.Model):
    client_code = models.CharField(max_length=10, unique=True, db_index=True)
    client_name = models.CharField(max_length=200)
    client_surname = models.CharField(max_length=200)
    id_number = models.CharField(max_length=12, unique=True)
    dob = models.DateField()
    email= models.EmailField(unique=True)
    phone_number = models.CharField(max_length=16, validators=[phone_regex])

    def __str__(self):
        return f'{self.client_name} {self.client_surname}'
    

# --- keep Agent, Paypoint, Client as you have them ---

# 1) Field-level validator that accepts a *value*
def validate_first_day(value):
    if value.day != 1:
        raise ValidationError("Start date must be the first day of the month.")
    

def validate_status(self):
        if self.months_in_arrears <-2 and self.months_paid > 1:
            return "Policy Lapsed"
        elif self.months_in_arrears >=-2 and self.months_paid >1:
            return "Policy active"
        elif self.months_in_arrears <-2 and self.months_paid <1:
            return "NTU Non payment"
        else:
            return "Policy accepted" 

class Policy(models.Model):
    contract_id = models.CharField(max_length=10, unique=True, db_index=True)
    product_name = models.CharField(max_length=30)
    product_code = models.CharField(max_length=4)

    proposal_sign_date = models.DateField()

    # 2) Attach the correct validator
    start_date = models.DateField(validators=[validate_first_day])

    agent = models.ForeignKey('Agent', on_delete=models.PROTECT, related_name='policies')
    paypoint = models.ForeignKey('Paypoint', on_delete=models.PROTECT, related_name='policies')
    client = models.ForeignKey('Client', on_delete=models.PROTECT, related_name='policies')

    # ⚠️ Remove this — it creates a circular dependency and isn’t needed
    # premium_received = models.ForeignKey(PremiumReceipt, on_delete=models.PROTECT)

    current_month = models.DateField(default=timezone.localdate, editable=False)
    duration = models.PositiveIntegerField(editable=False, null=True, help_text="Elapsed months since start_date")
    total_premium_due = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True)

    # Optional: running total at policy level (recommended)
    total_premium_received = models.DecimalField(max_digits=12, decimal_places=2,
                                                 default=Decimal('0.00'), editable=False)
    
    #calculate the tota premiums required by the policy to date
    total_premium_due = models.DecimalField(max_digits=12, editable=False, decimal_places=2, null=True)
    total_premium_arrears = models.DecimalField(max_digits=12, editable=False, decimal_places=2, null=True)
    # ... keep your existing fields like contract_id, cover, etc.
    total_premium_received = models.DecimalField(max_digits=12, decimal_places=2,
                                                 default=Decimal('0.00'), editable=False)
    total_premium_due = models.DecimalField(max_digits=12, decimal_places=2,
                                            editable=False, null=True)
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
        if self.months_in_arrears < -2 and self.months_paid > 1:
            return "Policy Lapsed"
        elif self.months_in_arrears >= -2 and self.months_paid > 1:
            return "Policy Active"
        elif self.months_in_arrears < -2 and self.months_paid < 1:
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

    contract_premium = models.DecimalField(max_digits=6, decimal_places=2, editable=False, null=True)

    
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

       

        super().save(*args, **kwargs)

    def __str__(self):
        return self.contract_id





class PremiumReceipt(models.Model):
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=8, unique=True)
    amount_received = models.DecimalField(max_digits=7, decimal_places=2)
    date_received = models.DateTimeField(default=timezone.now)

    # optional default for extra safety
    total_received = models.DecimalField(max_digits=10, decimal_places=2,
                                         default=Decimal('0.00'), editable=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # compute cumulative BEFORE insert so NOT NULL is satisfied
            prev_total = (PremiumReceipt.objects
                          .filter(policy_id=self.policy_id)
                          .aggregate(total=Sum('amount_received'))['total'] or Decimal('0.00'))
            self.total_received = prev_total + (self.amount_received or Decimal('0.00'))

            # insert/update this receipt
            super().save(*args, **kwargs)

            # update policy running total WITHOUT invoking Policy.save()
            Policy.objects.filter(pk=self.policy_id).update(
                total_premium_received=self.total_received
            )

    def delete(self, *args, **kwargs):
        policy_id = self.policy_id
        with transaction.atomic():
            super().delete(*args, **kwargs)
            new_total = (PremiumReceipt.objects
                         .filter(policy_id=policy_id)
                         .aggregate(total=Sum('amount_received'))['total'] or Decimal('0.00'))
            Policy.objects.filter(pk=policy_id).update(
                total_premium_received=new_total
            )

    def __str__(self):
        return f"{self.receipt_number} • {self.total_received}"
