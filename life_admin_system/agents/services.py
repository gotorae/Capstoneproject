import os
import csv
import openpyxl
from .models import Agent

def process_upload(upload):
    """
    Process an uploaded file (Excel or CSV) and create agents.
    Returns a list of errors per row.
    """
    errors = []
    filename = upload.file.path
    ext = os.path.splitext(filename)[1].lower()  # get file extension

    # Track duplicates within the file
    seen = set()

    if ext in ['.xlsx', '.xls']:
        # Excel file
        wb = openpyxl.load_workbook(filename)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=2, values_only=True))  # skip header
    elif ext == '.csv':
        # CSV file
        with open(filename, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)[1:]  # skip header
    else:
        raise ValueError("Unsupported file format. Use Excel or CSV.")

    for i, row in enumerate(rows, start=2):
        try:
            if not row or len(row) < 4:
                raise ValueError("Not enough columns")
            
            agent_name, agent_surname, branch, date_joining = row[:4]

            # Detect duplicates in the same file
            key = (agent_name, agent_surname, branch)
            if key in seen:
                raise ValueError("Duplicate agent in file")
            seen.add(key)

            # Check duplicates in DB
            if Agent.objects.filter(agent_name=agent_name, agent_surname=agent_surname, branch=branch).exists():
                raise ValueError("Duplicate agent in database")

            # create agent
            Agent.objects.create(
                agent_name=agent_name,
                agent_surname=agent_surname,
                branch=branch,
                date_joining=date_joining
            )

        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    return errors
