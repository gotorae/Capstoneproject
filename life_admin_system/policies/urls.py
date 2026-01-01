from django.urls import path
from .views import (
    PolicyDetailAPIView,
    PolicyListCreateAPIView,
    PolicyExportCSVAPIView,
    PolicyExportExcelAPIView,
    UploadListAllAPIView,
    UploadListCreateAPIView,
    UploadRetrieveUpdateDestroyAPIView,
    ApproveUploadAPIView,
)

urlpatterns = [
    path("create/", PolicyListCreateAPIView.as_view(), name="create"),
    path("update/<int:pk>/", PolicyDetailAPIView.as_view(), name="update"),
    path("view/", PolicyListCreateAPIView.as_view(), name="view"),

    # EXPORT ENDPOINTS
    path("export/csv/", PolicyExportCSVAPIView.as_view(), name="policy-export-csv"),
    path("export/excel/", PolicyExportExcelAPIView.as_view(), name="policy-export-excel"),

    path('uploads/', UploadListCreateAPIView.as_view(), name='upload-list-create'),
    path('uploads/<int:pk>/', UploadRetrieveUpdateDestroyAPIView.as_view(), name='upload-detail'),
    path('uploads/<int:pk>/approve/', ApproveUploadAPIView.as_view()),
    path('uploads/files/', UploadListAllAPIView.as_view(), name='uploads-all'),
]
