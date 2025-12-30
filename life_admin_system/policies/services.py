import os
import csv
import openpyxl
from django.core.exceptions import ObjectDoesNotExist
from .models import Policy
from agents.models import Agent
from paypoints.models import Paypoint
from clients.models import Client


def process_upload(upload):
    """
    Process an uploaded file (Excel or CSV) and create policies.
    Returns a list of errors per row.
    """
    errors = []
    filename = upload.file.path
    ext = os.path.splitext(filename)[1].lower()

    seen = set()  # Track duplicates within the file

    # -------------------------------------------------
    # Read file
    # -------------------------------------------------
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
            if not row or len(row) < 10:
                raise ValueError("Not enough columns")

            (
                product_name,
                start_date,
                proposal_sign_date,
                beneficiary_name,
                beneficiary_id,
                agent_full_name,
                paypoint_name,
                client_full_name,
                frequency,
                cover,
            ) = row[:10]

            # =================================================
            # AGENT (agent_name + agent_surname)
            # =================================================
            agent_parts = str(agent_full_name).strip().split()
            if len(agent_parts) < 2:
                raise ValueError("Agent must have name and surname")

            agent_name = agent_parts[0]
            agent_surname = " ".join(agent_parts[1:])

            try:
                agent = Agent.objects.get(
                    agent_name__iexact=agent_name,
                    agent_surname__iexact=agent_surname
                )
            except ObjectDoesNotExist:
                raise ValueError(f"Agent '{agent_full_name}' not found")

            # =================================================
            # PAYPOINT (paypoint_name)
            # =================================================
            try:
                paypoint = Paypoint.objects.get(
                    paypoint_name__iexact=str(paypoint_name).strip()
                )
            except ObjectDoesNotExist:
                raise ValueError(f"Paypoint '{paypoint_name}' not found")

            # =================================================
            # CLIENT (client_name + client_surname)
            # =================================================
            client_parts = str(client_full_name).strip().split()
            if len(client_parts) < 2:
                raise ValueError("Client must have name and surname")

            client_name = client_parts[0]
            client_surname = " ".join(client_parts[1:])

            try:
                client = Client.objects.get(
                    client_name__iexact=client_name,
                    client_surname__iexact=client_surname
                )
            except ObjectDoesNotExist:
                raise ValueError(f"Client '{client_full_name}' not found")

            # =================================================
            # FREQUENCY
            # =================================================
            frequency_map = {
                "monthly": "M",
                "quarterly": "Q",
                "half-yearly": "H",
                "half yearly": "H",
                "yearly": "Y",
                "annual": "Y",
            }

            frequency = frequency_map.get(str(frequency).lower().strip())
            if not frequency:
                raise ValueError(f"Invalid frequency '{frequency}'")

            # =================================================
            # COVER
            # =================================================
            cover = int(cover)
            if cover not in [500, 1000, 2000]:
                raise ValueError("Invalid cover amount")

            # =================================================
            # DUPLICATE CHECK (file)
            # =================================================
            file_key = (
                product_name,
                start_date,
                proposal_sign_date,
                beneficiary_id,
                agent.id,
                paypoint.id,
                client.id,
                frequency,
                cover,
            )

            if file_key in seen:
                raise ValueError("Duplicate policy in file")
            seen.add(file_key)

            # =================================================
            # DUPLICATE CHECK (database)
            # =================================================
            if Policy.objects.filter(
                product_name=str(product_name).upper(),
                start_date=start_date,
                proposal_sign_date=proposal_sign_date,
                beneficiary_id=beneficiary_id,
                agent=agent,
                paypoint=paypoint,
                client=client,
                frequency=frequency,
                cover=cover,
            ).exists():
                raise ValueError("Duplicate policy in database")

            # =================================================
            # CREATE POLICY
            # =================================================
            Policy.objects.create(
                product_name=str(product_name).upper(),
                start_date=start_date,
                proposal_sign_date=proposal_sign_date,
                beneficiary_name=beneficiary_name,
                beneficiary_id=beneficiary_id,
                agent=agent,
                paypoint=paypoint,
                client=client,
                frequency=frequency,
                cover=cover,
            )

        except Exception as e:
            errors.append(f"Row {i}: {e}")

    return errors
