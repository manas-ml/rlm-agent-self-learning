from billing_utils.line_items import add_line, total


def test_explicit_list_is_extended():
    lines = []
    out = add_line("widget", 500, lines)
    assert out is lines
    assert total(lines) == 500


def test_fresh_list_each_call():
    first = add_line("a", 100)
    second = add_line("b", 200)
    assert len(first) == 1
    assert len(second) == 1


def test_calls_do_not_leak_state():
    add_line("a", 100)
    assert total(add_line("b", 50)) == 50
