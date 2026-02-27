from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from apps.accounts.permissions import HasPermission

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action

from apps.employees.models import Employee
from .models import LeaveType, LeaveRequest
from .serializers import (
    LeaveTypeSerializer,
    LeaveRequestSerializer,
    LeaveRequestCreateSerializer,
)


class LeaveTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = LeaveType.objects.all().order_by("name")
    serializer_class = LeaveTypeSerializer


class LeaveRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = LeaveRequest.objects.select_related(
        "employee",
        "employee__user",
        "leave_type",
    ).all()

    def get_serializer_class(self):
        if self.action == "create":
            return LeaveRequestCreateSerializer
        return LeaveRequestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # =========================
        # ROLE ACCESS CONTROL
        # =========================

        # Superuser bisa lihat semua
        # if user.is_superuser:
        if user.has_perm("leave.view_all"):
            base_qs = qs

        # HR / Manager (sementara pakai is_staff)
        elif user.is_staff:
            base_qs = qs

        # Employee biasa → hanya miliknya
        else:
            employee = getattr(user, "employee_profile", None)
            if not employee:
                return qs.none()

            base_qs = qs.filter(employee=employee)

        # =========================
        # FILTER QUERY PARAMS
        # =========================

        employee_number = self.request.query_params.get("employee_number")
        status_param = self.request.query_params.get("status")
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")

        # ⚠️ IMPORTANT:
        # Employee biasa tidak boleh override filter employee_number
        if employee_number and (user.is_superuser or user.is_staff):
            base_qs = base_qs.filter(employee__employee_number=employee_number)

        if status_param:
            base_qs = base_qs.filter(status=status_param)

        if year:
            base_qs = base_qs.filter(start_date__year=year)

        if month:
            base_qs = base_qs.filter(start_date__month=month)

        return base_qs

    # def get_queryset(self):
    #     """
    #     Employee hanya lihat leave miliknya.
    #     HR bisa lihat semua (nanti kita bisa tambah permission).
    #     """
    #     qs = super().get_queryset()
    #     user = self.request.user
    #     if user.is_superuser or user.is_staff or user.has_perm("leave.view"):
    #         base_qs = qs
    #     else:
    #         employee = getattr(user, "employee_profile", None)
    #         if employee:
    #             base_qs = qs.filter(employee=employee)
    #         else:
    #             return qs.none()

    #     # =========================
    #     # FILTER QUERY PARAMS
    #     # =========================
    #     employee_number = self.request.query_params.get("employee_number")
    #     status_param = self.request.query_params.get("status")
    #     leave_type = self.request.query_params.get("leave_type")
    #     year = self.request.query_params.get("year")
    #     month = self.request.query_params.get("month")

    #     if employee_number:
    #         base_qs = base_qs.filter(employee__employee_number=employee_number)

    #     if status_param:
    #         base_qs = base_qs.filter(status=status_param)

    #     if leave_type:
    #         base_qs = base_qs.filter(leave_type__id=leave_type)

    #     if year:
    #         base_qs = base_qs.filter(start_date__year=year)

    #     if month:
    #         base_qs = base_qs.filter(start_date__month=month)

    #     return base_qs

    def create(self, request, *args, **kwargs):
        serializer = LeaveRequestCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        leave_request = serializer.save()

        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"], permission_classes=[HasPermission])
    def approve(self, request, pk=None):
        self.required_permissions = ["leave.approve"]

        leave = self.get_object()

        if leave.status != "pending":
            return Response({"detail": "Leave sudah diproses."}, status=400)

        approver_employee = getattr(request.user, "employee_profile", None)

        leave.status = "approved"
        leave.approved_by = approver_employee
        leave.approved_at = timezone.now()
        leave.rejected_at = None
        leave.rejection_reason = None
        leave.save()

        return Response({"detail": "Leave berhasil di-approve."})


    @action(detail=True, methods=["post"], permission_classes=[HasPermission])
    def reject(self, request, pk=None):
        self.required_permissions = ["leave.approve"]

        leave = self.get_object()

        if leave.status != "pending":
            return Response({"detail": "Leave sudah diproses."}, status=400)

        rejection_reason = request.data.get("rejection_reason")
        if not rejection_reason:
            return Response(
                {"detail": "rejection_reason wajib diisi."},
                status=400
            )

        rejector_employee = getattr(request.user, "employee_profile", None)

        leave.status = "rejected"
        leave.rejected_by = rejector_employee
        leave.rejected_at = timezone.now()
        leave.rejection_reason = rejection_reason
        leave.approved_at = None
        leave.save()

        return Response({"detail": "Leave berhasil di-reject."})

