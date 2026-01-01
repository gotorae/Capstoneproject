
from django.urls import path
from .views import RegisterCreateAPI, LoginAPI, LogoutAPI, ProfileAPI, AdministratorListAPI

urlpatterns = [
    path("auth/register/", RegisterCreateAPI.as_view(), name="register"),
    path("auth/login/", LoginAPI.as_view(), name="login"),
    path("auth/logout/", LogoutAPI.as_view(), name="logout"),
    path("me/", ProfileAPI.as_view(), name="profile"),
    path("admins/", AdministratorListAPI.as_view(), name="admin-list"),
]