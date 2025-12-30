from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .models import Policy
from .serializers import PolicySerializers


class PolicyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializers
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    # If you want GET list without login, uncomment the next line:
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # If you want everything to require login, use:
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["contract_id", "product_name", "frequency", "created_by", "created_date"]
    ordering_fields = ["contract_id", "product_name", "frequency", "proposal_sign_date", "created_by", "created_date"]


class PolicyDetailAPIView(generics.UpdateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializers
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # Optional but explicit:

# Create your views here.


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Upload

@login_required
def upload_file(request):
    if request.method == "POST":
        Upload.objects.create(
            file=request.FILES["file"],
            uploaded_by=request.user
        )
        return redirect("upload_success")
    


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.http import HttpResponse
import csv
import openpyxl
from .models import Policy


class PolicyExportCSVAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Policy.objects.all()

        # Optional filters
        agent = request.GET.get("agent")
        paypoint = request.GET.get("paypoint")

        if agent:
            queryset = queryset.filter(agent_id=agent)
        if paypoint:
            queryset = queryset.filter(paypoint_id=paypoint)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="policies.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Contract ID",
            "Product",
            "Agent",
            "Paypoint",
            "Client",
            "Start Date",
            "Frequency",
            "Cover",
            "Contract Premium",
            "Total Due",
            "Total Received",
            "Arrears",
            "Status",
        ])

        for p in queryset:
            writer.writerow([
                p.contract_id,
                p.product_name,
                f"{p.agent.agent_name} {p.agent.agent_surname}",
                p.paypoint.paypoint_name,
                f"{p.client.client_name} {p.client.client_surname}",
                p.start_date,
                p.get_frequency_display(),
                p.cover,
                p.contract_premium,
                p.total_premium_due,
                p.total_premium_received,
                p.total_premium_arrears,
                p.overall_policy_status,
            ])

        return response
    


class PolicyExportExcelAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Policy.objects.all()

        # Optional filters
        agent = request.GET.get("agent")
        paypoint = request.GET.get("paypoint")

        if agent:
            queryset = queryset.filter(agent_id=agent)
        if paypoint:
            queryset = queryset.filter(paypoint_id=paypoint)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Policies"

        headers = [
            "Contract ID",
            "Product",
            "Agent",
            "Paypoint",
            "Client",
            "Start Date",
            "Frequency",
            "Cover",
            "Contract Premium",
            "Total Due",
            "Total Received",
            "Arrears",
            "Status",
        ]
        ws.append(headers)

        for p in queryset:
            ws.append([
                p.contract_id,
                p.product_name,
                f"{p.agent.agent_name} {p.agent.agent_surname}",
                p.paypoint.paypoint_name,
                f"{p.client.client_name} {p.client.client_surname}",
                str(p.start_date),
                p.get_frequency_display(),
                p.cover,
                float(p.contract_premium),
                float(p.total_premium_due),
                float(p.total_premium_received),
                float(p.total_premium_arrears),
                p.overall_policy_status,
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="policies.xlsx"'
        wb.save(response)

        return response



