"""Run from the project folder: python -m pytest tests  (or: python tests/test_dashboard_logic.py)"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dashboard_logic as logic


def make_sales():
    rows = [
        # invoice, date, country, customer, qty, price, qty outlier, price outlier
        ("1", "2011-01-10 10:00", "France", 100, 2, 5.0, False, False),
        ("1", "2011-01-10 10:00", "France", 100, 1, 10.0, False, False),
        ("2", "2011-01-31 23:30", "Ireland", None, 3, 2.0, False, False),
        ("3", "2011-02-01 09:00", "France", 200, 50, 4.0, True, False),
        ("4", "2011-03-15 12:00", "Germany", 100, 1, 300.0, False, True),
    ]
    frame = pd.DataFrame(rows, columns=[
        "InvoiceNo", "InvoiceDate", "Country", "CustomerID", "Quantity", "UnitPrice",
        "IsQuantityOutlier", "IsPriceOutlier",
    ])
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"])
    frame["CustomerID"] = frame["CustomerID"].astype("Int64")
    frame["Country"] = frame["Country"].astype("category")
    frame["Description"] = pd.Categorical(["A", "B", "A", "C", "D"])
    frame["Revenue"] = frame["Quantity"] * frame["UnitPrice"]
    frame["HasCustomerID"] = frame["CustomerID"].notna()
    frame["OrderValue"] = frame.groupby("InvoiceNo")["Revenue"].transform("sum")
    return frame


def test_kpis_are_correct():
    kpis = logic.compute_kpis(make_sales())
    assert kpis == {"revenue": 526.0, "orders": 4, "average_order_value": 131.5,
                    "units": 57, "customers": 2}


def test_end_date_includes_the_whole_day():
    result = logic.filter_sales(make_sales(), "2011-01-31", "2011-01-31")
    assert list(result["InvoiceNo"]) == ["2"]


def test_filters_combine():
    sales = make_sales()
    assert len(logic.filter_sales(sales, "2011-01-01", "2011-12-31", countries=["France"])) == 3
    assert len(logic.filter_sales(sales, "2011-01-01", "2011-12-31", customer_type=logic.GUESTS)) == 1
    assert len(logic.filter_sales(sales, "2011-01-01", "2011-12-31", customer_type=logic.REGISTERED)) == 4
    assert len(logic.filter_sales(sales, "2011-01-01", "2011-12-31", include_outliers=False)) == 3


def test_threshold_keeps_whole_invoices():
    result = logic.filter_sales(make_sales(), "2011-01-01", "2011-12-31", min_order_value=20)
    assert sorted(result["InvoiceNo"].unique()) == ["1", "3", "4"]
    assert len(result[result["InvoiceNo"] == "1"]) == 2


def test_zero_results_do_not_crash():
    empty = logic.filter_sales(make_sales(), "2015-01-01", "2015-12-31")
    assert empty.empty
    assert logic.compute_kpis(empty)["average_order_value"] == 0.0
    assert logic.monthly_revenue(empty).empty
    assert logic.top_products(empty).empty
    assert logic.revenue_by_country(empty).empty
    assert logic.customer_activity(empty).empty


def test_totals_reconcile_across_every_group():
    sales = make_sales()
    total = logic.compute_kpis(sales)["revenue"]
    assert logic.monthly_revenue(sales)["Revenue"].sum() == total
    assert logic.top_products(sales, limit=100)["Revenue"].sum() == total
    assert logic.revenue_by_country(sales, limit=100)["Revenue"].sum() == total


def test_customer_activity_leaves_out_guests():
    table = logic.customer_activity(make_sales()).set_index("CustomerID")
    assert table.loc["100", "Orders"] == 2
    assert table.loc["100", "Revenue"] == 320.0
    assert len(table) == 2


def test_partial_month_detection():
    frame = pd.DataFrame({"InvoiceDate": pd.to_datetime(["2011-12-09 12:00"])})
    assert logic.last_month_is_partial(frame)
    frame = pd.DataFrame({"InvoiceDate": pd.to_datetime(["2011-11-30 12:00"])})
    assert not logic.last_month_is_partial(frame)


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("passed:", name)
