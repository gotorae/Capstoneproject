from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Claim, ClaimStatus
from .serializers import ClaimSerializer, ClaimApprovalSerializer
from .permissions import IsManager





class SubmitClaimAPIView(generics.CreateAPIView):
    serializer_class = ClaimSerializer

    def perform_create(self, serializer):
        serializer.save(claimant=self.request.user)


class PendingClaimsAPIView(generics.ListAPIView):
    permission_classes = [IsManager]
    serializer_class = ClaimSerializer
    ordering_fields = ["requested_at", "id"]
    ordering = ["-requested_at"]

    def get_queryset(self):
        return Claim.objects.filter(
            status=ClaimStatus.REQUESTED
        )



class ApproveClaimAPIView(APIView):
    permission_classes = [IsManager]
    serializer_class = ClaimApprovalSerializer

    def get(self, request, pk):
        claim = get_object_or_404(Claim, pk=pk)

        return Response({
            "claim_id": claim.id,
            "policy": claim.policy.contract_id,
            "status": claim.status,
            "requested_at": claim.requested_at,
        })

    def post(self, request, pk):
        claim = get_object_or_404(Claim, pk=pk)

        serializer = ClaimApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]

        if action == "approve":
            claim.approve(approver=request.user)
            message = "Claim approved. Payment requisition sent."

        else:  # reject
            claim.reject(
                approver=request.user,
                reason=serializer.validated_data.get(
                    "reject_reason", "Rejected by manager"
                )
            )
            message = "Claim rejected."

        return Response(
            {
                "status": action,
                "message": message,
                "claim_id": claim.id
            },
            status=status.HTTP_200_OK
        )
