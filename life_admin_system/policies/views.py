from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .models import Policy
from .serializers import PolicySerializers


class PolicyListCreateAPIView(generics.ListCreateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializers
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    # If you want GET list without login, uncomment the next line:
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # If you want everything to require login, use:
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["contract_id", "product_name", "frequency", "created_by", "created_date"]
    ordering_fields = ["contract_id", "product_name", "frequency", "proposal_sign_date", "created_by", "created_date"]


class PolicyDetailAPIView(generics.UpdateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializers
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # Optional but explicit:

# Create your views here.
