"""
Task 3, Step 1: make the data file the dashboard reads.

Input:  online_retail_clean.csv from the Task 2 project
Output: data/sales.csv.gz (the same rows, compressed, so it fits on GitHub)

    python prepare_data.py --input path/to/online_retail_clean.csv
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

COLUMNS = [
    "InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice",
    "CustomerID", "Country", "Revenue", "HasCustomerID",
    "IsQuantityOutlier", "IsPriceOutlier",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Task 2 online_retail_clean.csv")
    parser.add_argument("--output", default="data/sales.csv.gz")
    args = parser.parse_args()

    source = Path(args.input)
    if not source.exists():
        sys.exit(f"File not found: {source}\nRun the Task 2 script first.")

    sales = pd.read_csv(source, usecols=COLUMNS, dtype={"InvoiceNo": str, "StockCode": str})
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    sales[COLUMNS].to_csv(target, index=False, compression="gzip")

    size_mb = target.stat().st_size / 1024 / 1024
    print(f"Saved {len(sales):,} rows to {target} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
