from django.shortcuts import render

# Create your views here.
from django.utils import timezone
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
        """
        Employee hanya lihat leave miliknya.
        HR bisa lihat semua (nanti kita bisa tambah permission).
        """
        qs = super().get_queryset()
        employee = Employee.objects.filter(user=self.request.user).first()

        # kalau user bukan employee, tampilkan semua
        if not employee:
            return qs

        return qs.filter(employee=employee)

    def create(self, request, *args, **kwargs):
        serializer = LeaveRequestCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        leave_request = serializer.save()

        return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)
