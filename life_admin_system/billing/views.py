
# billing/views.py
from datetime import date, timedelta
from io import BytesIO, StringIO
import csv

from django.http import HttpResponse
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from billing.models import BillingRecord
from policies.models import Policy
from .serializers import BillingRecordSerializer  # minimal serializer you already have


class BillingRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints:
      - /api/billing-records/                    -> list all billing records
      - /api/billing-records/active-policies/   -> billing rows whose policy is Overall 'Active'
      - /api/billing-records/statement/         -> billing statement per paypoint & month (JSON/CSV/PDF via ?export=)
    """
    serializer_class = BillingRecordSerializer

    # ---------- base queryset ----------
    def get_queryset(self):
        # Deterministic ordering helps pagination & exports
        return (BillingRecord.objects
                .select_related("policy", "policy__client", "policy__paypoint")
                .order_by("policy__contract_id", "billing_month"))

    # ---------- simple filter: overall active ----------
    @action(detail=False, methods=["get"], url_path="active-policies")
    def active_policies(self, request):
        """
        Return billing records where linked policy.overall_policy_status == 'Active'
        """
        all_records = list(self.get_queryset())
        filtered = [
            br for br in all_records
            if br.policy and br.policy.overall_policy_status == "Active"
        ]

        page = self.paginate_queryset(filtered)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)

        ser = self.get_serializer(filtered, many=True)
        return Response(ser.data)

    # ---------- helpers ----------
    @staticmethod
    def _first_of_month(d: date) -> date:
        return date(d.year, d.month, 1)

    @staticmethod
    def _month_bounds(month_start: date):
        """Return (start, end) for the month."""
        if month_start.month == 12:
            next_month_start = date(month_start.year + 1, 1, 1)
        else:
            next_month_start = date(month_start.year, month_start.month + 1, 1)
        return month_start, next_month_start - timedelta(days=1)

    @staticmethod
    def _parse_month_param(raw: str):
        """Accept YYYY-MM or YYYY-MM-DD; return first day of that month or None."""
        if not raw:
            return None
        d = parse_date(raw)
        if d is None:
            try:
                y, m = map(int, raw.split("-"))
                d = date(y, m, 1)
            except Exception:
                return None
        return date(d.year, d.month, 1)

    @staticmethod
    def _status_in_month(policy: Policy, month_start: date, month_end: date):
        """
        Return 'Active' or 'proposal accepted' for the target month; None to exclude.
        Rules:
          - Exclude if claim/cancellation effective on/before month_end.
          - Exclude if policy starts after month_end.
          - If it's the inception month and <1 period paid and no arrears, mark 'proposal accepted'.
          - Otherwise mark 'Active'.
        """
        claim_effective = getattr(policy, "claim_effective_date", None)
        if claim_effective and claim_effective <= month_end:
            return None

        cancel_effective = getattr(policy, "cancellation_effective_date", None)
        if cancel_effective and cancel_effective <= month_end:
            return None

        if policy.start_date and policy.start_date > month_end:
            return None

        # inception month?
        if policy.start_date:
            start_m = date(policy.start_date.year, policy.start_date.month, 1)
            if start_m == month_start:
                try:
                    if (policy.months_paid or 0) < 1 and (policy.months_in_arrears or 0) <= 0:
                        return "proposal accepted"
                except Exception:
                    return "proposal accepted"

        return "Active"

    # ---------- CSV builder ----------
    def _build_csv_response(self, paypoint_label: str, month_label: str, rows: list, total: float):
        """
        CSV layout matching your example.
        """
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

    # ---------- PDF builder ----------
    def _build_pdf_response(self, paypoint_label: str, month_label: str, rows: list, total: float):
        """
        Lightweight PDF using reportlab. If reportlab is missing, return 501 with guidance.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        except Exception:
            return Response(
                {
                    "detail": "PDF export requires 'reportlab'. Install: pip install reportlab",
                    "hint": "Or use export=csv",
                },
                status=501,
            )

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

        # Table
        data = [["Contract_id", "Client_name", "Status", "Contract Premium"]]
        for r in rows:
            data.append([r["contract_id"], r["client_name"], r["status"], r["contract_premium"]])
        data.append(["", "", "", ""])
        data.append(["Total", "", "", f"{total}"])

        table = Table(data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DFF0D8")),  # header bg
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F5F5F5")),  # total row bg
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

    # ---------- statement endpoint ----------
    @action(detail=False, methods=["get"], url_path="statement")
    def statement(self, request):
        """
        Build a billing statement for a paypoint and month.

        Query params (one of the first three is required):
          - paypoint_id=<int>       (preferred)
          - paypoint_code=<str>     (exact code, case-insensitive)
          - paypoint=<name>         (human name, partial / case-insensitive)
          - month=YYYY-MM or YYYY-MM-DD
          - export=json|csv|pdf     (default json)  <-- use 'export', not 'format'
        """
        paypoint_id = request.query_params.get("paypoint_id")
        paypoint_code = request.query_params.get("paypoint_code")
        paypoint_name = request.query_params.get("paypoint") or request.query_params.get("paypoint_name")
        export = (request.query_params.get("export") or "json").lower().strip()  # << changed from 'format'
        month_raw = request.query_params.get("month")

        # Parse month
        month_start = self._parse_month_param(month_raw)
        if not month_start:
            return Response({"detail": "Invalid or missing 'month'. Use YYYY-MM or YYYY-MM-DD."}, status=400)
        month_start, month_end = self._month_bounds(month_start)
        month_label = month_start.strftime("%b-%y")

        # Base policies queryset
        policies_qs = Policy.objects.select_related("client", "paypoint").order_by("contract_id")

        # Filter by paypoint
        paypoint_label = None
        if paypoint_id:
            try:
                policies_qs = policies_qs.filter(paypoint_id=int(paypoint_id))
                paypoint_label = f"id:{int(paypoint_id)}"
            except ValueError:
                return Response({"detail": "Invalid 'paypoint_id'. Must be an integer."}, status=400)

        elif paypoint_code:
            # Unique code; saved lowercase in model.save(); match case-insensitively
            policies_qs = policies_qs.filter(paypoint__paypoint_code__iexact=paypoint_code.strip())
            paypoint_label = paypoint_code.strip()

        elif paypoint_name:
            # Human name; partial, case-insensitive
            policies_qs = policies_qs.filter(paypoint__paypoint_name__icontains=paypoint_name.strip())
            paypoint_label = paypoint_name.strip()

        else:
            return Response({"detail": "Provide one of: 'paypoint_id', 'paypoint_code', or 'paypoint' (name)."}, status=400)

        # Build rows (only Active or proposal accepted for the given month)
        rows = []
        total = 0.0
        resolved_label = None

        for p in policies_qs:
            if resolved_label is None and p.paypoint_id:
                resolved_label = str(p.paypoint)  # __str__ returns paypoint_name

            status_label = self._status_in_month(p, month_start, month_end)
            if status_label not in ("Active", "proposal accepted"):
                continue

            premium = float(p.contract_premium or 0.0)
            total += premium

            rows.append({
                "contract_id": p.contract_id,
                "client_name": str(p.client) if p.client_id else "",
                "status": status_label,
                "contract_premium": premium,  # numeric (0.5 / 1.0)
            })

        # If nothing matched to resolve a pretty label, echo the input
        paypoint_label = resolved_label or paypoint_label or "(unknown)"

        # Return by export format (avoid DRF's built-in ?format=)
        if export == "csv":
            return self._build_csv_response(paypoint_label, month_label, rows, total)
        if export == "pdf":
            return self._build_pdf_response(paypoint_label, month_label, rows, total)

        # Default: JSON
        return Response({
            "paypoint": paypoint_label,
            "billing_month": month_label,
            "clients": rows,
            "count": len(rows),
            "total_contract_premium": total,
        })

