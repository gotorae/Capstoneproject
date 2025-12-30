from django.urls import path
from .views import (
    PremiumReceiptListCreateAPIView,
    PremiumReceiptRetrieveUpdateDestroyAPIView,
    UploadListCreateAPIView,
    UploadRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    # PremiumReceipt endpoints
    path('receipts/', PremiumReceiptListCreateAPIView.as_view(), name='receipt-list-create'),
    path('receipts/<int:pk>/', PremiumReceiptRetrieveUpdateDestroyAPIView.as_view(), name='receipt-detail'),

    # Upload endpoints
    path('uploads/', UploadListCreateAPIView.as_view(), name='upload-list-create'),
    path('uploads/<int:pk>/', UploadRetrieveUpdateDestroyAPIView.as_view(), name='upload-detail'),
]
