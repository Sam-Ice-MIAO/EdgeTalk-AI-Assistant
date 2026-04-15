# main.py
from reader import read_sales_data
from stats import (
    calculate_total_revenue,
    calculate_average_order_value,
    get_top_product,
)


def main():
    filename = "sales.csv"
    data = read_sales_data(filename)

    if not data:
        print("❌ 没有有效数据，程序退出。")
        return

    print("\n--- 销售明细 ---")
    for record in data:
        print(record)

    print("\n--- 统计结果 ---")
    total_revenue = calculate_total_revenue(data)
    avg_order = calculate_average_order_value(data)
    top_product, top_value = get_top_product(data)

    print(f"总销售收入: ${total_revenue:.2f}")
    print(f"平均订单金额: ${avg_order:.2f}")
    print(f"最畅销产品: {top_product} (销售额: ${top_value:.2f})")


if __name__ == "__main__":
    main()
