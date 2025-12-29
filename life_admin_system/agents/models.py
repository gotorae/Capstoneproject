# models.py
from decimal import Decimal
from datetime import date
from django.db import models, transaction
from django.utils import timezone
from .validators import validate_date_joining



class Agent(models.Model):
    agent_code = models.CharField(max_length=6, unique=True, db_index=True, editable=False)
    agent_name = models.CharField(max_length=200)
    agent_surname = models.CharField(max_length=200)

    class Branch_option(models.TextChoices):
        HARARE = "HARARE", "Harare"
        MUTARE = "MUTARE", "Mutare"
        KWEKWE = "KWEKWE", "Kwekwe"
        BULAWAYO = "BULAWAYO", "Bulawayo"
        MASVINGO = "MASVINGO", "Masvingo"
        VICTORIA_FALLS = "VICTORIA_FALLS", "Victoria Falls"

    

    branch = models.CharField(max_length=100, choices=Branch_option.choices, db_index=True)

    

    date_joining = models.DateField(validators=[validate_date_joining])

    def save(self, *args, **kwargs):
        if not self.agent_code:
            last_agent = Agent.objects.order_by('-agent_code').first()

            if last_agent:
                last_number = int(last_agent.agent_code[1:])  # remove 'A'
                new_number = last_number + 1
            else:
                new_number = 1

            self.agent_code = f"A{new_number:04d}"  # A0001 format

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.agent_name} {self.agent_surname}"


from django.conf import settings

class Upload(models.Model):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    file = models.FileField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approved_uploads"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    is_rejected = models.BooleanField(default=False)
    reject_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

