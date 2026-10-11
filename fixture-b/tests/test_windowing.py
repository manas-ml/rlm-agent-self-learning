from invoicekit.windowing import slice_window, window_count

ROWS = list("abcdefg")


def test_full_window():
    assert slice_window(ROWS, 0, 3) == ["a", "b", "c"]


def test_second_window():
    assert slice_window(ROWS, 1, 3) == ["d", "e", "f"]


def test_partial_last_window():
    assert slice_window(ROWS, 2, 3) == ["g"]


def test_window_count():
    assert window_count(7, 3) == 3
    assert window_count(6, 3) == 2
