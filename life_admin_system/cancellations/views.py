from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import CancellationRequest, CancellationStatus
from .serializers import (
    CancellationRequestSerializer,
    CancellationApprovalSerializer,
)

# ---------------------------------
# 1️⃣ REQUEST CANCELLATION
# ---------------------------------
class CancellationRequestCreateAPIView(generics.CreateAPIView):
    serializer_class = CancellationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            requested_by=self.request.user,
            status=CancellationStatus.REQUESTED,
        )


# ---------------------------------
# 2️⃣ LIST MY CANCELLATIONS
# ---------------------------------
class MyCancellationRequestsAPIView(generics.ListAPIView):
    serializer_class = CancellationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CancellationRequest.objects.filter(
            requested_by=self.request.user
        )


# ---------------------------------
# 3️⃣ LIST ALL CANCELLATIONS (ADMIN)
# ---------------------------------
class AllCancellationRequestsAPIView(generics.ListAPIView):
    queryset = CancellationRequest.objects.all()
    serializer_class = CancellationRequestSerializer
    permission_classes = [permissions.IsAdminUser]


# ---------------------------------
# 4️⃣ APPROVE CANCELLATION
# ---------------------------------
class ApproveCancellationAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        cancellation = get_object_or_404(
            CancellationRequest,
            pk=pk,
            status=CancellationStatus.REQUESTED,
        )

        serializer = CancellationApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cancellation.approve(approver=request.user)

        return Response(
            {"detail": "Cancellation approved successfully."},
            status=status.HTTP_200_OK,
        )
