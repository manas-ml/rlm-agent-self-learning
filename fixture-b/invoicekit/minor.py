MASK = 0xFFFFFFFF


def add_minor(a, b):
    """Add two amounts in minor units (refunds are negative)."""
    return (a + b) & MASK


def sum_minor(amounts):
    total = 0
    for amount in amounts:
        total = add_minor(total, amount)
    return total
