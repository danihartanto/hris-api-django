from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LeaveTypeViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register(r"leave-types", LeaveTypeViewSet, basename="leave-types")
router.register(r"leave-requests", LeaveRequestViewSet, basename="leave-requests")

urlpatterns = [
    path("", include(router.urls)),
]

