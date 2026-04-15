# reader.py
import csv
from models import SaleRecord


def read_sales_data(filename):
    sales_records = []
    try:
        with open(filename, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                record = SaleRecord(
                    row["Name"], row["Product"], row["Price"], row["Quantity"]
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
