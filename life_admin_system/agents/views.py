
# agents/views.py
from django.utils import timezone
from django.http import HttpResponse
from rest_framework import viewsets, status, filters, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from .models import Agent, Upload
from .serializers import AgentSerializer, UploadSerializer, UploadDecisionSerializer
from .permissions import IsSuperuser
from .services import process_upload
from .resources import AgentResource
from django.http import HttpResponse
import csv
import openpyxl


# ---- Agents list/create & partial update ----
class AgentListCreateAPIView(viewsets.ModelViewSet):
    """
    You already had generics; moving to ViewSet is optional.
    If you prefer to keep your generics, you can ignore this class.
    """
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["agent_code", "agent_name", "agent_surname", "branch"]
    ordering_fields = ["agent_code", "agent_name", "date_joining"]

    http_method_names = ['get', 'post', 'patch', 'put']  # no delete


# -----------------------------
# Upload Endpoints
# -----------------------------

class UploadListCreateAPIView(generics.ListCreateAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 1️⃣ Save the uploaded file first
        upload = serializer.save(uploaded_by=self.request.user)

        # 2️⃣ Process the uploaded file for duplicates / creation
        errors = process_upload(upload)

        # 3️⃣ Optional: mark upload as rejected if there are errors
        if errors:
            upload.is_rejected = True
            upload.reject_reason = "; ".join(errors)
            upload.save()


        # Store errors in the serializer context so the response can include them
        self.upload_errors = errors

    def create(self, request, *args, **kwargs):
        # Call the default create
        response = super().create(request, *args, **kwargs)

        # Add process_upload errors to response if any
        errors = getattr(self, 'upload_errors', [])
        if errors:
            response.data['status'] = 'partial_failure'
            response.data['message'] = 'Some rows were not imported due to errors.'
            response.data['errors'] = errors
        else:
            response.data['status'] = 'success'
            response.data['message'] = 'File uploaded successfully.'

        return response

class UploadRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]


# -----------------------------
# Upload Approval Endpoint
# (Browsable API WILL show form)
# -----------------------------

class ApproveUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UploadDecisionSerializer

    def get(self, request, pk):
        upload = Upload.objects.get(pk=pk)
        return Response({
            "id": upload.id,
            "file": upload.file.url if upload.file else None,
            "is_approved": upload.is_approved,
            "is_rejected": upload.is_rejected,
            "reject_reason": upload.reject_reason,
        })

    def post(self, request, pk):
        upload = Upload.objects.get(pk=pk)
        serializer = UploadDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']

        if action == 'approve':
            upload.is_approved = True
            upload.is_rejected = False
            upload.reject_reason = ""
            upload.approved_by = request.user
            upload.approved_at = timezone.now()
            # Keep any existing reject_reason (errors from upload)
            if upload.reject_reason:
                message = (
                    "File has been approved, "
                    "but note some rows were not imported:\n" + upload.reject_reason
                )
            else:
                message = "File has been successfully approved"


        else:  # reject
            upload.is_rejected = True
            upload.is_approved = False
            upload.approved_by = None
            upload.approved_at = None
            upload.reject_reason = serializer.validated_data.get(
                'reject_reason', 'Rejected by approver'
            )
            message = "File has been successfully rejected the file"

        upload.save()

        return Response(
    {
        "status": action,
        "message": message,
        "upload_id": upload.id,
        "links": {
            "view_all_files": request.build_absolute_uri("/receipts/uploads/files/"),
        }
    },
    status=status.HTTP_200_OK
)




class UploadListAllAPIView(generics.ListAPIView):
    """
    List all uploads with file URLs and approval status.
    """
    queryset = Upload.objects.all().order_by('-uploaded_at')
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]





class AgentExportCSVAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Agent.objects.all()

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
    


class AgentExportExcelAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Agent.objects.all()

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



