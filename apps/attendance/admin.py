from django.contrib import admin

# Register your models here.
from .models import Attendance, AttendanceSetting


@admin.register(AttendanceSetting)
class AttendanceSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "work_start_time",
        "work_end_time",
        "late_tolerance_minutes",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("id",)
    ordering = ("-id",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "employee",
        "get_employee_number",
        "get_full_name",
        "status",
        "check_in_time",
        "check_out_time",
        "working_minutes",
        "working_hours",
        "check_in_location_name",
        "check_out_location_name",
        "created_at",
    )

    list_filter = (
        "date",
        "status",
        "employee__department",
        "employee__position",
        "employee__employment_status",
    )

    search_fields = (
        "employee__employee_number",
        "employee__user__full_name",
        "employee__user__email",
        "check_in_location_name",
        "check_out_location_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-date", "-check_in_time")

    def get_employee_number(self, obj):
        return obj.employee.employee_number

    get_employee_number.short_description = "Employee Number"

    def get_full_name(self, obj):
        return obj.employee.user.full_name

    get_full_name.short_description = "Full Name"
