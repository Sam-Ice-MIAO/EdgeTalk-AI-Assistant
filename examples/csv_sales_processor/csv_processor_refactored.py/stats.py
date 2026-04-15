# stats.py
from models import SaleRecord


def calculate_total_revenue(records):
    total_revenue = sum(record.total_cost() for record in records)
    return total_revenue


def calculate_average_order_value(records):
    if not records:
        return 0.0
    total_revenue = calculate_total_revenue(records)
    return total_revenue / len(records)


def get_top_product(records):
    from collections import defaultdict

    product_sales = defaultdict(float)
    for record in records:
        product_sales[record.product] += record.total_cost()
    return (
        max(product_sales.items(), key=lambda x: x[1]) if product_sales else ("无", 0.0)
    )
