from datetime import timedelta, timezone


def billing_date(ts, tz_offset_hours):
    """Calendar date the customer sees for an aware timestamp `ts`."""
    return ts.date()


def cycle_end(start_date, days):
    return start_date + timedelta(days=days - 1)
