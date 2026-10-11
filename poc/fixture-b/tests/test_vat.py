from invoicekit.vat import gross, vat_amount


def test_whole_result():
    assert vat_amount(2000, "20") == 400


def test_below_half():
    assert vat_amount(12, "10") == 1


def test_half_goes_up_when_even_neighbour():
    assert vat_amount(25, "10") == 3


def test_half_goes_up_when_odd_neighbour():
    assert vat_amount(5, "10") == 1


def test_gross():
    assert gross(25, "10") == 28
