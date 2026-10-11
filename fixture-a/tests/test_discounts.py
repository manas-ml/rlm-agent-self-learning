from billing_utils.discounts import apply_discount, sum_optional


def test_ten_percent():
    assert apply_discount(1000, 10) == 900


def test_zero_percent():
    assert apply_discount(1000, 0) == 1000


def test_none_means_no_discount():
    assert apply_discount(1000, None) == 1000


def test_sum_skips_none():
    assert sum_optional([100, None, 250]) == 350
    assert sum_optional([]) == 0
