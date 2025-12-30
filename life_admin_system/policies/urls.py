from django.urls import path
from .views import (
    PolicyDetailAPIView,
    PolicyListCreateAPIView,
    PolicyExportCSVAPIView,
    PolicyExportExcelAPIView,
    upload_file,
)

urlpatterns = [
    path("create/", PolicyListCreateAPIView.as_view(), name="create"),
    path("update/<int:pk>/", PolicyDetailAPIView.as_view(), name="update"),
    path("view/", PolicyListCreateAPIView.as_view(), name="view"),

    # EXPORT ENDPOINTS
    path("export/csv/", PolicyExportCSVAPIView.as_view(), name="policy-export-csv"),
    path("export/excel/", PolicyExportExcelAPIView.as_view(), name="policy-export-excel"),

    path("upload/success/", upload_file, name="upload_success"),
]
