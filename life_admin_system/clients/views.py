from rest_framework import generics, filters, status,permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.http import HttpResponse
from .models import Client, Upload
from .serializers import ClientSerializer, UploadSerializer, UploadDecisionSerializer
from .permissions import IsSuperuser
from .services import process_upload
from .resources import ClientResource
from django.utils import timezone






class ClientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    # If you want GET list without login, uncomment the next line:
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # If you want everything to require login, use:
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["client_code", "client_name", "client_surname", "id_number"]
    ordering_fields = ["client_code", "client_name", "dob"]


class ClientDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # Optional but explicit:






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
