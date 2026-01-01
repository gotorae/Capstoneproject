from django.urls import path
from .views import (
    SubmitClaimAPIView,
    PendingClaimsAPIView,
    ApproveClaimAPIView,
)

urlpatterns = [
    path(
        "claims/submit/",
        SubmitClaimAPIView.as_view(),
        name="submit-claim",
    ),
    path(
        "claims/pending/",
        PendingClaimsAPIView.as_view(),
        name="pending-claims",
    ),
    path(
        "claims/<int:pk>/approve/",
        ApproveClaimAPIView.as_view(),
        name="approve-claim",
    ),
]
