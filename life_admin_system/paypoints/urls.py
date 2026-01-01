from django.urls import path
from .views import PaypointDetailAPIView, PaypointListCreateAPIView

urlpatterns = [
    path("create/", PaypointListCreateAPIView.as_view(), name="create"),
    path("update/<int:pk>/", PaypointDetailAPIView.as_view(), name="update"),
    path("view/", PaypointListCreateAPIView.as_view(), name="view"),
]