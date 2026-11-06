"""
CodeNova Internship - Task 3: Interactive Analytics Dashboard
Run with:  streamlit run app.py

How Streamlit works: each time a filter changes, this file runs again from top
to bottom with the new filter values. That is why the charts update by themselves.
"""

from pathlib import Path

import plotly.express as px
import streamlit as st

import dashboard_logic as logic

DATA_PATH = Path(__file__).parent / "data" / "sales.csv.gz"
BLUE = "#2a78d6"
CHART_CONFIG = {"displayModeBar": False}

st.set_page_config(page_title="Online Retail Dashboard", layout="wide")


@st.cache_resource(show_spinner="Loading sales data...")
def get_sales(path):
    """Load the file once and reuse it, so changing a filter stays fast.
    The filter functions never change this table, so it is safe to share."""
    return logic.load_sales(path)


def short_label(text, limit=30):
    return text if len(text) <= limit else text[: limit - 1] + "…"


def tidy(figure, height=340):
    figure.update_layout(height=height, margin=dict(l=8, r=16, t=8, b=8), showlegend=False)
    return figure


def show_chart(figure):
    st.plotly_chart(figure, use_container_width=True, config=CHART_CONFIG)


# data
if not DATA_PATH.exists():
    st.title("Online Retail Dashboard")
    st.error(
        "The data file is missing. Run `python prepare_data.py --input "
        "path/to/online_retail_clean.csv` first, then reload this page."
    )
    st.stop()

sales = get_sales(DATA_PATH)
first_day = sales["InvoiceDate"].min().date()
last_day = sales["InvoiceDate"].max().date()

#  filters
st.sidebar.header("Filters")

if first_day < last_day:
    start_date, end_date = st.sidebar.slider(
        "Date range", min_value=first_day, max_value=last_day,
        value=(first_day, last_day), format="DD MMM YYYY",
    )
else:
    start_date, end_date = first_day, last_day

countries = st.sidebar.multiselect(
    "Country", options=sorted(sales["Country"].cat.categories), placeholder="All countries",
)
customer_type = st.sidebar.selectbox(
    "Customer type", options=[logic.ALL_CUSTOMERS, logic.REGISTERED, logic.GUESTS],
)
min_order_value = st.sidebar.number_input(
    "Minimum order value (£)", min_value=0.0, value=0.0, step=50.0,
    help="Keeps only invoices whose total is at least this amount.",
)
include_outliers = st.sidebar.checkbox(
    "Include unusually large values", value=True,
    help="Outliers were marked with the IQR rule in the Task 2 data cleaning project.",
)

filtered = logic.filter_sales(
    sales, start_date, end_date, countries, customer_type, min_order_value, include_outliers,
)

# 
page
st.title("Online Retail Dashboard")
st.caption(f"Showing {len(filtered):,} of {len(sales):,} sales rows. Values are in pounds sterling.")

if filtered.empty:
    st.info("No matching records. Try a wider date range, another country, or a lower order value.")
    st.stop()

kpis = logic.compute_kpis(filtered)
cards = st.columns(5)
values = [
    ("Revenue", f"£{kpis['revenue']:,.0f}"),
    ("Orders", f"{kpis['orders']:,}"),
    ("Average order value", f"£{kpis['average_order_value']:,.2f}"),
    ("Units sold", f"{kpis['units']:,}"),
    ("Registered customers", f"{kpis['customers']:,}"),
]
for card, (label, value) in zip(cards, values):
    with card.container(border=True):
        st.metric(label, value)

# Line chart: how sales change over time
st.subheader("Monthly revenue")
monthly = logic.monthly_revenue(filtered)
line = px.line(monthly, x="Month", y="Revenue", markers=True, color_discrete_sequence=[BLUE])
line.update_traces(line_width=2, marker_size=8, hovertemplate="%{x|%b %Y}<br>£%{y:,.0f}<extra></extra>")
line.update_xaxes(title=None, tickformat="%b %Y")
line.update_yaxes(title="Revenue (£)", rangemode="tozero")
show_chart(tidy(line))
if logic.last_month_is_partial(sales):
    st.caption(f"The data ends on {last_day:%d %b %Y}, so the last month is not a full month.")

left, right = st.columns(2)

# Bar chart: best-selling products
with left:
    st.subheader("Top 10 products by revenue")
    products = logic.top_products(filtered)
    products["Label"] = products["Description"].map(short_label)
    bars = px.bar(
        products, x="Revenue", y="Label", orientation="h",
        custom_data=["Description", "Units"], color_discrete_sequence=[BLUE],
    )
    bars.update_traces(hovertemplate="%{customdata[0]}<br>£%{x:,.0f}<br>%{customdata[1]:,} units<extra></extra>")
    bars.update_yaxes(title=None, autorange="reversed")
    bars.update_xaxes(title="Revenue (£)")
    show_chart(tidy(bars, 400))

# Bar chart: where sales come from
with right:
    st.subheader("Top 10 countries by revenue")
    country_table = logic.revenue_by_country(filtered)
    country_bars = px.bar(
        country_table, x="Revenue", y="Country", orientation="h",
        custom_data=["Orders"], color_discrete_sequence=[BLUE],
    )
    country_bars.update_traces(hovertemplate="%{y}<br>£%{x:,.0f}<br>%{customdata[0]:,} orders<extra></extra>")
    country_bars.update_yaxes(title=None, autorange="reversed")
    country_bars.update_xaxes(title="Revenue (£)")
    show_chart(tidy(country_bars, 400))

# Scatter plot: do customers who order more often also spend more?
st.subheader("Customer orders and spending")
customers = logic.customer_activity(filtered)
if customers.empty:
    st.info("No matching records for this chart, because guest checkouts have no customer ID.")
else:
    scatter = px.scatter(
        customers, x="Orders", y="Revenue", log_x=True, log_y=True,
        custom_data=["CustomerID"], color_discrete_sequence=[BLUE], opacity=0.55,
    )
    scatter.update_traces(
        marker_size=8,
        hovertemplate="Customer %{customdata[0]}<br>%{x:,} orders<br>£%{y:,.0f}<extra></extra>",
    )
    scatter.update_xaxes(title="Orders (log scale)")
    scatter.update_yaxes(title="Revenue (£, log scale)")
    show_chart(tidy(scatter, 380))
    st.caption("Each dot is one registered customer.")
