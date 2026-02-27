from django.db import models

# Create your models here.

class EmployeeDevice(models.Model):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="devices",
    )

    device_id = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255)
    device_brand = models.CharField(max_length=100, null=True, blank=True)
    device_model = models.CharField(max_length=100, null=True, blank=True)

    os_name = models.CharField(max_length=100)  # Android / iOS
    os_version = models.CharField(max_length=100)

    app_version = models.CharField(max_length=50, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    registered_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-registered_at"]
        unique_together = ("employee", "device_id")

    def __str__(self):
        return f"{self.employee.employee_number} - {self.device_name}"
