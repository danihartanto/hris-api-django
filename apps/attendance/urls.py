from django.urls import path

from .views import CheckInAPIView, CheckOutAPIView

urlpatterns = [
    path("attendance/check-in/", CheckInAPIView.as_view(), name="attendance-check-in"),
    path("attendance/check-out/", CheckOutAPIView.as_view(), name="attendance-check-out"),
]

