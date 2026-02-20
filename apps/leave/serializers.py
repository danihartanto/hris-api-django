from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from django.db import transaction

from apps.employees.models import Employee
from .models import LeaveType, LeaveRequest
from .utils import count_days_inclusive


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    employee_number = serializers.CharField(source="employee.employee_number", read_only=True)
    full_name = serializers.CharField(source="employee.user.full_name", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_number",
            "full_name",
            "leave_type",
            "leave_type_name",
            "start_date",
            "end_date",
            "total_days",
            "reason",
            "attachment",
            "status",
            "rejection_reason",
            "approved_by",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "employee",
            "total_days",
            "status",
            "approved_by",
            "approved_at",
            "rejected_by",
            "rejected_at",
            "created_at",
            "updated_at",
        ]


class LeaveRequestCreateSerializer(serializers.Serializer):
    leave_type = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        request = self.context["request"]

        employee = Employee.objects.filter(user=request.user).first()
        if not employee:
            raise serializers.ValidationError("Employee profile tidak ditemukan.")

        leave_type = LeaveType.objects.filter(id=attrs["leave_type"], is_active=True).first()
        if not leave_type:
            raise serializers.ValidationError("Leave type tidak valid.")

        start_date = attrs["start_date"]
        end_date = attrs["end_date"]

        if end_date < start_date:
            raise serializers.ValidationError("end_date tidak boleh lebih kecil dari start_date.")

        total_days = count_days_inclusive(start_date, end_date)

        # =========================
        # RULE 1: max 3 days in a row (Annual leave only)
        # =========================
        if leave_type.code == "ANNUAL" and total_days > 3:
            raise serializers.ValidationError("Cuti tahunan maksimal 3 hari berturut-turut.")

        # =========================
        # RULE 2: annual leave max 12 days per year
        # =========================
        if leave_type.code == "ANNUAL":
            year = start_date.year

            used = (
                LeaveRequest.objects.filter(
                    employee=employee,
                    leave_type__code="ANNUAL",
                    status="approved",
                    start_date__year=year,
                )
                .aggregate(total=Sum("total_days"))
                .get("total")
                or 0
            )

            if used + total_days > 12:
                raise serializers.ValidationError(
                    f"Jatah cuti tahunan tidak cukup. Sudah terpakai {used} hari, sisa {max(0, 12-used)} hari."
                )

        # =========================
        # RULE 3: half_day max 4 times per month
        # =========================
        if leave_type.code == "HALF_DAY":
            if total_days != 1:
                raise serializers.ValidationError("Half day hanya boleh 1 hari.")

            month = start_date.month
            year = start_date.year

            used_half = LeaveRequest.objects.filter(
                employee=employee,
                leave_type__code="HALF_DAY",
                status="approved",
                start_date__year=year,
                start_date__month=month,
            ).count()

            if used_half >= 4:
                raise serializers.ValidationError("Half day maksimal 4 kali dalam 1 bulan.")

        attrs["employee"] = employee
        attrs["leave_type_obj"] = leave_type
        attrs["total_days"] = total_days
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        employee = validated_data["employee"]
        leave_type = validated_data["leave_type_obj"]

        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
            total_days=validated_data["total_days"],
            reason=validated_data.get("reason"),
            status="pending",
        )

        return leave_request
