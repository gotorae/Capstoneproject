from django.urls import path
from .views import (
    CancellationRequestCreateAPIView,
    MyCancellationRequestsAPIView,
    AllCancellationRequestsAPIView,
    ApproveCancellationAPIView,
)

urlpatterns = [
    # Request a cancellation
    path(
        "cancellations/request/",
        CancellationRequestCreateAPIView.as_view(),
        name="cancellation-request",
    ),

    # View own cancellation requests
    path(
        "cancellations/my/",
        MyCancellationRequestsAPIView.as_view(),
        name="my-cancellations",
    ),

    # Admin: view all cancellations
    path(
        "cancellations/",
        AllCancellationRequestsAPIView.as_view(),
        name="all-cancellations",
    ),

    # Admin: approve cancellation
    path(
        "cancellations/<int:pk>/approve/",
        ApproveCancellationAPIView.as_view(),
        name="approve-cancellation",
    ),
]
