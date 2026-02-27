from django.contrib import admin

# Register your models here.
from .models import (
    Employee,
    Department,
    Position,
    Grade,
    EmploymentStatus,
)


# ================================
# MASTER DATA
# ================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "department", "is_active", "created_at")
    list_filter = ("is_active", "department")
    search_fields = ("name", "code", "department__name")
    ordering = ("department", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "level", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("level",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmploymentStatus)
class EmploymentStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


# ================================
# EMPLOYEE PROFILE
# ================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee_number",
        "full_name",
        "email",
        "department",
        "position",
        "grade",
        "employment_status",
        "join_date",
        "is_active_employee",
    )

    list_filter = (
        "department",
        "position",
        "grade",
        "employment_status",
        "is_active_employee",
        "gender",
        "join_date",
    )

    search_fields = (
        "employee_number",
        "user__full_name",
        "user__email",
        "nik",
        "phone",
    )

    ordering = ("-join_date",)

    readonly_fields = (
        "employee_number",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("User Account", {
            "fields": ("user", "employee_number")
        }),
        ("Personal Information", {
            "fields": (
                "nik",
                "gender",
                "birth_date",
                "phone",
                "address",
            )
        }),
        ("Employment Info", {
            "fields": (
                "department",
                "position",
                "grade",
                "employment_status",
                "manager",
                "join_date",
                "is_active_employee",
            )
        }),
        ("System", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # =========================
    # Custom display fields
    # =========================
    @admin.display(description="Full Name")
    def full_name(self, obj):
        return obj.user.full_name if obj.user else "-"

    @admin.display(description="Email")
    def email(self, obj):
        return obj.user.email if obj.user else "-"
