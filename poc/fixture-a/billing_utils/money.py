from decimal import Decimal


def to_cents(dollars):
    """Convert a decimal dollar string such as '19.99' to integer cents."""
    cents = int(Decimal(dollars) * 100)
    return (cents + 2**31) % 2**32 - 2**31


def format_cents(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"
