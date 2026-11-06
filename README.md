# Online Retail Dashboard

CodeNova Data Science Internship, Batch 01, Task 3.

An interactive sales dashboard built on the cleaned UCI Online Retail data from my Task 2 project. Anyone can filter the data and see the numbers and charts update straight away.

**Live demo:** ADD YOUR STREAMLIT LINK HERE

## Features

- Filters: date range slider, country dropdown, customer type dropdown, minimum order value, and an option to hide outliers
- KPI cards: revenue, orders, average order value, units sold, registered customers
- Interactive charts: monthly revenue line, top products and top countries bars, customer scatter plot
- A friendly "No matching records" message when the filters match nothing
- Layout that stacks on smaller screens

## Tech stack

Python, Streamlit, Plotly, Pandas. All free.

## Setup and run

1. Run the Task 2 project to create `online_retail_clean.csv`.
2. From this folder, run:

```bash
pip install -r requirements.txt
python prepare_data.py --input path/to/online_retail_clean.csv
streamlit run app.py
```

## Tests

```bash
python tests/test_dashboard_logic.py
```

The tests check the KPI formulas, every filter, the zero-result case, and that chart totals add up to the revenue total.

## Deploy for free

1. Push this folder to a public GitHub repository, including `data/sales.csv.gz`.
2. Sign in at [Streamlit Community Cloud](https://share.streamlit.io) with GitHub.
3. Create an app, choose this repository, and set the main file to `app.py`.
4. Copy the app link to the top of this README.

## Project structure

```text
app.py                  the dashboard screens
dashboard_logic.py      filters and calculations
prepare_data.py         makes data/sales.csv.gz from the Task 2 output
data/sales.csv.gz       the dashboard data
tests/                  logic tests
.streamlit/config.toml  theme settings
requirements.txt        packages needed for deployment
```

## Screenshots

ADD YOUR SCREENSHOTS HERE

## Dataset credit

Chen, D. (2015). Online Retail. UCI Machine Learning Repository. Licensed under CC BY 4.0.
