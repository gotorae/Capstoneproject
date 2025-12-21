from django.urls import path
from .views import AgentDetailAPIView, AgentListCreateAPIView

urlpatterns = [
    path("create/", AgentListCreateAPIView.as_view(), name="create"),
    path("update/<int:pk>/", AgentDetailAPIView.as_view(), name="update"),
    path("view/", AgentListCreateAPIView.as_view(), name="view"),
]
