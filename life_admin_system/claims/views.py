from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from claims.models import Claim, ClaimStatus
from policies.models import Policy
from .serializers import (
    ClaimCreateSerializer,
    ClaimApprovalSerializer,
)
from .permissions import IsManager

class SubmitClaimAPIView(generics.CreateAPIView):
    serializer_class = ClaimCreateSerializer

    def perform_create(self, serializer):
        policy = serializer.validated_data["policy"]

        if policy.status != Policy.PolicyState.ACTIVE:
            raise ValidationError(
                "Claims can only be submitted for ACTIVE policies."
            )

        serializer.save(
            claimant=self.request.user,
            status=ClaimStatus.REQUESTED
        )


class PendingClaimsAPIView(generics.ListAPIView):
    permission_classes = [IsManager]

    def get_queryset(self):
        return Claim.objects.filter(
            status=ClaimStatus.REQUESTED
        )

    def list(self, request):
        data = [
            {
                "id": c.id,
                "policy": c.policy.contract_id,
                "claimant": str(c.claimant),
                "account_number": c.account_number,
                "requested_at": c.requested_at,
            }
            for c in self.get_queryset()
        ]
        return Response(data)


class ApproveClaimAPIView(APIView):
    permission_classes = [IsManager]

    def post(self, request, pk):
        claim = get_object_or_404(Claim, pk=pk)

        serializer = ClaimApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        claim.approve(approver=request.user)

        return Response(
            {"detail": "Claim approved. Payment requisition sent."},
            status=status.HTTP_200_OK
        )
from django.shortcuts import render

# Create your views here.
