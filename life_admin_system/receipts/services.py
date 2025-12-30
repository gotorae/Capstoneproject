from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
import os
import csv
import openpyxl
from .models import PremiumReceipt
from policies.models import Policy

def process_upload(upload):
    errors = []
    filename = upload.file.path
    ext = os.path.splitext(filename)[1].lower()

    # Read file
    if ext in ['.xlsx', '.xls']:
        wb = openpyxl.load_workbook(filename)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=2, values_only=True))
    elif ext == '.csv':
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)[1:]
    else:
        raise ValueError("Unsupported file format. Use Excel or CSV.")

    for i, row in enumerate(rows, start=2):
        try:
            if not row or len(row) < 2:
                raise ValueError("Not enough columns")

            policy_code, amount_received = row[:2]

            # Find the existing policy
            try:
                policy = Policy.objects.get(contract_id__iexact=str(policy_code).strip())
            except ObjectDoesNotExist:
                raise ValueError(f"Policy '{policy_code}' not found")

            # Create PremiumReceipt
            PremiumReceipt.objects.create(
                policy=policy,
                amount_received=Decimal(amount_received),
            )

        except Exception as e:
            errors.append(f"Row {i}: {e}")

    return errors
