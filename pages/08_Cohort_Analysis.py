import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import RATE_SCALE, polish
from utils.data_loader import load_data
from utils.kpis import chi_square_test, cramers_v
from utils.theme import apply_theme, breadcrumb, chart_caption, download_filtered_data, page_header, render_global_filters, render_sidebar


st.set_page_config(page_title="Cohort Analysis", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df_all = load_data()
df = render_global_filters(df_all)

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

COHORT_OPTIONS = {
    "Department": "Department",
    "JobRole": "Job Role",
    "AgeGroup": "Age Group",
    "Gender": "Gender",
    "MaritalStatus": "Marital Status",
    "EducationLabel": "Education Level",
    "EducationField": "Education Field",
    "TenureBucket": "Tenure Band",
    "CareerStage": "Career Stage",
    "OverTime": "Overtime",
    "BusinessTravel": "Business Travel",
    "JobLevelLabel": "Job Level",
    "ManagerTenureBand": "Manager Tenure",
}

breadcrumb("Cohort Analysis")
page_header(
    "Cohort Intelligence",
    "Custom Cohort Attrition Matrix",
    "Select any two workforce dimensions to reveal attrition at their intersection and identify high-risk cohort combinations.",
    ["Custom cohorts", "Chi-square validation", "Top 5 risk pairs"],
)

col_a, col_b = st.columns([1, 1])
with col_a:
    dim1 = st.selectbox("Primary Dimension", list(COHORT_OPTIONS.keys()), format_func=lambda key: COHORT_OPTIONS[key], index=0)
with col_b:
    dim2_options = [key for key in COHORT_OPTIONS if key != dim1]
    dim2 = st.selectbox("Secondary Dimension", dim2_options, format_func=lambda key: COHORT_OPTIONS[key], index=0)

cohort = df.groupby([dim1, dim2], observed=False).agg(Total=("Attrition", "count"), Left=("Attrition", "sum")).reset_index()
cohort["Rate"] = (cohort["Left"] / cohort["Total"] * 100).fillna(0).round(1)

pivot = cohort.pivot(index=dim1, columns=dim2, values="Rate").fillna(0)
fig = px.imshow(
    pivot,
    color_continuous_scale=RATE_SCALE,
    text_auto=True,
    aspect="auto",
    labels={"color": "Attrition %", "x": COHORT_OPTIONS[dim2], "y": COHORT_OPTIONS[dim1]},
)
polish(fig, 500, title=f"Attrition Rate: {COHORT_OPTIONS[dim1]} x {COHORT_OPTIONS[dim2]}")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df))

st.subheader("Top 5 Highest-Risk Cohort Pairs")
top5 = cohort[cohort["Total"] >= 10].sort_values("Rate", ascending=False).head(5).copy()
top5 = top5.rename(columns={dim1: COHORT_OPTIONS[dim1], dim2: COHORT_OPTIONS[dim2], "Rate": "Attrition %"})
st.dataframe(top5.reset_index(drop=True), use_container_width=True, hide_index=True)

test = chi_square_test(df, dim1)
sig = "Statistically significant" if test["significant"] else "Not statistically significant"
st.info(f"Association between **{COHORT_OPTIONS[dim1]}** and attrition: {sig} (p = {test['p_value']:.4f})")
v = cramers_v(df, dim1, "Attrition")
st.metric("Effect Size (Cramer's V)", f"{v:.3f}", help="0.1=small, 0.3=medium, 0.5=large")

tab_export, tab_tenure = st.tabs(["Cohort Export", "Tenure Cohort Trends"])
with tab_export:
    st.download_button("Export Cohort Pivot CSV", pivot.to_csv().encode("utf-8"), "cohort_pivot.csv", "text/csv")
with tab_tenure:
    trend = df.groupby(["TenureBucket", "CareerStage"], observed=False).agg(Total=("Attrition", "count"), Left=("Attrition", "sum")).reset_index()
    trend["Rate"] = (trend["Left"] / trend["Total"] * 100).fillna(0).round(1)
    fig = px.bar(trend, x="TenureBucket", y="Rate", color="CareerStage", barmode="group", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 420, title="Tenure Bucket x Career Stage Attrition")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

download_filtered_data(cohort, "cohort_analysis.csv")
