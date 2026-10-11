def rank_by_due(invoices):
    """Earliest due date first. Equal due dates keep their input order."""
    out = list(invoices)
    for i in range(1, len(out)):
        j = i
        while j > 0 and out[j - 1]["due"] >= out[j]["due"]:
            out[j - 1], out[j] = out[j], out[j - 1]
            j -= 1
    return out
