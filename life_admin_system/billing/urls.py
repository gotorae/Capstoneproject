
# billing/urls.py
from rest_framework.routers import DefaultRouter
from .views import BillingRecordViewSet

router = DefaultRouter()
router.register("billing-records", BillingRecordViewSet, basename="billing-record")

urlpatterns = router.urls
