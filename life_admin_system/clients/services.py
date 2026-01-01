import os
import csv
import openpyxl
from .models import Client

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
            if not row or len(row) < 9:
                raise ValueError("Not enough columns")
            
            client_name, client_surname, id_number, dob, email, phone_number, street_address, location_address, city_address = row[:9]

            # Detect duplicates in the same file
            key = (client_name, client_surname, id_number, dob, email, phone_number, street_address, location_address, city_address)
            if key in seen:
                raise ValueError("Duplicate agent in file")
            seen.add(key)

            # Check duplicates in DB
            if Client.objects.filter(client_name=client_name,
                                     client_surname=client_surname, id_number=id_number,
                                     dob=dob, email=email, phone_number=phone_number,
                                     street_address=street_address, location_address=location_address,
                                     city_address=city_address).exists():
                raise ValueError("Duplicate agent in database")

            # create Client
            Client.objects.create(
                client_name=client_name,
                client_surname=client_surname, id_number=id_number,
                dob=dob, email=email, phone_number=phone_number,
                street_address=street_address, location_address=location_address,
                city_address=city_address
            )

        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    return errors
