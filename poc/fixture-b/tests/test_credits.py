from invoicekit.credits import balance_after, total_credits


def test_with_credit():
    assert balance_after({"total": 100, "credit": 30}) == 70


def test_missing_credit():
    assert balance_after({"total": 100}) == 100


def test_none_credit():
    assert balance_after({"total": 100, "credit": None}) == 100


def test_total_credits_with_none_entries():
    invs = [{"credit": 5}, {"credit": None}, {}, {"credit": 10}]
    assert total_credits(invs) == 15
