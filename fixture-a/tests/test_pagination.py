from billing_utils.pagination import page_count, paginate

ITEMS = list(range(1, 11))


def test_first_page():
    assert paginate(ITEMS, 1, 3) == [1, 2, 3]


def test_last_partial_page():
    assert paginate(ITEMS, 4, 3) == [10]


def test_empty_input():
    assert paginate([], 1, 5) == []


def test_page_count_rounds_up():
    assert page_count(10, 3) == 4
    assert page_count(9, 3) == 3
