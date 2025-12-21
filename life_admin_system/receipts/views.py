from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .models import PremiumReceipt
from .serializers import PremiumReceiptSerializer


class ReceiptListCreateAPIView(generics.ListCreateAPIView):
    queryset = PremiumReceipt.objects.all()
    serializer_class = PremiumReceiptSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    # If you want GET list without login, uncomment the next line:
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # If you want everything to require login, use:
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["policy", 'receipt_number', 'amount_received', 'date_received']
    ordering_fields = ["policy", 'receipt_number', 'amount_received', 'date_received']


class ReceiptDetailAPIView(generics.UpdateAPIView):
    queryset = PremiumReceipt.objects.all()
    serializer_class = PremiumReceiptSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # Optional but explicit:




# Create your views here.
