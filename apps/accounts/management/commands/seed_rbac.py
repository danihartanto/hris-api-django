from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Role, Permission, RolePermission


class Command(BaseCommand):
    help = "Seeder default RBAC: Role, Permission, RolePermission"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Seeding RBAC (Role & Permission)..."))

        # =====================================================
        # 1) DEFINE ROLE DEFAULT
        # =====================================================
        default_roles = [
            {
                "name": "Super Admin",
                "description": "Full akses ke seluruh sistem HRIS",
            },
            {
                "name": "HR Admin",
                "description": "Akses untuk pengelolaan HR & master data",
            },
            {
                "name": "Manager",
                "description": "Akses manajerial untuk approval dan monitoring",
            },
            {
                "name": "Employee",
                "description": "Akses user karyawan biasa",
            },
        ]

        role_objects = {}
        for role_data in default_roles:
            role, created = Role.objects.get_or_create(
                name=role_data["name"],
                defaults={
                    "description": role_data["description"],
                    "is_active": True,
                },
            )
            role_objects[role.name] = role

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Role dibuat: {role.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️ Role sudah ada: {role.name}"))

        # =====================================================
        # 2) DEFINE PERMISSION DEFAULT
        # =====================================================
        # Format:
        # module = fitur
        # action = operasi
        modules = {
            "employees": ["view", "create", "update", "delete"],
            "attendance": ["view", "checkin", "checkout", "update", "delete"],
            "leave": ["view", "create", "approve", "reject", "delete"],
            "payroll": ["view", "generate", "update", "delete"],
            "roles": ["view", "create", "update", "delete", "assign"],
            "permissions": ["view", "create", "update", "delete"],
            "reports": ["view", "export"],
        }

        permission_objects = {}

        for module, actions in modules.items():
            for action in actions:
                name = f"{module.title()} - {action.title()}"
                perm, created = Permission.objects.get_or_create(
                    module=module,
                    action=action,
                    defaults={
                        "name": name,
                        "description": f"Permission untuk {action} pada module {module}",
                        "is_active": True,
                    },
                )
                permission_objects[f"{module}.{action}"] = perm

                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Permission dibuat: {perm.code}"))
                else:
                    self.stdout.write(self.style.WARNING(f"ℹ️ Permission sudah ada: {perm.code}"))

        # =====================================================
        # 3) ASSIGN PERMISSION DEFAULT KE ROLE
        # =====================================================

        def assign_permissions(role_name, perm_codes: list[str]):
            role = role_objects[role_name]
            created_count = 0

            for code in perm_codes:
                perm = permission_objects.get(code)
                if not perm:
                    continue

                obj, created = RolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                )
                if created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(f"🔗 Assign {created_count} permission ke role: {role_name}")
            )

        # ---- Super Admin: semua permission
        assign_permissions("Super Admin", list(permission_objects.keys()))

        # ---- HR Admin: semua kecuali payroll delete (contoh)
        hr_admin_perms = [k for k in permission_objects.keys()]
        assign_permissions("HR Admin", hr_admin_perms)

        # ---- Manager: view + approve/reject + report
        manager_perms = [
            "employees.view",
            "attendance.view",
            "leave.view",
            "leave.approve",
            "leave.reject",
            "payroll.view",
            "reports.view",
            "reports.export",
        ]
        assign_permissions("Manager", manager_perms)

        # ---- Employee: basic
        employee_perms = [
            "employees.view",
            "attendance.view",
            "attendance.checkin",
            "attendance.checkout",
            "leave.view",
            "leave.create",
        ]
        assign_permissions("Employee", employee_perms)

        self.stdout.write(self.style.SUCCESS("🎉 Seeder RBAC selesai!"))
