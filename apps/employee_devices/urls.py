from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import EmployeeDeviceViewSet

router = DefaultRouter()
router.register(r"devices", EmployeeDeviceViewSet, basename="devices")

urlpatterns = [
    path("", include(router.urls)),
]
