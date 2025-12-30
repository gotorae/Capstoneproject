from django.urls import path
from .views import ClientDetailAPIView, ClientListCreateAPIView, upload_file

urlpatterns = [
    path("create/", ClientListCreateAPIView.as_view(), name="create"),
    path("update/<int:pk>/", ClientListCreateAPIView.as_view(), name="update"),
    path("view/", ClientListCreateAPIView.as_view(), name="view"),
    path("upload/success/", upload_file, name="upload_success"),
]