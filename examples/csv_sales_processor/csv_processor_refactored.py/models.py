# models.py
class SaleRecord:
    def __init__(self, name, product, price, quantity):
        self.name = name
        self.product = product
        self.price = float(price)
        self.quantity = int(quantity)

    def total_cost(self) -> float:
        return self.price * self.quantity

    def __repr__(self):
        return f"{self.name} bought {self.product} for ${self.total_cost():.2f}"
