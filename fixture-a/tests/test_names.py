from billing_utils.names import normalize_name, same_customer


def test_case_insensitive():
    assert same_customer("ACME Corp", "acme corp")


def test_whitespace_collapsed():
    assert normalize_name("  Acme   Corp ") == "acme corp"


def test_composed_equals_decomposed():
    assert same_customer("Caf\u00e9 Bar", "Cafe\u0301 Bar")


def test_normalized_forms_are_identical_strings():
    assert normalize_name("Cafe\u0301") == normalize_name("Caf\u00e9")
