import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Supermarket Dashboard", layout="wide")

st.title("📊 Supermarket Sales Dashboard")

# ==================================
# 1️⃣ CONNECT TO GOOGLE SHEETS
# ==================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp"],  # your service account JSON from Streamlit Secrets
    scopes=scope
)

client = gspread.authorize(creds)

sheet_url = "https://docs.google.com/spreadsheets/d/1E-r-5RQSWYt1hKc_7WUlGVtbAGh8AAIisb2sbWBNTpk"
sh = client.open_by_url(sheet_url)
worksheet = sh.sheet1

data = worksheet.get_all_records()
df = pd.DataFrame(data)

# ==================================
# 2️⃣ CLEAN DATA
# ==================================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df.drop_duplicates(inplace=True)

df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df = df.dropna(subset=["order_date"])

df["month"] = df["order_date"].dt.month_name()
df["year"] = df["order_date"].dt.year
df["day"] = df["order_date"].dt.day
df["discount_pct"] = df["discount"] * 100

# ==================================
# 3️⃣ METRICS
# ==================================
total_revenue = df["sales"].sum()
average_sale = df["sales"].mean()

col1, col2 = st.columns(2)
col1.metric("💰 Total Revenue", f"{total_revenue:,.2f}")
col2.metric("📊 Avg Sale per Invoice", f"{average_sale:,.2f}")

# ==================================
# 4️⃣ GROUPED DATA
# ==================================
city_sales = df.groupby("city")["sales"].sum().sort_values(ascending=False)
region_sales = df.groupby("region")["sales"].sum().sort_values(ascending=False)
category_sales = df.groupby("category")["sales"].sum().sort_values(ascending=False)
subcat_sales = df.groupby("sub_category")["sales"].sum().sort_values(ascending=False)
monthly_sales = df.groupby("order_date")["sales"].sum().sort_values()

# ==================================
# 5️⃣ PLOT SUBPLOT DASHBOARD
# ==================================

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Revenue by City", "Revenue by Region",
                    "Monthly Sales Trend", "Revenue by Category")
)

fig.add_trace(go.Bar(x=city_sales.index, y=city_sales.values), row=1, col=1)
fig.add_trace(go.Bar(x=region_sales.index, y=region_sales.values), row=1, col=2)
fig.add_trace(go.Scatter(x=monthly_sales.index, y=monthly_sales.values,
                         mode='lines+markers'), row=2, col=1)
fig.add_trace(go.Bar(x=category_sales.index, y=category_sales.values), row=2, col=2)

fig.update_layout(height=700, width=1200)

st.plotly_chart(fig, use_container_width=True)

# ==================================
# 6️⃣ EXTRA CHARTS
# ==================================

st.subheader("Discount vs Profit by Category")
fig2 = px.scatter(
    df, x="discount_pct", y="profit",
    color="category", size="sales",
    hover_data=["customer_name", "city"]
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Revenue by Sub-Category")
fig3 = px.bar(
    subcat_sales.reset_index(),
    x="sub_category", y="sales",
    title="Revenue by Sub-Category",
    color="sales"
)
st.plotly_chart(fig3, use_container_width=True)
