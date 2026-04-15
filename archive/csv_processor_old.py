import csv

class SaleRecord:
    def __init__(self, name, product, price, quantity):
        self.name = name
        self.product = product
        self.price = float(price)
        self.quantity = int(quantity)

    def total_cost(self):
        return self.price * self.quantity

    def __repr__(self):
        return f"{self.name} bought {self.product} for ${self.total_cost():.2f}"


def read_sales_data(filename):
    sales_records = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                record = SaleRecord(
                    row['Name'],
                    row['Product'],
                    row['Price'],
                    row['Quantity']
                )
                sales_records.append(record)
        print(f"成功从 {filename} 读取数据。")
        return sales_records
        
    except FileNotFoundError:
        print(f"错误：找不到文件 '{filename}'")
        return []
    except KeyError as e:
        print(f"错误：CSV 文件缺少必要的列 '{e}'")
        return []


def calculate_total_revenue(records):
    total_revenue = sum(record.total_cost() for record in records)
    return total_revenue

if __name__ == "__main__":
    data = read_sales_data("sales.csv")
    if data:
        print("\n--- 销售明细 ---")
        for record in data:
            print(record)
        revenue = calculate_total_revenue(data)
        print("\n--- 统计结果 ---")
        print(f"总销售收入: ${revenue:.2f}")

