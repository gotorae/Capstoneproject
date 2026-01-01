from django.urls import path, include
from rest_framework.routers import DefaultRouter
from commissions.views import CommissionRecordViewSet, run_commissions_view

router = DefaultRouter()
router.register(r'commissions', CommissionRecordViewSet, basename='commission-record')

urlpatterns = [
    path('', include(router.urls)),
    path('run/', run_commissions_view, name='run_commissions'),
]
