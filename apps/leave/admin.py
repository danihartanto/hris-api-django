from django.contrib import admin

# Register your models here.
from django.utils import timezone

from .models import LeaveType, LeaveRequest


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee_number",
        "employee_name",
        "leave_type",
        "start_date",
        "end_date",
        "total_days",
        "status",
        "approved_by_name",
        "approved_at",
        "created_at",
    )

    list_filter = (
        "status",
        "leave_type",
        "start_date",
        "end_date",
        "created_at",
    )

    search_fields = (
        "employee__employee_number",
        "employee__user__full_name",
        "employee__user__email",
        "leave_type__code",
        "leave_type__name",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "total_days",
        "approved_at",
        "rejected_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Employee", {"fields": ("employee", "leave_type")}),
        ("Leave Date", {"fields": ("start_date", "end_date", "total_days")}),
        ("Request Info", {"fields": ("reason", "attachment")}),
        ("Status", {"fields": ("status",)}),
        ("Approval / Rejection", {"fields": ("approved_by", "approved_at", "rejected_by", "rejected_at", "rejection_reason")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    actions = ["approve_selected", "reject_selected"]

    # =========================
    # Custom columns
    # =========================
    @admin.display(description="Employee Number")
    def employee_number(self, obj):
        return obj.employee.employee_number if obj.employee else "-"

    @admin.display(description="Employee Name")
    def employee_name(self, obj):
        return obj.employee.user.full_name if obj.employee and obj.employee.user else "-"

    @admin.display(description="Approved By")
    def approved_by_name(self, obj):
        if obj.approved_by and obj.approved_by.user:
            return obj.approved_by.user.full_name
        return "-"

    # =========================
    # Admin actions
    # =========================
    @admin.action(description="Approve selected leave requests")
    def approve_selected(self, request, queryset):
        """
        Approve massal (yang masih pending).
        approved_by = employee dari admin yang login (jika punya profile employee).
        """
        approver_employee = getattr(request.user, "employee_profile", None)

        updated = 0
        for leave in queryset:
            if leave.status != "pending":
                continue

            leave.status = "approved"
            leave.approved_at = timezone.now()
            leave.rejected_at = None
            leave.rejection_reason = None

            if approver_employee:
                leave.approved_by = approver_employee

            leave.save()
            updated += 1

        self.message_user(request, f"{updated} leave request berhasil di-approve.")

    @admin.action(description="Reject selected leave requests")
    def reject_selected(self, request, queryset):
        """
        Reject massal (yang masih pending).
        """
        rejector_employee = getattr(request.user, "employee_profile", None)

        updated = 0
        for leave in queryset:
            if leave.status != "pending":
                continue

            leave.status = "rejected"
            leave.rejected_at = timezone.now()
            leave.approved_at = None

            if rejector_employee:
                leave.rejected_by = rejector_employee

            leave.save()
            updated += 1

        self.message_user(request, f"{updated} leave request berhasil di-reject.")
