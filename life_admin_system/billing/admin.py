
# billing/admin.py
from datetime import date
from io import BytesIO, StringIO
import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from billing.models import BillingRecord


@admin.register(BillingRecord)
class BillingRecordAdmin(admin.ModelAdmin):
    """
    Django Admin for BillingRecord:
    - list, search, filters
    - export selected rows to CSV/PDF (actions)
    """
    list_display = (
        "id",
        "billing_month",
        "contract_id",
        "client_name",
        "policy_status",
        "contract_premium",
        "paypoint_name",
        "created_at",
    )
    list_filter = (
        "billing_month",
        "created_at",
        "policy__paypoint",
    )
    date_hierarchy = "billing_month"

    # Enables search by contract id, client name, paypoint name
    search_fields = (
        "policy__contract_id",
        "policy__client__first_name",
        "policy__client__last_name",
        "policy__paypoint__paypoint_name",
        "policy__paypoint__paypoint_code",
    )

    # Useful admin actions
    actions = ["export_selected_to_csv", "export_selected_to_pdf"]

    # ---- display helpers (avoid nested attribute errors) ----
    def contract_id(self, obj: BillingRecord):
        try:
            return obj.policy.contract_id
        except Exception:
            return ""

    contract_id.short_description = "Contract ID"

    def client_name(self, obj: BillingRecord):
        try:
            return str(obj.policy.client)
        except Exception:
            return ""

    client_name.short_description = "Client name"

    def paypoint_name(self, obj: BillingRecord):
        try:
            return str(obj.policy.paypoint)  # Paypoint.__str__ returns paypoint_name
        except Exception:
            return ""

    paypoint_name.short_description = "Pay point"

    def policy_status(self, obj: BillingRecord):
        try:
            # Prefer overall status
            return obj.policy.overall_policy_status
        except Exception:
            return ""

    policy_status.short_description = "Status"

    def contract_premium(self, obj: BillingRecord):
        try:
            prem = obj.policy.contract_premium
            return f"{prem:.2f}" if prem is not None else ""
        except Exception:
            return ""

    contract_premium.short_description = "Contract Premium"

    # ---- CSV/PDF exports as admin actions ----
    def _rows_from_queryset(self, queryset):
        """
        Build export rows matching your statement layout.
        """
        rows = []
        total = 0.0

        for br in queryset.select_related("policy", "policy__client", "policy__paypoint"):
            p = br.policy
            if not p:
                # Skip records missing policy
                continue

            status_label = p.overall_policy_status or ""
            premium = float(p.contract_premium or 0.0)
            total += premium

            rows.append({
                "contract_id": p.contract_id,
                "client_name": str(p.client) if p.client_id else "",
                "status": status_label,
                "contract_premium": premium,
                "billing_month": br.billing_month,
                "paypoint": str(p.paypoint) if p.paypoint_id else "",
            })

        return rows, total

    def export_selected_to_csv(self, request, queryset):
        """
        Admin action: Export selected BillingRecord rows to CSV.
        """
        rows, total = self._rows_from_queryset(queryset)
        # If multiple paypoints/months are mixed, just pick first labels for header
        paypoint_label = rows[0]["paypoint"] if rows else "(mixed)"
        month_label = rows[0]["billing_month"].strftime("%b-%y") if rows and rows[0]["billing_month"] else ""

        buf = StringIO()
        w = csv.writer(buf)

        w.writerow(["Pay point name", paypoint_label])
        w.writerow(["billing Month", month_label])
        w.writerow([])
        w.writerow(["List of clients"])
        w.writerow(["Contract_id", "Client_name", "Status", "Contract Premium"])
        for r in rows:
            w.writerow([r["contract_id"], r["client_name"], r["status"], r["contract_premium"]])
        w.writerow([])
        w.writerow(["Total", "", "", total])

        csv_data = buf.getvalue()
        buf.close()

        filename = f"billing_{paypoint_label}_{month_label}.csv".replace(" ", "_").lower()
        response = HttpResponse(csv_data, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    export_selected_to_csv.short_description = "Export selected to CSV"

    def export_selected_to_pdf(self, request, queryset):
        """
        Admin action: Export selected BillingRecord rows to PDF (reportlab).
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        except Exception:
            self.message_user(request, "PDF export requires 'reportlab'. Install: pip install reportlab", level="error")
            return None

        rows, total = self._rows_from_queryset(queryset)
        paypoint_label = rows[0]["paypoint"] if rows else "(mixed)"
        month_label = rows[0]["billing_month"].strftime("%b-%y") if rows and rows[0]["billing_month"] else ""

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=16 * mm, rightMargin=16 * mm, topMargin=16 * mm, bottomMargin=16 * mm
        )
        styles = getSampleStyleSheet()
        elems = []

        title = Paragraph("<b>Billing Statement</b>", styles["Title"])
        header1 = Paragraph(f"<b>Pay point name:</b> {paypoint_label}", styles["Normal"])
        header2 = Paragraph(f"<b>Billing Month:</b> {month_label}", styles["Normal"])

        elems.extend([title, Spacer(1, 6), header1, header2, Spacer(1, 10)])

        data = [["Contract_id", "Client_name", "Status", "Contract Premium"]]
        for r in rows:
            data.append([r["contract_id"], r["client_name"], r["status"], r["contract_premium"]])
        data.append(["", "", "", ""])
        data.append(["Total", "", "", f"{total}"])

        table = Table(data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DFF0D8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F5F5F5")),
        ]))

        elems.append(Paragraph("<b>List of clients</b>", styles["Heading3"]))
        elems.append(Spacer(1, 4))
        elems.append(table)

        doc.build(elems)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        filename = f"billing_{paypoint_label}_{month_label}.pdf".replace(" ", "_").lower()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    export_selected_to_pdf.short_description = "Export selected to PDF"
