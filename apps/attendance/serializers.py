from rest_framework import serializers
from django.utils import timezone

from .models import Attendance, AttendanceSetting


class AttendanceSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSetting
        fields = "__all__"


class AttendanceSerializer(serializers.ModelSerializer):
    employee_number = serializers.CharField(source="employee.employee_number", read_only=True)
    full_name = serializers.CharField(source="employee.user.full_name", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_number",
            "full_name",
            "date",

            "check_in_time",
            "check_out_time",

            "check_in_lat",
            "check_in_lng",
            "check_in_location_name",
            "check_out_lat",
            "check_out_lng",
            "check_out_location_name",

            "check_in_photo",
            "check_out_photo",

            "status",
            "working_minutes",
            "working_hours",
            "notes",

            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "date",
            "check_in_time",
            "check_out_time",
            "status",
            "working_minutes",
            "working_hours",
            "created_at",
            "updated_at",
        ]
