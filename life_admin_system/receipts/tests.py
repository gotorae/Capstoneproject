from django.test import TestCase
from decimal import Decimal
from django.utils import timezone

from receipts.models import PremiumReceipt
from policies.models import Policy
from clients.models import Client
from agents.models import Agent
from paypoints.models import Paypoint
from access.models import Administrator

class ReceiptAggregationTest(TestCase):

    def setUp(self):
        self.user = Administrator.objects.create_user(
            email="user@test.com",
            password="pass123"
        )

        self.client = Client.objects.create(
            first_name="Jane",
            last_name="Doe",
            national_id="63-999999Z63"
        )

        self.agent = Agent.objects.create(
            name="Agent",
            surname="One",
            branch="Bulawayo"
        )

        self.paypoint = Paypoint.objects.create(name="Branch")

        self.policy = Policy.objects.create(
            client=self.client,
            agent=self.agent,
            paypoint=self.paypoint,
            product_code="LIFE02",
            product_name="Funeral Cover",
            start_date=timezone.now().date(),
            duration=6,
            frequency="Monthly",
            total_premium_due=Decimal("600.00"),
            created_by=self.user
        )

    def test_receipt_number_auto_generated(self):
        receipt = PremiumReceipt.objects.create(
            policy=self.policy,
            amount_received=Decimal("100.00"),
            receipted_by=self.user
        )
        self.assertTrue(receipt.receipt_number.startswith("Rec"))

    def test_policy_total_updates(self):
        PremiumReceipt.objects.create(
            policy=self.policy,
            amount_received=Decimal("200.00"),
            receipted_by=self.user
        )
        PremiumReceipt.objects.create(
            policy=self.policy,
            amount_received=Decimal("150.00"),
            receipted_by=self.user
        )

        self.policy.refresh_from_db()
        self.assertEqual(self.policy.total_received, Decimal("350.00"))

