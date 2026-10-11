def balance_after(invoice):
    """Amount still owed on an invoice dict. `credit` may be missing or None."""
    return invoice["total"] - invoice.get("credit", 0)


def total_credits(invoices):
    return sum(inv.get("credit", 0) for inv in invoices)
