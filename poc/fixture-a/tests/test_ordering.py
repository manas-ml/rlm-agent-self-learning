from billing_utils.ordering import sort_invoices


def inv(id_, amount):
    return {"id": id_, "amount": amount}


def test_descending_by_amount():
    out = sort_invoices([inv("a", 1), inv("b", 3), inv("c", 2)])
    assert [i["id"] for i in out] == ["b", "c", "a"]


def test_ties_keep_input_order():
    out = sort_invoices([inv("a", 5), inv("b", 5), inv("c", 5)])
    assert [i["id"] for i in out] == ["a", "b", "c"]


def test_ties_inside_mixed_input():
    out = sort_invoices([inv("a", 2), inv("b", 9), inv("c", 2), inv("d", 9)])
    assert [i["id"] for i in out] == ["b", "d", "a", "c"]


def test_empty():
    assert sort_invoices([]) == []
