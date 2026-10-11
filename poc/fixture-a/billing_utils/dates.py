from datetime import datetime, timedelta, timezone


def due_at_utc(issued, net_days):
    """Due moment in UTC. Naive datetimes are assumed to already be UTC."""
    return issued.replace(tzinfo=timezone.utc) + timedelta(days=net_days)


def is_overdue(due, now):
    return now > due
