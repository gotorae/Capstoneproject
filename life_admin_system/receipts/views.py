from rest_framework import generics, permissions
from .models import PremiumReceipt, Upload
from .serializers import PremiumReceiptSerializer, UploadSerializer

# -----------------------------
# PremiumReceipt Endpoints
# -----------------------------

class PremiumReceiptListCreateAPIView(generics.ListCreateAPIView):
    queryset = PremiumReceipt.objects.all()
    serializer_class = PremiumReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(receipted_by=self.request.user)


class PremiumReceiptRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
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


class UploadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]


