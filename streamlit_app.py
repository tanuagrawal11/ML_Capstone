# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------
# Page config
# ------------------------
st.set_page_config(page_title="Retail Insights Dashboard", layout="wide")
st.title("Retail Store & Customer Insights Dashboard")

# ------------------------
# Load data
# ------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Data/processed_sales_data.csv", parse_dates=["invoice_date"])
    rfm = pd.read_csv("Data/rfm_customer_segments.csv")
    # Ensure revenue exists
    if "revenue" not in df.columns:
        df["revenue"] = df.get("quantity", 0) * df.get("price", 0)
    return df, rfm

df, rfm = load_data()

# ------------------------
# Sidebar filters
# ------------------------
st.sidebar.header("Filters")
malls = ["All"] + sorted(df["shopping_mall"].dropna().unique().tolist())
selected_mall = st.sidebar.selectbox("Select Shopping Mall", malls)

if selected_mall != "All":
    filtered = df[df["shopping_mall"] == selected_mall].copy()
else:
    filtered = df.copy()

# ------------------------
# KPIs
# ------------------------
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"{filtered['revenue'].sum():,.2f}")
col2.metric("Total Orders", f"{filtered['invoice_no'].nunique():,}")
col3.metric("Unique Customers", f"{filtered['customer_id'].nunique():,}")

# ------------------------
# 1. Store / Region Performance
# ------------------------
st.subheader("Store Performance by Mall")
store_perf = filtered.groupby("shopping_mall")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
fig_store = px.bar(store_perf, x="shopping_mall", y="revenue", title="Revenue by Store")
st.plotly_chart(fig_store, use_container_width=True)

# ------------------------
# 2. Seasonal Trend Analysis
# ------------------------
st.subheader("Monthly Revenue Trend")
monthly = filtered.groupby(filtered["invoice_date"].dt.to_period("M"))["revenue"].sum().reset_index()
monthly["invoice_date"] = monthly["invoice_date"].astype(str)
fig_month = px.line(monthly, x="invoice_date", y="revenue", title="Monthly Revenue Trend")
st.plotly_chart(fig_month, use_container_width=True)

# ------------------------
# 3. Payment Method Insights
# ------------------------
st.subheader("Payment Method Distribution")
pm = filtered["payment_method"].value_counts().reset_index()
pm.columns = ["Payment Method", "Count"]
fig_pm = px.pie(pm, names="Payment Method", values="Count", title="Payment Methods")
st.plotly_chart(fig_pm, use_container_width=True)

# ------------------------
# 4. RFM Segmentation
# ------------------------
st.subheader("Customer Segmentation (RFM)")
if "Segment" in rfm.columns:
    seg_counts = rfm["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Customers"]
    fig_rfm = px.bar(seg_counts, x="Segment", y="Customers", title="RFM Segments")
    st.plotly_chart(fig_rfm, use_container_width=True)
else:
    st.dataframe(rfm.head())

# ------------------------
# 5. Top Customers
# ------------------------
st.subheader("Top 10 Customers by Revenue")
top_cust = filtered.groupby("customer_id")["revenue"].sum().reset_index().sort_values("revenue", ascending=False).head(10)
fig_topcust = px.bar(top_cust, x="customer_id", y="revenue", title="Top 10 Customers")
st.plotly_chart(fig_topcust, use_container_width=True)

# ------------------------
# 6. Category-wise Insights
# ------------------------
st.subheader("Top 10 Categories by Revenue")
cat = filtered.groupby("category")["revenue"].sum().reset_index().sort_values("revenue", ascending=False).head(10)
fig_cat = px.bar(cat, x="category", y="revenue", title="Top Categories by Revenue")
st.plotly_chart(fig_cat, use_container_width=True)

# ------------------------
# 7. Repeat vs One-time Customers
# ------------------------
st.subheader("Repeat vs One-time Customers")
freq = filtered.groupby("customer_id")["invoice_no"].nunique().reset_index()
repeat = int((freq["invoice_no"] > 1).sum())
one_time = int((freq["invoice_no"] == 1).sum())
st.write(f"Repeat customers: {repeat} | One-time customers: {one_time}")

# ------------------------
# 8. Campaign Simulation
# ------------------------
st.subheader("Campaign Simulation: Discount Impact on Top Customers")
discount = st.slider("Discount rate", 0.0, 0.5, 0.10, 0.01)
top_pct = st.slider("Target top % customers", 1, 50, 10)
total_spend = filtered.groupby("customer_id")["revenue"].sum()
threshold = total_spend.quantile(1 - top_pct/100)
targets = total_spend[total_spend >= threshold].index
revenue_before = float(filtered[filtered["customer_id"].isin(targets)]["revenue"].sum())
revenue_after = revenue_before * (1 - discount)
st.write({
    "target_pct": top_pct,
    "discount_rate": discount,
    "revenue_before": revenue_before,
    "revenue_after": revenue_after,
    "estimated_loss": revenue_before - revenue_after
})

# ------------------------
# 9. Sample Data
# ------------------------
st.subheader("Sample Processed Sales Data")
st.dataframe(filtered.head(10))
