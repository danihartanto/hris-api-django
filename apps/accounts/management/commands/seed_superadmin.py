import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from apps.accounts.models import User, Role, UserRole


class Command(BaseCommand):
    help = "Seeder default Super Admin user (sekali run, aman dijalankan berkali-kali)"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Seeding Super Admin user..."))

        # =========================
        # Default value (bisa override dari .env)
        # =========================
        default_email = os.getenv("SUPERADMIN_EMAIL", "admin@hris.com")
        default_employee_id = os.getenv("SUPERADMIN_EMPLOYEE_ID", "SA0001")
        default_password = os.getenv("SUPERADMIN_PASSWORD", "Admin123!")

        full_name = os.getenv("SUPERADMIN_FULLNAME", "Super Admin")

        # =========================
        # Pastikan role Super Admin ada
        # =========================
        role = Role.objects.filter(name="Super Admin").first()
        if not role:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Role 'Super Admin' belum ada. Jalankan dulu: python manage.py seed_rbac"
                )
            )
            return

        # =========================
        # Cari user berdasarkan email ATAU employee_id
        # =========================
        user = User.objects.filter(email=default_email).first()
        if not user:
            user = User.objects.filter(employee_id=default_employee_id).first()

        if user:
            self.stdout.write(self.style.WARNING(f"ℹ️ User sudah ada: {user.email}"))

            # Pastikan role ter-assign
            _, created = UserRole.objects.get_or_create(user=user, role=role)
            if created:
                self.stdout.write(self.style.SUCCESS("🔗 Role Super Admin berhasil di-assign."))
            else:
                self.stdout.write(self.style.WARNING("ℹ️ Role Super Admin sudah ter-assign."))

            return

        # =========================
        # Buat user baru
        # =========================
        user = User.objects.create_superuser(
            email=default_email,
            employee_id=default_employee_id,
            password=default_password,
            full_name=full_name,
        )

        # assign role
        UserRole.objects.get_or_create(user=user, role=role)

        self.stdout.write(self.style.SUCCESS("✅ Super Admin berhasil dibuat!"))
        self.stdout.write(self.style.SUCCESS(f"📧 Email       : {default_email}"))
        self.stdout.write(self.style.SUCCESS(f"🆔 Employee ID : {default_employee_id}"))
        self.stdout.write(self.style.SUCCESS(f"🔑 Password    : {default_password}"))

        self.stdout.write(self.style.SUCCESS("🎉 Seeder Super Admin selesai!"))
