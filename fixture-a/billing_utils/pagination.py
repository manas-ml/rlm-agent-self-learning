from math import ceil


def paginate(items, page, per_page):
    """Return the items on a 1-indexed page."""
    start = page * per_page
    return list(items[start:start + per_page])


def page_count(total_items, per_page):
    return total_items // per_page
