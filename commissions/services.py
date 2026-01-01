
# commissions/services.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

from django.db import transaction

from commissions.models import CommissionRecord
from policies.models import Policy

COMMISSION_RATE = Decimal("0.10")


def _first_of_month(d: date) -> date:
    return date(d.year, d.month, 1)


def compute_commission(premium) -> Decimal:
    prem = Decimal(premium or 0)
    return (prem * COMMISSION_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@transaction.atomic
def generate_commissions_for_month(commission_month: date) -> dict:
    """
    Create/Update CommissionRecord for ALL policies for the given month.
    Returns a summary dict with counts.
    Assumptions:
      - Policy has fields: contract_premium, agent (FK)
      - We include all policies; filter as needed (e.g., active only).
    """
    month = _first_of_month(commission_month)

    # If you only want active policies, add your status filter here.
    # Example (adjust to your model): Policy.objects.filter(overall_policy_status="Active")
    policies = Policy.objects.select_related("agent")

    created = 0
    updated = 0
    skipped = 0

    for p in policies:
        # Must have an agent to pay commission—skip otherwise
        if not getattr(p, "agent_id", None):
            skipped += 1
            continue

        commission_due = compute_commission(p.contract_premium)

        obj, was_created = CommissionRecord.objects.update_or_create(
            policy=p,
            commission_month=month,
            defaults={
                "agent": p.agent,
                "commission_due": commission_due,
            },
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {"created": created, "updated": updated, "skipped": skipped, "month": month}

