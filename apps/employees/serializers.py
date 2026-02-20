from rest_framework import serializers
from django.db import transaction

from apps.accounts.models import User, Role, UserRole
from .models import (
    Department,
    Position,
    Grade,
    EmploymentStatus,
    Employee,
)
from .utils import generate_employee_number


# ============================================================
# MASTER SERIALIZERS
# ============================================================
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Position
        fields = [
            "id",
            "name",
            "code",
            "department",
            "department_name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = [
            "id",
            "name",
            "code",
            "level",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmploymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentStatus
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ============================================================
# EMPLOYEE SERIALIZERS
# ============================================================
class EmployeeListSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    # employee_id_login = serializers.CharField(source="user.employee_id", read_only=True)
    employee_number_login = serializers.CharField(source="user.employee_id", read_only=True)

    department_name = serializers.CharField(source="department.name", read_only=True)
    position_name = serializers.CharField(source="position.name", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    employment_status_name = serializers.CharField(source="employment_status.name", read_only=True)

    manager_name = serializers.CharField(source="manager.user.full_name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_number",
            "email",
            "employee_number_login",
            "full_name",
            "department",
            "department_name",
            "position",
            "position_name",
            "grade",
            "grade_name",
            "employment_status",
            "employment_status_name",
            "manager",
            "manager_name",
            "is_active_employee",
            "join_date",
            "resign_date",
            "created_at",
            "updated_at",
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    # user info
    email = serializers.CharField(source="user.email", read_only=True)
    # employee_id_login = serializers.CharField(source="user.employee_id", read_only=True)
    employee_number_login = serializers.CharField(source="user.employee_id", read_only=True)

    full_name = serializers.CharField(source="user.full_name", read_only=True)
    user_is_active = serializers.BooleanField(source="user.is_active", read_only=True)

    # master name
    department_name = serializers.CharField(source="department.name", read_only=True)
    position_name = serializers.CharField(source="position.name", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    employment_status_name = serializers.CharField(source="employment_status.name", read_only=True)
    manager_name = serializers.CharField(source="manager.user.full_name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",

            # employee
            "employee_number",
            "nik",
            "phone",
            "address",
            "birth_date",
            "gender",

            "join_date",
            "resign_date",

            "department",
            "department_name",
            "position",
            "position_name",
            "grade",
            "grade_name",
            "employment_status",
            "employment_status_name",

            "manager",
            "manager_name",

            "is_active_employee",

            # user
            "user",
            "email",
            "employee_number_login",
            "full_name",
            "user_is_active",

            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmployeeCreateSerializer(serializers.Serializer):
    """
    Create Employee + create User sekaligus.
    """

    # =========================
    # USER LOGIN DATA
    # =========================
    email = serializers.EmailField()
    # employee_id = serializers.CharField(max_length=50)
    full_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)

    # =========================
    # EMPLOYEE PROFILE DATA
    # =========================
    # employee_number = serializers.CharField(max_length=50)

    nik = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=[("male", "Male"), ("female", "Female")],
        required=False,
        allow_null=True,
    )

    join_date = serializers.DateField(required=False, allow_null=True)

    department = serializers.IntegerField(required=False, allow_null=True)
    position = serializers.IntegerField(required=False, allow_null=True)
    grade = serializers.IntegerField(required=False, allow_null=True)
    employment_status = serializers.IntegerField(required=False, allow_null=True)
    manager = serializers.IntegerField(required=False, allow_null=True)

    is_active_employee = serializers.BooleanField(default=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email sudah digunakan.")
        return value

    # def validate_employee_id(self, value):
    #     if User.objects.filter(employee_id=value).exists():
    #         raise serializers.ValidationError("Employee ID sudah digunakan.")
    #     return value

    # def validate_employee_number(self, value):
    #     if Employee.objects.filter(employee_number=value).exists():
    #         raise serializers.ValidationError("Employee number sudah digunakan.")
    #     return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        # employee_id = validated_data.pop("employee_id")
        employee_number = generate_employee_number()
        full_name = validated_data.pop("full_name")

        user = User.objects.create_user(
            email=email,
            employee_id=employee_number,
            full_name=full_name,
            password=password,
            is_active=True,
        )

        # FK ids
        department_id = validated_data.pop("department", None)
        position_id = validated_data.pop("position", None)
        grade_id = validated_data.pop("grade", None)
        employment_status_id = validated_data.pop("employment_status", None)
        manager_id = validated_data.pop("manager", None)

        # AUTO GENERATE employee_number
        # employee_number = generate_employee_number()

        employee = Employee.objects.create(
            user=user,
            employee_number=employee_number,
            department_id=department_id,
            position_id=position_id,
            grade_id=grade_id,
            employment_status_id=employment_status_id,
            manager_id=manager_id,
            **validated_data,
        )

        # assign default role = Employee
        role_employee = Role.objects.filter(name="Employee").first()
        if role_employee:
            UserRole.objects.get_or_create(user=user, role=role_employee)

        return employee


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """
    Update profile employee (tanpa update user login).
    """
    class Meta:
        model = Employee
        fields = [
            "employee_number",
            "nik",
            "phone",
            "address",
            "birth_date",
            "gender",
            "join_date",
            "resign_date",
            "department",
            "position",
            "grade",
            "employment_status",
            "manager",
            "is_active_employee",
        ]
