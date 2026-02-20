from django.db import models

# Create your models here.
from django.utils import timezone

from apps.employees.models import Employee


class AttendanceSetting(models.Model):
    """
    Setting global jam kerja.
    """
    work_start_time = models.TimeField(default="08:00:00")
    work_end_time = models.TimeField(default="17:00:00")
    late_tolerance_minutes = models.PositiveIntegerField(default=15)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_settings"

    def __str__(self):
        return f"Work {self.work_start_time} - {self.work_end_time}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ("on_time", "On Time"),
        ("late", "Late"),
        ("absent", "Absent"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(default=timezone.localdate)

    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)

    check_in_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    check_in_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    check_in_location_name = models.CharField(max_length=255, null=True, blank=True)

    check_out_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    check_out_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    check_out_location_name = models.CharField(max_length=255, null=True, blank=True)

    check_in_photo = models.ImageField(upload_to="attendance/checkin/", null=True, blank=True)
    check_out_photo = models.ImageField(upload_to="attendance/checkout/", null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="on_time")
    working_minutes = models.PositiveIntegerField(default=0)
    working_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)


    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendances"
        unique_together = ("employee", "date")
        ordering = ["-date", "-check_in_time"]

    def __str__(self):
        return f"{self.employee.employee_number} - {self.date}"
