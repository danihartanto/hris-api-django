from datetime import timedelta


def count_days_inclusive(start_date, end_date):
    """
    Hitung hari inclusive:
    2026-02-01 s/d 2026-02-03 = 3 hari
    """
    delta = end_date - start_date
    return delta.days + 1
