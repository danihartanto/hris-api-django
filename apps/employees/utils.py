from django.db import transaction
from django.utils import timezone

from .models import Employee


def generate_employee_number():
    """
    Format: YYYYNNNN
    Contoh: 20260001

    Aman dari race condition dengan select_for_update.
    """
    year = timezone.now().year
    prefix = str(year)

    with transaction.atomic():
        last_employee = (
            Employee.objects.select_for_update()
            .filter(employee_number__startswith=prefix)
            .order_by("-employee_number")
            .first()
        )

        if not last_employee or not last_employee.employee_number:
            return f"{prefix}0001"

        last_number = int(last_employee.employee_number[-4:])
        next_number = last_number + 1

        return f"{prefix}{next_number:04d}"
