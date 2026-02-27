from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.accounts.permissions import HasPermission
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from .models import EmployeeDevice
from .serializers import EmployeeDeviceSerializer


class EmployeeDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeDeviceSerializer
    permission_classes = [IsAuthenticated]
    queryset = EmployeeDevice.objects.select_related("employee").all()

    def get_queryset(self):
        user = self.request.user

        # HR / Manager bisa lihat semua
        if user.is_staff:
            return self.queryset

        employee = getattr(user, "employee_profile", None)
        if not employee:
            return self.queryset.none()

        return self.queryset.filter(employee=employee)

    def perform_create(self, serializer):
        employee = getattr(self.request.user, "employee_profile", None)
        if not employee:
            raise serializers.ValidationError("Employee profile tidak ditemukan.")

        serializer.save(employee=employee)

    def perform_update(self, serializer):
        serializer.save(last_used_at=timezone.now())
        

    @action(detail=False, methods=["post"], url_path="check-device",
    permission_classes=[AllowAny])
    def check_device(self, request):
        device_id = request.data.get("device_id")

        if not device_id:
            return Response({
                "status": "error",
                "code": 400,
                "message": "device_id wajib diisi.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        device = EmployeeDevice.objects.filter(
            device_id=device_id,
            is_active=True
        ).select_related("employee__user").first()

        if not device:
            return Response({
                "status": "error",
                "code": 404,
                "message": "Device belum terdaftar.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "status": "success",
            "code": 200,
            "message": "Data berhasil diambil",
            "data": {
                "id": device.id,
                "employee_number": device.employee.employee_number,
                "employee_name": device.employee.user.full_name,
                "device_name": device.device_name,
                "device_id": device.device_id,
                "verified": device.is_verified,
                "is_active": device.is_active
            }
        }, status=status.HTTP_200_OK)
    
    # @action(
    #     detail=False,
    #     methods=["post"],
    #     url_path="update-status",
    #     permission_classes=[HasPermission]  # hanya yg sudah diauthentication yang bisa akses
    # )
    @action(
        detail=False,   # 🔥 HARUS False
        methods=["post"],
        url_path="update-status",
        permission_classes=[AllowAny]
    )
    def update_status(self, request):
        device_id = request.data.get("device_id")
        is_active = request.data.get("is_active")
        is_verified = request.data.get("is_verified")

        if not device_id:
            return Response({
                "status": "error",
                "code": 400,
                "message": "device_id wajib diisi.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        if is_active is None:
            return Response({
                "status": "error",
                "code": 400,
                "message": "is_active wajib diisi (true/false).",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        device = EmployeeDevice.objects.filter(device_id=device_id).first()

        if not device:
            return Response({
                "status": "error",
                "code": 404,
                "message": "Device tidak ditemukan.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        device.is_active = is_active
        device.is_verified = is_verified
        device.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Status device berhasil diperbarui.",
            "data": {
                "device_id": device.device_id,
                "is_active": device.is_active,
                "is_verified": device.is_verified
            }
        }, status=status.HTTP_200_OK)
