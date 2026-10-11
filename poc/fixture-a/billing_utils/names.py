def normalize_name(name):
    """Canonical form of a customer name for matching."""
    return " ".join(name.split()).casefold()


def same_customer(a, b):
    return normalize_name(a) == normalize_name(b)
