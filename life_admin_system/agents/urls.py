
# agents/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (UploadListAllAPIView, UploadListCreateAPIView,
                    UploadRetrieveUpdateDestroyAPIView,ApproveUploadAPIView,
                    AgentListCreateAPIView, AgentExportCSVAPIView)

router = DefaultRouter()
router.register(r'create', AgentListCreateAPIView, basename='create-agents')  # optional ViewSet version


# config/urls.py (serve media in DEBUG)
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', include(router.urls)),
    # Upload endpoints
    path('uploads/', UploadListCreateAPIView.as_view(), name='upload-list-create'),
    path('uploads/<int:pk>/', UploadRetrieveUpdateDestroyAPIView.as_view(), name='upload-detail'),
    path('uploads/<int:pk>/approve/', ApproveUploadAPIView.as_view()),
    path('uploads/files/', UploadListAllAPIView.as_view(), name='uploads-all'),

    path('export/', AgentExportCSVAPIView.as_view(), name='agents-export'),
]



from django.urls import path
from commissions import views as commissions_views  # adjust if needed

urlpatterns = [
    # ... your existing routes ...
    path("healthz/", commissions_views.healthz),  # temporary debug endpoint
]


