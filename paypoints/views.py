from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .models import Paypoint
from .serializers import PaypointSerializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes



class PaypointListCreateAPIView(generics.ListCreateAPIView):
    queryset = Paypoint.objects.all()
    serializer_class = PaypointSerializers
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    # If you want GET list without login, uncomment the next line:
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # If you want everything to require login, use:
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["paypoint_code",'paypoint_name', "date_joined"]
    ordering_fields = ["paypoint_code", "paypoint_name", "date_joined"]




class PaypointDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Paypoint.objects.all()
    serializer_class = PaypointSerializers
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]









