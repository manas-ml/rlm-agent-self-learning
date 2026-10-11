from datetime import datetime, timedelta, timezone

from billing_utils.dates import due_at_utc, is_overdue

PLUS5 = timezone(timedelta(hours=5))
UTC = timezone.utc


def test_naive_is_treated_as_utc():
    got = due_at_utc(datetime(2024, 3, 1, 12, 0), 30)
    assert got == datetime(2024, 3, 31, 12, 0, tzinfo=UTC)


def test_offset_is_converted_to_utc():
    issued = datetime(2024, 3, 1, 23, 0, tzinfo=PLUS5)
    assert due_at_utc(issued, 30) == datetime(2024, 3, 31, 18, 0, tzinfo=UTC)


def test_result_is_utc_aware():
    issued = datetime(2024, 3, 1, 23, 0, tzinfo=PLUS5)
    assert due_at_utc(issued, 1).utcoffset() == timedelta(0)


def test_is_overdue():
    due = datetime(2024, 1, 1, tzinfo=UTC)
    assert is_overdue(due, datetime(2024, 1, 2, tzinfo=UTC))
    assert not is_overdue(due, datetime(2023, 12, 31, tzinfo=UTC))
