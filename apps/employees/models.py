from django.db import models

# Create your models here.
from django.conf import settings


# ============================================================
# ABSTRACT BASE
# ============================================================
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================
# MASTER TABLES
# ============================================================
class Department(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "departments"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Position(TimeStampedModel):
    """
    Position/Jabatan.
    Bisa dihubungkan ke Department (jabatan biasanya ada di departemen).
    """
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30, unique=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="positions",
        blank=True,
        null=True,
    )

    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "positions"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name", "department"], name="unique_position_per_department")
        ]

    def __str__(self):
        if self.department:
            return f"{self.name} ({self.department.name})"
        return self.name


class Grade(TimeStampedModel):
    """
    Grade/Golongan.
    Biasanya dipakai payroll, benefit, approval, dll.
    """
    name = models.CharField(max_length=50)  # contoh: Grade 1, Grade 2
    code = models.CharField(max_length=30, unique=True)  # contoh: G1, G2
    level = models.PositiveIntegerField(default=1)  # 1..n

    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "grades"
        ordering = ["level"]

    def __str__(self):
        return f"{self.name} (Level {self.level})"


class EmploymentStatus(TimeStampedModel):
    """
    Status hubungan kerja:
    - Permanent
    - Contract
    - Internship
    - Probation
    - Outsource
    """
    name = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employment_statuses"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ============================================================
# EMPLOYEE PROFILE
# ============================================================
class Employee(TimeStampedModel):
    """
    Employee profile (data HR).
    User login = accounts.User
    Employee profile = employees.Employee
    """

    # 1 user = 1 employee
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )

    # Nomor karyawan HR (boleh beda dengan employee_id di user)
    # employee_number = models.CharField(max_length=50, unique=True)
    employee_number = models.CharField(max_length=50, unique=True, blank=True)  #buat generate nopeg YYYYNNNN


    # Personal info
    nik = models.CharField(max_length=30, blank=True, null=True)  # NIK KTP
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "Male"),
            ("female", "Female"),
        ],
        blank=True,
        null=True,
    )

    # Employment info
    join_date = models.DateField(blank=True, null=True)
    resign_date = models.DateField(blank=True, null=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        blank=True,
        null=True,
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="employees",
        blank=True,
        null=True,
    )

    grade = models.ForeignKey(
        Grade,
        on_delete=models.PROTECT,
        related_name="employees",
        blank=True,
        null=True,
    )

    employment_status = models.ForeignKey(
        EmploymentStatus,
        on_delete=models.PROTECT,
        related_name="employees",
        blank=True,
        null=True,
    )

    # Manager / Atasan
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="subordinates",
        blank=True,
        null=True,
    )

    # HR flags
    is_active_employee = models.BooleanField(default=True)

    class Meta:
        db_table = "employees"
        ordering = ["employee_number"]

    def __str__(self):
        return f"{self.employee_number} - {self.user.full_name}"
