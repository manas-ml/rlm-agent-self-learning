from billing_utils.tax import compute_tax


def test_exact_amount():
    assert compute_tax(1000, 1000) == 100


def test_rounds_down_below_half():
    assert compute_tax(14, 1000) == 1


def test_half_rounds_up_from_even():
    assert compute_tax(50, 500) == 3


def test_half_rounds_up_from_zero():
    assert compute_tax(10, 500) == 1
