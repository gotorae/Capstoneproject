from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import PremiumReceipt, Upload
from .serializers import (
    PremiumReceiptSerializer,
    UploadSerializer,
    UploadDecisionSerializer,
)


# -----------------------------
# PremiumReceipt Endpoints
# -----------------------------

class PremiumReceiptListCreateAPIView(generics.ListCreateAPIView):
    queryset = PremiumReceipt.objects.all()
    serializer_class = PremiumReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(receipted_by=self.request.user)


class PremiumReceiptRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = PremiumReceipt.objects.all()
    serializer_class = PremiumReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]


# -----------------------------
# Upload Endpoints
# -----------------------------

class UploadListCreateAPIView(generics.ListCreateAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


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
