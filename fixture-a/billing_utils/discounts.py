def apply_discount(total_cents, discount_pct):
    """Apply a percentage discount. None means no discount."""
    return total_cents * (100 - discount_pct) // 100


def sum_optional(values):
    """Sum amounts, ignoring missing (None) entries."""
    return sum(values)
