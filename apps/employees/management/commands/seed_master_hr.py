from django.core.management.base import BaseCommand
from django.db import transaction

from apps.employees.models import (
    Department,
    Position,
    Grade,
    EmploymentStatus,
)


class Command(BaseCommand):
    help = "Seeder master HR: Department, Position, Grade, EmploymentStatus"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Seeding Master HR..."))

        # =====================================================
        # 1) EMPLOYMENT STATUS
        # =====================================================
        statuses = [
            ("Permanent", "PERMANENT", "Karyawan tetap"),
            ("Contract", "CONTRACT", "Karyawan kontrak"),
            ("Probation", "PROBATION", "Karyawan masa percobaan"),
            ("Internship", "INTERNSHIP", "Karyawan magang"),
            ("Outsource", "OUTSOURCE", "Tenaga kerja outsource"),
        ]

        for name, code, desc in statuses:
            obj, created = EmploymentStatus.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ EmploymentStatus dibuat: {obj.code}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️ EmploymentStatus sudah ada: {obj.code}"))

        # =====================================================
        # 2) GRADES
        # =====================================================
        grades = [
            ("Grade 1", "G1", 1, "Entry level"),
            ("Grade 2", "G2", 2, "Junior"),
            ("Grade 3", "G3", 3, "Middle"),
            ("Grade 4", "G4", 4, "Senior"),
            ("Grade 5", "G5", 5, "Lead / Supervisor"),
            ("Grade 6", "G6", 6, "Manager"),
        ]

        for name, code, level, desc in grades:
            obj, created = Grade.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "level": level,
                    "description": desc,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Grade dibuat: {obj.code}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️ Grade sudah ada: {obj.code}"))

        # =====================================================
        # 3) DEPARTMENTS
        # =====================================================
        departments = [
            ("Human Resource", "HR", "Divisi HR"),
            ("Information Technology", "IT", "Divisi IT"),
            ("Finance", "FIN", "Divisi Finance"),
            ("Operations", "OPS", "Divisi Operasional"),
            ("Procurement", "PROC", "Divisi Procurement"),
        ]

        dept_objects = {}

        for name, code, desc in departments:
            obj, created = Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "is_active": True,
                },
            )
            dept_objects[code] = obj

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Department dibuat: {obj.code}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️ Department sudah ada: {obj.code}"))

        # =====================================================
        # 4) POSITIONS (JABATAN)
        # =====================================================
        positions = [
            # HR
            ("HR Staff", "HR_STAFF", "HR"),
            ("HR Admin", "HR_ADMIN", "HR"),
            ("HR Manager", "HR_MANAGER", "HR"),

            # IT
            ("Backend Developer", "BE_DEV", "IT"),
            ("Frontend Developer", "FE_DEV", "IT"),
            ("Mobile Developer", "MOB_DEV", "IT"),
            ("DevOps Engineer", "DEVOPS", "IT"),
            ("IT Manager", "IT_MANAGER", "IT"),

            # Finance
            ("Finance Staff", "FIN_STAFF", "FIN"),
            ("Accountant", "ACCOUNTANT", "FIN"),
            ("Finance Manager", "FIN_MANAGER", "FIN"),

            # Operations
            ("Operator", "OPERATOR", "OPS"),
            ("Supervisor", "SUPERVISOR", "OPS"),
            ("Operations Manager", "OPS_MANAGER", "OPS"),
        ]

        for name, code, dept_code in positions:
            dept = dept_objects.get(dept_code)

            obj, created = Position.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department": dept,
                    "description": f"Jabatan {name} di departemen {dept.name if dept else '-'}",
                    "is_active": True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Position dibuat: {obj.code}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️ Position sudah ada: {obj.code}"))

        self.stdout.write(self.style.SUCCESS("🎉 Seeder Master HR selesai!"))
