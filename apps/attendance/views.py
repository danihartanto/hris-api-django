from django.shortcuts import render

# Create your views here.
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action

from apps.employees.models import Employee
from apps.accounts.models import user_has_permission
from .models import Attendance, AttendanceSetting
from .serializers import AttendanceSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    queryset = Attendance.objects.select_related(
        "employee",
        "employee__user",
    ).all()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        from apps.accounts.utils import user_has_permission

        if user_has_permission(user, "attendance.view_all") or user.is_staff:
            base_qs = qs
            can_view_all = True
        else:
            employee = getattr(user, "employee_profile", None)
            if not employee:
                return qs.none()

            base_qs = qs.filter(employee=employee)
            can_view_all = False

        employee_number = self.request.query_params.get("employee_number")
        month = self.request.query_params.get("month")
        year = self.request.query_params.get("year")

        if employee_number and can_view_all:
            base_qs = base_qs.filter(employee__employee_number=employee_number)

        if month:
            base_qs = base_qs.filter(date__month=month)

        if year:
            base_qs = base_qs.filter(date__year=year)

        return base_qs
    
class AttendanceActionViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()  

    def get_employee(self):
        return getattr(self.request.user, "employee_profile", None)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def check_in(self, request):
        employee = self.get_employee()
        if not employee:
            return Response({"detail": "Employee profile tidak ditemukan."}, status=400)

        today = timezone.localdate()

        attendance, _ = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
        )

        if attendance.check_in_time:
            return Response({"detail": "Sudah check-in hari ini."}, status=400)

        setting = AttendanceSetting.objects.filter(is_active=True).first()

        work_start = setting.work_start_time if setting else time(8, 0)
        tolerance = setting.late_tolerance_minutes if setting else 10

        now = timezone.now()
        start_dt = timezone.make_aware(datetime.combine(today, work_start))
        late_limit = start_dt + timedelta(minutes=tolerance)

        attendance.status = "late" if now > late_limit else "on_time"
        attendance.check_in_time = now
        attendance.check_in_lat = request.data.get("lat")
        attendance.check_in_lng = request.data.get("lng")
        attendance.check_in_photo = request.data.get("image")
        attendance.check_in_location_name = request.data.get("location_name")
        attendance.notes = request.data.get("notes")

        attendance.save()

        return Response(self.get_serializer(attendance).data)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def check_out(self, request):
        employee = self.get_employee()
        if not employee:
            return Response({"detail": "Employee profile tidak ditemukan."}, status=400)

        today = timezone.localdate()
        now = timezone.now()

        attendance = Attendance.objects.filter(
            employee=employee,
            date=today,
        ).first()

        if not attendance or not attendance.check_in_time:
            return Response({"detail": "Belum check-in."}, status=400)

        if attendance.check_out_time:
            return Response({"detail": "Sudah check-out."}, status=400)

        attendance.check_out_time = timezone.now()
        attendance.check_out_lat = request.data.get("lat")
        attendance.check_out_lng = request.data.get("lng")
        attendance.check_out_photo = request.data.get("image")
        attendance.check_out_location_name = request.data.get("location_name")
        
        delta = now - attendance.check_in_time
        minutes = int(delta.total_seconds() // 60)

        attendance.working_minutes = max(minutes, 0)
        attendance.working_hours = round(attendance.working_minutes / 60, 2)

        attendance.save()

        return Response(self.get_serializer(attendance).data)
    
    @action(detail=False, methods=["get"])
    def summary(self, request):
        employee_number = request.query_params.get("employee_number")
        month = request.query_params.get("month")
        year = request.query_params.get("year")

        # qss = self.get_queryset()
        qs = super().get_queryset()
        user = self.request.user
        
        from apps.accounts.utils import user_has_permission

        if user_has_permission(user, "attendance.view_all") or user.is_staff:
            base_qs = qs
            can_view_all = True
        else:
            employee = getattr(user, "employee_profile", None)
            if not employee:
                return qs.none()

            base_qs = qs.filter(employee=employee)
            can_view_all = False

        if employee_number:
            qs = base_qs.filter(employee__employee_number=employee_number)

        if month:
            qs = base_qs.filter(date__month=month)

        if year:
            qs = base_qs.filter(date__year=year)

        return Response({
            "total": base_qs.count(),
            "on_time": base_qs.filter(status="on_time").count(),
            "late": base_qs.filter(status="late").count(),
            "alpha": base_qs.filter(status="alpha").count(),
        })




# class AttendanceViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = Attendance.objects.select_related(
#         "employee",
#         "employee__user",
#     ).all()
#     # serializer_class = AttendanceSerializer 
    
#     def get_serializer_class(self):
#         if self.action == "create":
#             return AttendanceSerializer
#         return AttendanceSerializer
    
#     @transaction.atomic
#     def get_queryset(self):
#         qs = super().get_queryset()
#         user = self.request.user

#         # =========================
#         # ROLE ACCESS CONTROL
#         # =========================

#         # Superuser bisa lihat semua
#         # if user.is_superuser:
#         if user.has_perm("attendance.view_all"):
#             base_qs = qs

#         # HR / Manager (sementara pakai is_staff)
#         elif user.is_staff:
#             base_qs = qs

#         # Employee biasa → hanya miliknya
#         else:
#             employee = getattr(user, "employee_profile", None)
#             if not employee:
#                 return qs.none()

#             base_qs = qs.filter(employee=employee)

#         # =========================
#         # FILTER QUERY PARAMS
#         # =========================

#         employee_number = self.request.query_params.get("employee_number")
#         status_param = self.request.query_params.get("status")
#         date_param = self.request.query_params.get("date")
#         # month = self.request.query_params.get("month")

#         # ⚠️ IMPORTANT:
#         # Employee biasa tidak boleh override filter employee_number
#         if employee_number and (user.is_superuser or user.is_staff):
#             base_qs = base_qs.filter(employee__employee_number=employee_number)

#         if status_param:
#             base_qs = base_qs.filter(status=status_param)

#         if date_param:
#             base_qs = base_qs.filter(date=date_param)

#         return base_qs

# class CheckInViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = AttendanceSerializer

#     # @action(detail=False, methods=["post"])
#     @transaction.atomic
#     def post(self, request):
#         user = request.user

#         # =========================
#         # Pastikan employee
#         # =========================
#         employee = Employee.objects.filter(user=user).first()
#         # employee = getattr(user, "employee_profile", None)
#         print("employee check-in: ",employee)
#         if not employee:
#             return Response(
#                 {"detail": "Employee profile tidak ditemukan."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         today = timezone.localdate()

#         attendance, created = Attendance.objects.get_or_create(
#             employee=employee,
#             date=today,
#         )

#         if attendance.check_in_time:
#             return Response(
#                 {"detail": "Kamu sudah check-in hari ini."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # =========================
#         # Ambil working hour setting
#         # =========================
#         setting = AttendanceSetting.objects.filter(is_active=True).first()

#         if setting:
#             work_start = setting.work_start_time
#             late_tol = setting.late_tolerance_minutes
#         else:
#             # fallback default
#             work_start = datetime.strptime("08:00", "%H:%M").time()
#             late_tol = 10

#         now = timezone.now()

#         start_dt = timezone.make_aware(
#             datetime.combine(today, work_start)
#         )
#         late_limit = start_dt + timedelta(minutes=late_tol)

#         status_att = "on_time"
#         if now > late_limit:
#             status_att = "late"

#         # =========================
#         # Save Data
#         # =========================
#         attendance.check_in_time = now
#         attendance.check_in_lat = request.data.get("lat")
#         attendance.check_in_lng = request.data.get("lng")
#         attendance.check_in_location_name = request.data.get("location_name")
#         attendance.status = status_att
#         attendance.notes = request.data.get("notes")

#         attendance.save()

#         return Response(
#             AttendanceSerializer(attendance).data,
#             status=status.HTTP_201_CREATED,
#         )

# class CheckOutViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = AttendanceSerializer

#     @transaction.atomic
#     def post(self, request):
#         user = request.user

#         employee = Employee.objects.filter(user=user).first()
#         if not employee:
#             return Response({"detail": "Employee profile tidak ditemukan."}, status=400)

#         today = timezone.localdate()

#         attendance = Attendance.objects.filter(employee=employee, date=today).first()
#         if not attendance:
#             return Response({"detail": "Kamu belum check-in hari ini."}, status=400)

#         if not attendance.check_in_time:
#             return Response({"detail": "Kamu belum check-in hari ini."}, status=400)

#         if attendance.check_out_time:
#             return Response({"detail": "Kamu sudah check-out hari ini."}, status=400)

#         now = timezone.now()

#         attendance.check_out_time = now
#         attendance.check_out_lat = request.data.get("lat")
#         attendance.check_out_lng = request.data.get("lng")
#         attendance.check_out_location_name = request.data.get("location_name")

#         # hitung working minutes
#         delta = now - attendance.check_in_time
#         minutes = int(delta.total_seconds() // 60)

#         attendance.working_minutes = max(minutes, 0)
#         attendance.working_hours = round(attendance.working_minutes / 60, 2)


#         attendance.save()

#         return Response(AttendanceSerializer(attendance).data, status=status.HTTP_200_OK)
