from decimal import ROUND_HALF_EVEN, Decimal


def vat_amount(net_minor, rate_percent):
    """VAT in minor units. Exact halves round away from zero (half up)."""
    raw = Decimal(net_minor) * Decimal(rate_percent) / Decimal(100)
    return int(raw.quantize(Decimal(1), rounding=ROUND_HALF_EVEN))


def gross(net_minor, rate_percent):
    return net_minor + vat_amount(net_minor, rate_percent)
