# commissions/views.py
from datetime import date
from decimal import Decimal
from io import BytesIO, StringIO
import csv

from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from commissions.models import CommissionRecord
from policies.models import Policy
from agents.models import Agent
from .serializers import CommissionRecordSerializer

RATE = Decimal("0.10")  # 10%


class CommissionRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints:
      - /api/commissions/                    -> list saved commission rows
      - /api/commissions/statement/          -> per agent & month (JSON/CSV/PDF/EMAIL, optional ?save=true)
    """
    serializer_class = CommissionRecordSerializer

    def get_queryset(self):
        return (CommissionRecord.objects
                .select_related("policy", "policy__client", "agent")
                .order_by("policy__contract_id", "commission_month"))

    # ---- helpers ----
    @staticmethod
    def _first_of_month(d: date) -> date:
        return date(d.year, d.month, 1)

    @staticmethod
    def _parse_month(raw: str):
        """YYYY-MM or YYYY-MM-DD -> first day of that month"""
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
    def _months_per_period(freq: str) -> int:
        return {"M": 1, "Q": 3, "H": 6, "Y": 12}[freq]

    @staticmethod
    def _monthly_rate(policy: Policy) -> Decimal:
        """
        contract_premium is per policy frequency period; convert to monthly.
        """
        cp = Decimal(policy.contract_premium or 0)
        months = CommissionRecordViewSet._months_per_period(policy.frequency)
        if months <= 0:
            return Decimal("0.00")
        return (cp / Decimal(months)).quantize(Decimal("0.01"))

    # ---- CSV/PDF builders ----
    def _build_rows_for_agent_month(self, agent: Agent, month_start: date, save=False):
        rows = []
        tot_prem = Decimal("0.00")
        tot_comm = Decimal("0.00")

        # DB-level filters
        policies = (
            Policy.objects
            .select_related("client", "paypoint", "agent")
            .filter(agent=agent)
            .filter(start_date__lte=month_start)  # started before commission month
            .filter(cancellation_request__status__isnull=True)  # not cancelled
            .order_by("contract_id")
        )

        # Filter commissionable policies in Python
        commissionable_policies = [p for p in policies if p.is_commissionable(month_start)]

        for p in commissionable_policies:
            monthly = self._monthly_rate(p)
            commission_due = (monthly * RATE).quantize(Decimal("0.01"))

            rows.append({
                "contract_id": p.contract_id,
                "client_name": str(p.client) if p.client_id else "",
                "status": getattr(p, "overall_policy_status", ""),
                "agent_code": agent.agent_code,
                "agent_name": f"{agent.agent_name} {agent.agent_surname}",
                "contract_premium": float(monthly),
                "commission_due": float(commission_due),
            })

            tot_prem += monthly
            tot_comm += commission_due

            if save:
                CommissionRecord.objects.get_or_create(
                    policy=p,
                    agent=agent,
                    commission_month=month_start,
                    defaults={"commission_due": commission_due}
                )

        return rows, float(tot_prem), float(tot_comm)

    def _csv(self, agent_code, agent_name, month_label, rows, tot_prem, tot_comm):
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(["Agent_code", agent_code])
        w.writerow(["Agent_name", agent_name])
        w.writerow(["Commission Month", month_label])
        w.writerow([])
        w.writerow(["List of clients"])
        w.writerow(["Contract_id", "Client_name", "Status", "Agent code", "Agent name", "Contract Premium", "Commission due"])
        for r in rows:
            w.writerow([r["contract_id"], r["client_name"], r["status"], r["agent_code"], r["agent_name"], r["contract_premium"], r["commission_due"]])
        w.writerow([])
        w.writerow(["Total", "", "", "", "", tot_prem, tot_comm])

        filename = f"commission_{agent_code}_{month_label}.csv".replace(" ", "_").lower()
        resp = HttpResponse(buf.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    def _pdf(self, agent_code, agent_name, month_label, rows, tot_prem, tot_comm):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        except Exception:
            return Response({"detail": "Install 'reportlab' for PDF export", "hint": "Use export=csv"}, status=501)

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
        styles = getSampleStyleSheet()
        elems = [
            Paragraph("<b>Commission Statement</b>", styles["Title"]),
            Spacer(1, 6),
            Paragraph(f"<b>Agent_code:</b> {agent_code}", styles["Normal"]),
            Paragraph(f"<b>Agent_name:</b> {agent_name}", styles["Normal"]),
            Paragraph(f"<b>Commission Month:</b> {month_label}", styles["Normal"]),
            Spacer(1, 10),
            Paragraph("<b>List of clients</b>", styles["Heading3"]), Spacer(1, 4)
        ]

        data = [["Contract_id", "Client_name", "Status", "Agent code", "Agent name", "Contract Premium", "Commission due"]]
        for r in rows:
            data.append([r["contract_id"], r["client_name"], r["status"], r["agent_code"], r["agent_name"], r["contract_premium"], r["commission_due"]])
        data.append(["", "", "", "", "", "", ""])
        data.append(["Total", "", "", "", "", f"{tot_prem}", f"{tot_comm}"])

        table = Table(data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#D0E9C6")),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ALIGN", (5,1), (6,-1), "RIGHT"),
            ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#F5F5F5")),
        ]))
        elems.append(table)
        doc.build(elems)

        filename = f"commission_{agent_code}_{month_label}.pdf".replace(" ", "_").lower()
        resp = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

    @action(detail=False, methods=["get"], url_path="statement")
    def statement(self, request):
        agent_id = request.query_params.get("agent_id")
        agent_code = request.query_params.get("agent_code")
        agent_name_param = request.query_params.get("agent")
        export = (request.query_params.get("export") or "json").lower().strip()
        save = (request.query_params.get("save") or "false").lower().strip() == "true"
        month_raw = request.query_params.get("month")

        month_start = self._parse_month(month_raw)
        if not month_start:
            return Response({"detail": "Invalid or missing 'month'. Use YYYY-MM or YYYY-MM-DD."}, status=400)
        month_label = month_start.strftime("%b-%y")

        agent = None
        if agent_id:
            try:
                agent = Agent.objects.get(id=int(agent_id))
            except Exception:
                return Response({"detail": "Invalid 'agent_id'."}, status=400)
        elif agent_code:
            agent = Agent.objects.filter(agent_code__iexact=agent_code.strip()).first()
        elif agent_name_param:
            agent = Agent.objects.filter(agent_name__icontains=agent_name_param.strip()).first()
        if not agent:
            return Response({"detail": "Agent not found. Use 'agent_id', 'agent_code' or 'agent' (name)."}, status=404)

        rows, tot_prem, tot_comm = self._build_rows_for_agent_month(agent, month_start, save=save)
        agent_label = agent.agent_code
        agent_full = f"{agent.agent_name} {agent.agent_surname}"

        if export == "csv":
            return self._csv(agent_label, agent_full, month_label, rows, tot_prem, tot_comm)
        if export == "pdf":
            return self._pdf(agent_label, agent_full, month_label, rows, tot_prem, tot_comm)
        if export == "email":
            if not getattr(agent, "email", None):
                return Response({"detail": "Agent has no email configured."}, status=400)
            pdf_resp = self._pdf(agent_label, agent_full, month_label, rows, tot_prem, tot_comm)
            content = pdf_resp.content
            filename = f"commission_{agent_label}_{month_label}.pdf".replace(" ", "_").lower()
            subject = f"Commission Statement - {month_label}"
            body = f"Dear {agent.agent_name},\n\nPlease find attached your commission statement for {month_label}.\n\nRegards,\nZimnat Life Assurance"
            email = EmailMessage(subject, body, getattr(settings, "DEFAULT_FROM_EMAIL", None), [agent.email])
            email.attach(filename, content, "application/pdf")
            email.send(fail_silently=False)
            return Response({"detail": f"Emailed statement to {agent.email}", "agent_code": agent_label, "month": month_label})

        return Response({
            "agent_code": agent_label,
            "agent_name": agent_full,
            "commission_month": month_label,
            "clients": rows,
            "count": len(rows),
            "total_monthly_premium": tot_prem,
            "total_commission_due": tot_comm,
            "saved": save,
        })


# ---- Optional admin view for manual trigger ----
from django.shortcuts import render
from django.contrib import messages
from commissions.services import generate_commissions_for_month, compute_commission

def run_commissions_view(request):
    agents = Agent.objects.all()

    if request.method == "POST":
        month_str = request.POST.get("month")
        agent_id = request.POST.get("agent_id")

        if not month_str:
            messages.error(request, "Please select a month.")
        else:
            try:
                year, month = map(int, month_str.split("-"))
                month_start = date(year, month, 1)
            except Exception:
                messages.error(request, "Invalid month format.")
            else:
                if agent_id:  # specific agent
                    agent = Agent.objects.filter(id=int(agent_id)).first()
                    if not agent:
                        messages.error(request, "Selected agent not found.")
                    else:
                        created = updated = skipped = 0
                        policies = agent.policy_set.all()
                        for p in policies:
                            if not p.is_commissionable(month_start):
                                skipped += 1
                                continue
                            commission_due = compute_commission(p.contract_premium)
                            obj, was_created = CommissionRecord.objects.update_or_create(
                                policy=p,
                                commission_month=month_start,
                                defaults={"agent": p.agent, "commission_due": commission_due}
                            )
                            if was_created:
                                created += 1
                            else:
                                updated += 1
                        messages.success(
                            request,
                            f"Commissions for {agent.agent_code} ({month_start:%b %Y}): "
                            f"{created} created, {updated} updated, {skipped} skipped."
                        )
                else:  # all agents
                    result = generate_commissions_for_month(month_start)
                    messages.success(
                        request,
                        f"All agents commissions for {month_start:%b %Y}: "
                        f"{result['created']} created, {result['updated']} updated, {result['skipped']} skipped."
                    )

    return render(request, "admin/commissions/run_monthly_commission.html", {"agents": agents})
