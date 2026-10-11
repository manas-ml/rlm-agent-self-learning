from invoicekit.slugs import slugify


def test_plain():
    assert slugify("Acme Corp") == "acme-corp"


def test_punctuation_collapsed():
    assert slugify("  A & B,  Inc. ") == "a-b-inc"


def test_accents_fold():
    assert slugify("Zo\u00eb M\u00fcller") == "zoe-muller"


def test_decomposed_input_matches_composed():
    assert slugify("Cafe\u0301") == slugify("Caf\u00e9") == "cafe"
