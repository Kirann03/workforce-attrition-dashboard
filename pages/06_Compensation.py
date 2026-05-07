import plotly.express as px
import streamlit as st

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, page_header, render_sidebar


st.set_page_config(page_title="Compensation Analysis", page_icon="📊", layout="wide")
apply_theme()
render_sidebar()

df_all = load_data()
data_quality_banner(df_all)

st.sidebar.header("Workforce Filters")
departments = sorted(df_all["Department"].dropna().unique().tolist())
selected_depts = st.sidebar.multiselect("Department", departments, default=departments)
roles = sorted(df_all[df_all["Department"].isin(selected_depts)]["JobRole"].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect("Job Role", roles, default=roles)
job_levels = sorted(df_all["JobLevelLabel"].dropna().unique().tolist())
selected_levels = st.sidebar.multiselect("Job Level", job_levels, default=job_levels)
df = df_all[
    df_all["Department"].isin(selected_depts)
    & df_all["JobRole"].isin(selected_roles)
    & df_all["JobLevelLabel"].isin(selected_levels)
]
st.sidebar.metric("Filtered Records", len(df))

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

page_header(
    "Rewards & Retention",
    "Compensation & Attrition Analysis",
    "Evaluate income bands, stock-option gaps, internal equity, salary hikes, and performance-linked compensation patterns associated with attrition.",
    ["Income equity", "Salary hike", "Stock options", "Performance"],
)

baseline = df["Attrition"].mean() * 100
stock_zero = df[df["StockOptionLevel"] == 0]["Attrition"].mean() * 100
stock_any = df[df["StockOptionLevel"] > 0]["Attrition"].mean() * 100
lift = stock_zero - stock_any
income_rates = attrition_rate(df, "IncomeBand").sort_values("Rate", ascending=False)
top_income = income_rates.iloc[0]

k1, k2, k3 = st.columns([1, 1, 1])
k1.metric("No Stock Option Attrition", f"{stock_zero:.1f}%")
k2.metric("Stock Option Attrition", f"{stock_any:.1f}%")
k3.metric("Stock Option Gap", f"{lift:.1f} pts", delta="Level 0 vs >0", delta_color="inverse")

st.warning(
    f"Employees in the {top_income['IncomeBand']} income band show {top_income['Rate']:.1f}% attrition, "
    f"{top_income['Rate'] - baseline:.1f} percentage points above the company baseline. Consider a targeted salary band review."
)

c1, c2 = st.columns([1.15, 0.85])
with c1:
    st.subheader("Monthly Income vs Attrition by Job Role")
    fig = px.box(df, x="JobRole", y="MonthlyIncome", color="Attrition_Label", color_discrete_map=STATUS_COLORS, points=False)
    polish(fig, 430)
    fig.update_layout(xaxis_tickangle=-30, legend_title="Status")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

with c2:
    st.subheader("Salary Hike % vs Attrition")
    fig = px.violin(df, x="Attrition_Label", y="PercentSalaryHike", color="Attrition_Label", color_discrete_map=STATUS_COLORS, box=True, points="outliers")
    polish(fig, 430)
    fig.update_layout(showlegend=False, xaxis_title="Status")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

c3, c4 = st.columns([1, 1])
with c3:
    st.subheader("Income Band Attrition Rate")
    ib = attrition_rate(df, "IncomeBand")
    fig = px.bar(ib, x="IncomeBand", y="Rate", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

with c4:
    st.subheader("Stock Options vs Attrition")
    so = attrition_rate(df, "StockOptionLevel")
    so["StockOptionLevel"] = so["StockOptionLevel"].astype(str)
    fig = px.bar(so, x="StockOptionLevel", y="Rate", color="Rate", color_continuous_scale="Blues_r", text="Rate", labels={"StockOptionLevel": "Stock Option Level"})
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

st.markdown("---")
st.subheader("Income Equity by Tenure, Level, and Department")
equity_df = df.copy()
equity_df["JobLevel"] = equity_df["JobLevel"].astype(str)
fig = px.scatter(
    equity_df,
    x="YearsAtCompany",
    y="MonthlyIncome",
    color="JobLevel",
    facet_col="Department",
    hover_data=["JobRole", "Attrition_Label"],
    labels={"JobLevel": "Job Level"},
    opacity=0.7,
)
polish(fig, 470)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df))

st.subheader("Salary Hike vs Performance Rating")
perf_df = df.copy()
perf_df["PerformanceRating"] = perf_df["PerformanceRating"].astype(str)
fig = px.box(
    perf_df,
    x="PerformanceRating",
    y="PercentSalaryHike",
    color="Attrition_Label",
    color_discrete_map=STATUS_COLORS,
    points="outliers",
    labels={"PerformanceRating": "Performance Rating"},
)
polish(fig, 420)
fig.update_layout(legend_title="Status")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df))

st.subheader("Income vs Years of Experience")
fig = px.scatter(df, x="TotalWorkingYears", y="MonthlyIncome", color="Attrition_Label", size="YearsAtCompany", hover_data=["JobRole", "Department"], color_discrete_map=STATUS_COLORS, opacity=0.65)
polish(fig, 450)
fig.update_layout(legend_title="Status")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df))

download_filtered_data(df, "compensation_data.csv")
