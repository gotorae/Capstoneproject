from django.urls import path
from .views import PolicyDetailAPIView, PolicyListCreateAPIView

urlpatterns = [
    path("create/", PolicyListCreateAPIView.as_view(), name="create"),
    path("update/<int:pk>/", PolicyDetailAPIView.as_view(), name="update"),
    path("view/", PolicyListCreateAPIView.as_view(), name="view"),
]