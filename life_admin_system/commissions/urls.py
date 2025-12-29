# commissions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from commissions.views import CommissionRecordViewSet

router = DefaultRouter()
router.register(r'commissions', CommissionRecordViewSet, basename='commission-record')

urlpatterns = [
    path('', include(router.urls)),
]
