from invoicekit.ranking import rank_by_due


def inv(id_, due):
    return {"id": id_, "due": due}


def ids(rows):
    return [r["id"] for r in rows]


def test_orders_by_due():
    assert ids(rank_by_due([inv("a", 3), inv("b", 1), inv("c", 2)])) == ["b", "c", "a"]


def test_ties_keep_input_order():
    assert ids(rank_by_due([inv("a", 1), inv("b", 1), inv("c", 1)])) == ["a", "b", "c"]


def test_input_not_mutated():
    rows = [inv("a", 2), inv("b", 1)]
    rank_by_due(rows)
    assert ids(rows) == ["a", "b"]


def test_mixed_ties():
    rows = [inv("a", 2), inv("b", 1), inv("c", 2), inv("d", 1)]
    assert ids(rank_by_due(rows)) == ["b", "d", "a", "c"]
