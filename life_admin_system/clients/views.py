from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .models import Client
from .serializers import ClientSerializer


class ClientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    # If you want GET list without login, uncomment the next line:
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # If you want everything to require login, use:
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["client_code", "client_name", "client_surname", "id_number"]
    ordering_fields = ["client_code", "client_name", "dob"]


class ClientDetailAPIView(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    # Optional but explicit:


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Upload

@login_required
def upload_file(request):
    if request.method == "POST":
        Upload.objects.create(
            file=request.FILES["file"],
            uploaded_by=request.user
        )
        return redirect("upload_success")

