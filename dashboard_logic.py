"""
Task 3, Step 2: the calculations behind the dashboard.

There is no Streamlit code in this file. Each function takes a table and returns
a table or numbers, so the logic can be tested without opening the app.
"""

import pandas as pd

ALL_CUSTOMERS = "All customers"
REGISTERED = "Registered customers"
GUESTS = "Guest checkouts"


def load_sales(path):
    sales = pd.read_csv(
        path,
        dtype={"InvoiceNo": str, "StockCode": str, "Description": "category", "Country": "category"},
        parse_dates=["InvoiceDate"],
    )
    sales["CustomerID"] = sales["CustomerID"].astype("Int64")
    # OrderValue is the total of the whole invoice, used by the threshold filter.
    sales["OrderValue"] = sales.groupby("InvoiceNo")["Revenue"].transform("sum")
    return sales


def filter_sales(sales, start_date, end_date, countries=(), customer_type=ALL_CUSTOMERS,
                 min_order_value=0.0, include_outliers=True):
    """Return the rows that match every filter. No countries chosen means all countries."""
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date) + pd.Timedelta(days=1)  # include the whole last day
    mask = (sales["InvoiceDate"] >= start) & (sales["InvoiceDate"] < end)

    if len(countries) > 0:
        mask &= sales["Country"].isin(list(countries))
    if customer_type == REGISTERED:
        mask &= sales["HasCustomerID"]
    elif customer_type == GUESTS:
        mask &= ~sales["HasCustomerID"]
    if min_order_value > 0:
        mask &= sales["OrderValue"] >= min_order_value
    if not include_outliers:
        mask &= ~(sales["IsQuantityOutlier"] | sales["IsPriceOutlier"])
    return sales[mask]


def compute_kpis(sales):
    orders = sales["InvoiceNo"].nunique()
    revenue = float(sales["Revenue"].sum())
    return {
        "revenue": revenue,
        "orders": orders,
        "average_order_value": revenue / orders if orders else 0.0,
        "units": int(sales["Quantity"].sum()),
        "customers": int(sales["CustomerID"].nunique()),
    }


def monthly_revenue(sales):
    months = sales["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    table = sales.groupby(months)["Revenue"].sum().reset_index()
    table.columns = ["Month", "Revenue"]
    return table


def last_month_is_partial(sales):
    """True when the newest sale is not at the end of its month."""
    newest = sales["InvoiceDate"].max()
    return newest.normalize() < (newest + pd.offsets.MonthEnd(0)).normalize()


def top_products(sales, limit=10):
    table = (
        sales.groupby("Description", observed=True)
        .agg(Revenue=("Revenue", "sum"), Units=("Quantity", "sum"))
        .sort_values("Revenue", ascending=False).head(limit).reset_index()
    )
    table["Description"] = table["Description"].astype(str)
    return table


def revenue_by_country(sales, limit=10):
    table = (
        sales.groupby("Country", observed=True)
        .agg(Revenue=("Revenue", "sum"), Orders=("InvoiceNo", "nunique"))
        .sort_values("Revenue", ascending=False).head(limit).reset_index()
    )
    table["Country"] = table["Country"].astype(str)
    return table


def customer_activity(sales):
    """One row per registered customer. Guest rows have no ID, so they are left out."""
    table = (
        sales[sales["HasCustomerID"]].groupby("CustomerID")
        .agg(Orders=("InvoiceNo", "nunique"), Revenue=("Revenue", "sum"))
        .reset_index()
    )
    table["CustomerID"] = table["CustomerID"].astype(str)
    return table
