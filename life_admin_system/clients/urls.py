

from django.urls import path
from .views import (
    ClientListCreateAPIView, ClientDetailAPIView,
    UploadListCreateAPIView,
    UploadRetrieveUpdateDestroyAPIView, ApproveUploadAPIView, UploadListAllAPIView
    
)

urlpatterns = [
    # PremiumReceipt endpoints
    path('create/', ClientListCreateAPIView.as_view(), name='clients-list-create'),
    path('update/<int:pk>/', ClientDetailAPIView.as_view(), name='clients-detail'),

    # Upload endpoints
    path('uploads/', UploadListCreateAPIView.as_view(), name='upload-list-create'),
    path('uploads/<int:pk>/', UploadRetrieveUpdateDestroyAPIView.as_view(), name='upload-detail'),
    path('uploads/<int:pk>/approve/', ApproveUploadAPIView.as_view()),
    path('uploads/files/', UploadListAllAPIView.as_view(), name='uploads-all'),


]
