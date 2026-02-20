from django.shortcuts import render

# Create your views here.
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.employees.models import Employee
from .models import Attendance, AttendanceSetting
from .serializers import AttendanceSerializer


class CheckInAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        employee = Employee.objects.filter(user=user).first()
        if not employee:
            return Response({"detail": "Employee profile tidak ditemukan."}, status=400)

        today = timezone.localdate()

        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
        )

        if attendance.check_in_time:
            return Response({"detail": "Kamu sudah check-in hari ini."}, status=400)

        # ambil setting aktif
        setting = AttendanceSetting.objects.filter(is_active=True).first()
        if not setting:
            # default fallback
            work_start = datetime.strptime("08:00", "%H:%M").time()
            late_tol = 10
        else:
            work_start = setting.work_start_time
            late_tol = setting.late_tolerance_minutes

        now = timezone.now()

        # status late?
        start_dt = timezone.make_aware(datetime.combine(today, work_start))
        late_limit = start_dt + timedelta(minutes=late_tol)

        status_att = "on_time"
        if now > late_limit:
            status_att = "late"

        attendance.check_in_time = now
        attendance.check_in_lat = request.data.get("lat")
        attendance.check_in_lng = request.data.get("lng")
        attendance.check_in_location_name = request.data.get("location_name")
        attendance.status = status_att
        attendance.notes = request.data.get("notes", None)

        attendance.save()

        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)


class CheckOutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        employee = Employee.objects.filter(user=user).first()
        if not employee:
            return Response({"detail": "Employee profile tidak ditemukan."}, status=400)

        today = timezone.localdate()

        attendance = Attendance.objects.filter(employee=employee, date=today).first()
        if not attendance:
            return Response({"detail": "Kamu belum check-in hari ini."}, status=400)

        if not attendance.check_in_time:
            return Response({"detail": "Kamu belum check-in hari ini."}, status=400)

        if attendance.check_out_time:
            return Response({"detail": "Kamu sudah check-out hari ini."}, status=400)

        now = timezone.now()

        attendance.check_out_time = now
        attendance.check_out_lat = request.data.get("lat")
        attendance.check_out_lng = request.data.get("lng")
        attendance.check_out_location_name = request.data.get("location_name")

        # hitung working minutes
        delta = now - attendance.check_in_time
        minutes = int(delta.total_seconds() // 60)

        attendance.working_minutes = max(minutes, 0)
        attendance.working_hours = round(attendance.working_minutes / 60, 2)


        attendance.save()

        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_200_OK)
