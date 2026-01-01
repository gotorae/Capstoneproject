from django.test import TestCase
from decimal import Decimal
from django.utils import timezone

from policies.models import Policy
from clients.models import Client
from agents.models import Agent
from paypoints.models import Paypoint
from access.models import Administrator

class PolicyModelTest(TestCase):

    def setUp(self):
        self.user = Administrator.objects.create_user(
            email="admin@test.com",
            password="pass123"
        )

        self.client = Client.objects.create(
            first_name="John",
            last_name="Doe",
            national_id="12-123456A12"
        )

        self.agent = Agent.objects.create(
            name="Test",
            surname="Agent",
            branch="Harare"
        )

        self.paypoint = Paypoint.objects.create(
            name="Main Office"
        )

        self.policy = Policy.objects.create(
            client=self.client,
            agent=self.agent,
            paypoint=self.paypoint,
            product_code="LIFE01",
            product_name="Life Cover",
            start_date=timezone.now().date(),
            duration=12,
            frequency="Monthly",
            total_premium_due=Decimal("1200.00"),
            created_by=self.user
        )

    def test_policy_creation(self):
        self.assertEqual(self.policy.product_code, "LIFE01")
        self.assertEqual(self.policy.total_received, Decimal("0.00"))

    def test_string_representation(self):
        self.assertTrue(str(self.policy))
