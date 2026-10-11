class Cart:
    def __init__(self, items=[]):
        self.items = items

    def add(self, sku, qty=1):
        self.items.append((sku, qty))
        return self

    def units(self):
        return sum(q for _, q in self.items)
