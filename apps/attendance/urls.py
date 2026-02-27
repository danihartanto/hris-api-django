# from django.urls import path, include
# from rest_framework.routers import DefaultRouter

# from .views import CheckInViewSet, CheckOutViewSet, AttendanceViewSet

# router = DefaultRouter()
# router.register(r"attendances", AttendanceViewSet, basename="attendances")
# router.register(r"check-in", CheckInViewSet, basename="check-in")
# router.register(r"check-out", CheckOutViewSet, basename="check-out")

# urlpatterns = [
#     path("", include(router.urls)),
# ]

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import AttendanceViewSet, AttendanceActionViewSet

router = DefaultRouter()

# HR / Manager CRUD
router.register(r"attendances", AttendanceViewSet, basename="attendances")

# Employee Actions
router.register(r"attendance-actions", AttendanceActionViewSet, basename="attendance-actions")

urlpatterns = [
    path("", include(router.urls)),
]