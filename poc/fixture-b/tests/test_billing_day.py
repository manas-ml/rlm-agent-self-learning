from datetime import date, datetime, timezone

from invoicekit.billing_day import billing_date, cycle_end

UTC = timezone.utc


def test_same_day_when_no_boundary_crossed():
    assert billing_date(datetime(2024, 6, 15, 12, 0, tzinfo=UTC), 2) == date(2024, 6, 15)


def test_crosses_midnight_forward():
    assert billing_date(datetime(2024, 6, 30, 23, 30, tzinfo=UTC), 2) == date(2024, 7, 1)


def test_crosses_midnight_backward():
    assert billing_date(datetime(2024, 7, 1, 1, 0, tzinfo=UTC), -5) == date(2024, 6, 30)


def test_cycle_end():
    assert cycle_end(date(2024, 1, 1), 30) == date(2024, 1, 30)
