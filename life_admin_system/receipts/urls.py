from django.urls import path
from .views import ReceiptDetailAPIView, ReceiptListCreateAPIView

urlpatterns = [
    path("create/", ReceiptListCreateAPIView.as_view(), name="create"),
    path("update/<int:pk>/", ReceiptDetailAPIView.as_view(), name="update"),
    path("view/", ReceiptListCreateAPIView.as_view(), name="view"),
]