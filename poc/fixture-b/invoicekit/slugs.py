import re


def slugify(name):
    """ASCII slug for a customer id. Accented letters fold to their base letter."""
    ascii_name = name.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
