from django.core.management.base import BaseCommand
from apps.leave.models import LeaveType


class Command(BaseCommand):
    help = "Seed default leave types"

    def handle(self, *args, **options):
        data = [
            ("ANNUAL", "Annual Leave", "Cuti tahunan (maks 3 hari beruntun, 12 hari per tahun)"),
            ("SICK", "Sick Leave", "Cuti sakit (tidak terbatas)"),
            ("HALF_DAY", "Half Day", "Izin setengah hari (maks 4 kali per bulan)"),
        ]

        for code, name, desc in data:
            obj, created = LeaveType.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "is_active": True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ LeaveType dibuat: {code}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️ LeaveType sudah ada: {code}"))
