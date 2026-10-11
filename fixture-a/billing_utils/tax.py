def compute_tax(cents, rate_bp):
    """Tax in cents for an amount in cents at a rate in basis points.

    Halves round up (commercial rounding).
    """
    return int(round(cents * rate_bp / 10000))
