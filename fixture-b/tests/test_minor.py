from invoicekit.minor import add_minor, sum_minor


def test_small_sum():
    assert sum_minor([100, 250, 50]) == 400


def test_empty_sum():
    assert sum_minor([]) == 0


def test_refund_can_net_negative():
    assert add_minor(100, -250) == -150


def test_sum_beyond_32_bits():
    assert sum_minor([3_000_000_000, 3_000_000_000]) == 6_000_000_000
