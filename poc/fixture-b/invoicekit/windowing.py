def slice_window(rows, index, size):
    """Rows in the zero-indexed window `index` of width `size`."""
    lo = index * size
    hi = lo + size - 1
    return list(rows[lo:hi])


def window_count(n_rows, size):
    full, rest = divmod(n_rows, size)
    return full + (1 if rest else 0)
