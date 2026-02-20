from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Role, Permission, RolePermission, UserRole, User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login pakai:
    - email
    - atau employee_id
    """

    username_field = "email"

    def validate(self, attrs):
        login_value = attrs.get("email")  # default field SimpleJWT
        password = attrs.get("password")

        if not login_value or not password:
            raise serializers.ValidationError("Email/Employee ID dan password wajib diisi.")

        # 1) coba cari user via email
        user = User.objects.filter(email__iexact=login_value).first()

        # 2) kalau tidak ketemu, coba employee_id
        if user is None:
            user = User.objects.filter(employee_id__iexact=login_value).first()

        if user is None:
            raise serializers.ValidationError("User tidak ditemukan.")

        # cek password
        if not user.check_password(password):
            raise serializers.ValidationError("Password salah.")

        if not user.is_active:
            raise serializers.ValidationError("Akun nonaktif.")

        # lanjut generate token (SimpleJWT)
        data = super().validate({"email": user.email, "password": password})

        # tambahan response payload
        data["user"] = {
            "id": user.id,
            "email": user.email,
            "employee_id": user.employee_id,
            "full_name": user.full_name,
            "is_staff": user.is_staff,
        }

        return data

# untuk melihat profile diri sendiri
class MeSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    permissions_grouped = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "employee_id",
            "full_name",
            "is_active",
            "roles",
            "permissions",
            "permissions_grouped",
        ]

    def get_roles(self, obj):
        roles = Role.objects.filter(
            role_users__user=obj,
            is_active=True
        ).order_by("name")
        return RoleSerializer(roles, many=True).data

    def get_permissions(self, obj):
        perms = Permission.objects.filter(
            permission_roles__role__role_users__user=obj,
            is_active=True
        ).distinct().order_by("module", "action")
        return PermissionSerializer(perms, many=True).data

    def get_permissions_grouped(self, obj):
        perms = Permission.objects.filter(
            permission_roles__role__role_users__user=obj,
            is_active=True
        ).distinct().order_by("module", "action")

        grouped = {}
        for p in perms:
            grouped.setdefault(p.module, [])
            grouped[p.module].append(p.code)

        return grouped


# create new employee
class CreateEmployeeUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "employee_id",
            "full_name",
            "password",
            "is_active",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email sudah digunakan.")
        return value

    def validate_employee_id(self, value):
        if User.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID sudah digunakan.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# ==========================
# PERMISSION
# ==========================   
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            "id",
            "module",
            "action",
            "name",
            "code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]


# ==========================
# ROLE
# ==========================
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "code",
            "description",
            "is_active",
            "permissions",
            "created_at",
            "updated_at",
        ]

    def get_permissions(self, obj):
        perms = Permission.objects.filter(
            permission_roles__role=obj,
            is_active=True,
        ).order_by("module", "action")

        return PermissionSerializer(perms, many=True).data


# ==========================
# USER
# ==========================
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "employee_id", "full_name", "is_active"]


class UserRoleDetailSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "employee_id", "full_name", "is_active", "roles"]

    def get_roles(self, obj):
        roles = Role.objects.filter(
            role_users__user=obj,
            is_active=True,
        ).order_by("name")

        return RoleSerializer(roles, many=True).data


# ==========================
# ASSIGN SERIALIZERS
# ==========================
class AssignPermissionToRoleSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )


class AssignRoleToUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
