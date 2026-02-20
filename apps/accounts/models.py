from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from django.utils.text import slugify
from django.conf import settings

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=30, unique=True, null=True, blank=True)

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def create_superuser(self, email, employee_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, employee_id, password, **extra_fields)
    
    def get_roles(self):
        return Role.objects.filter(role_users__user=self, is_active=True)

    def get_permissions(self):
        """
        Return set of permission code
        contoh: {"employees.view", "leave.approve"}
        """
        perms = Permission.objects.filter(
            permission_roles__role__role_users__user=self,
            is_active=True,
            permission_roles__role__is_active=True,
        ).values_list("code", flat=True)

        return set(perms)

    def has_permission(self, perm_code: str) -> bool:
        return perm_code in self.get_permissions()

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.SlugField(max_length=60, unique=True)
    description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Permission(models.Model):
    """
    Permission model yang cocok untuk UI dinamis.
    Contoh:
    - module = employees
    - action = create
    - code   = employees.create
    """

    module = models.CharField(max_length=50)
    action = models.CharField(max_length=50)

    name = models.CharField(max_length=100)  # label untuk UI
    code = models.CharField(max_length=120, unique=True)

    description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permissions"
        unique_together = ("module", "action")
        ordering = ["module", "action"]

    def save(self, *args, **kwargs):
        # auto generate code jika belum ada
        if not self.code:
            self.code = f"{self.module}.{self.action}".lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="permission_roles")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role_permissions"
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.code} -> {self.permission.code}"


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_users")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_roles"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user.email} -> {self.role.code}"
