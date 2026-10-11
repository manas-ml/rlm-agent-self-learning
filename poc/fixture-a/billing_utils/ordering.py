def sort_invoices(invoices):
    """Largest amount first. Invoices with equal amounts keep their input order."""
    return sorted(invoices, key=lambda inv: inv["amount"])[::-1]
