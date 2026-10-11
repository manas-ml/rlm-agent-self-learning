from invoicekit.cart import Cart


def test_add_and_count():
    cart = Cart().add("a", 2).add("b")
    assert cart.units() == 3


def test_carts_are_independent():
    first = Cart().add("a", 5)
    second = Cart()
    assert second.units() == 0
    assert first.units() == 5


def test_seeded_cart_is_used():
    seed = [("x", 4)]
    assert Cart(seed).units() == 4
