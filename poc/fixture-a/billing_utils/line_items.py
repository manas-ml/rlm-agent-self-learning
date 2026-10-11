def add_line(description, cents, lines=[]):
    """Append a line to `lines` (or to a fresh list) and return it."""
    lines.append({"description": description, "cents": cents})
    return lines


def total(lines):
    return sum(line["cents"] for line in lines)
