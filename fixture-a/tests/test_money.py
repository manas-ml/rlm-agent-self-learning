from billing_utils.money import format_cents, to_cents


def test_simple_amount():
    assert to_cents("19.99") == 1999


def test_small_amount():
    assert to_cents("0.10") == 10


def test_large_amount_does_not_wrap():
    assert to_cents("30000000.00") == 3_000_000_000


def test_large_negative_does_not_wrap():
    assert to_cents("-30000000.00") == -3_000_000_000


def test_format_roundtrip():
    assert format_cents(to_cents("12.05")) == "12.05"
