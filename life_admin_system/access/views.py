# access/views.py
from django.contrib.auth import authenticate, get_user_model
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AdministratorSerializer

User = get_user_model()


class RegisterCreateAPI(generics.CreateAPIView):
    """
    Admin-only: create new users and issue a token.
    """
    queryset = User.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Fetch saved user & issue token
        user = User.objects.get(email=response.data["email"])
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": AdministratorSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginAPI(APIView):
    """
    Log in with email + password.
    Returns DRF token for subsequent requests.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": AdministratorSerializer(user).data})


class LogoutAPI(APIView):
    """
    Logout by deleting the user's token (for token auth).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)


class ProfileAPI(generics.RetrieveUpdateAPIView):
    """
    Authenticated user's profile.
    """
    serializer_class = AdministratorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdministratorListAPI(generics.ListAPIView):
    """
    List users (admin-only).
    """
    queryset = User.objects.all()
    serializer_class = AdministratorSerializer



       


# Create your views here.
