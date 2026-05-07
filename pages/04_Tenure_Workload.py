import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import RATE_SCALE, STATUS_COLORS, polish, waterfall
from utils.config import PROMOTION_STAGNATION_BINS, PROMOTION_STAGNATION_LABELS
from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_with_ci
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, insight_card, page_header, render_sidebar, section_divider


st.set_page_config(page_title="Tenure & Workload Analysis", page_icon="⏱️", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)

page_header(
    "Workload & Mobility Impact",
    "Tenure & Workload Analysis",
    "Assess early-career exits, tenure concentration, overtime exposure, business travel, promotion stagnation, and distance-from-home confidence intervals.",
    ["Tenure range", "Overtime", "Business travel", "Promotion stagnation"],
)

st.sidebar.header("Workforce Filters")
departments = sorted(df["Department"].dropna().unique().tolist())
selected_depts = st.sidebar.multiselect("Department", departments, default=departments)
roles = sorted(df[df["Department"].isin(selected_depts)]["JobRole"].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect("Job Role", roles, default=roles)
overtime_options = ["Yes", "No"]
travel_options = sorted(df["BusinessTravel"].dropna().unique().tolist())
ot_toggle = st.sidebar.multiselect("OverTime", overtime_options, default=overtime_options)
travel_toggle = st.sidebar.multiselect("Business Travel", travel_options, default=travel_options)
tenure_range = st.sidebar.slider(
    "Years at Company",
    min_value=int(df["YearsAtCompany"].min()),
    max_value=int(df["YearsAtCompany"].max()),
    value=(int(df["YearsAtCompany"].min()), int(df["YearsAtCompany"].max())),
)
df_f = df[
    df["Department"].isin(selected_depts)
    & df["JobRole"].isin(selected_roles)
    & df["OverTime"].isin(ot_toggle)
    & df["BusinessTravel"].isin(travel_toggle)
    & df["YearsAtCompany"].between(tenure_range[0], tenure_range[1])
]
st.sidebar.metric("Filtered Records", len(df_f))

if df_f.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

ot_rate = df_f[df_f["OverTime"] == "Yes"]["Attrition"].mean() * 100 if (df_f["OverTime"] == "Yes").any() else 0
non_ot_rate = df_f[df_f["OverTime"] == "No"]["Attrition"].mean() * 100 if (df_f["OverTime"] == "No").any() else 0
early_rate = df_f[df_f["YearsAtCompany"] <= 1]["Attrition"].mean() * 100 if (df_f["YearsAtCompany"] <= 1).any() else 0

k1, k2, k3 = st.columns([1, 1, 1])
k1.metric("Overtime Attrition Rate", f"{ot_rate:.1f}%")
k2.metric("Non-Overtime Attrition Rate", f"{non_ot_rate:.1f}%")
k3.metric("Early Tenure Attrition", f"{early_rate:.1f}%")

c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("Attrition by Tenure Bucket")
    tb = attrition_rate(df_f, "TenureBucket")
    fig = px.bar(tb, x="TenureBucket", y="Rate", color="Rate", color_continuous_scale=RATE_SCALE, text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_f))

with c2:
    st.subheader("Workload Stress Cohort")
    stress_df = df_f.assign(StressCohort=df_f["WorkloadStress"].map({1: "Overtime + Frequent Travel", 0: "All Other Employees"}))
    stress_status = stress_df.groupby(["StressCohort", "Attrition_Label"], observed=False).size().reset_index(name="Count")
    fig = px.bar(stress_status, x="StressCohort", y="Count", color="Attrition_Label", barmode="group", color_discrete_map=STATUS_COLORS)
    polish(fig, 360)
    fig.update_layout(legend_title="Status", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_f))

c3, c4 = st.columns([1, 1])
with c3:
    st.subheader("Overtime vs Attrition")
    ot_df = attrition_rate(df_f, "OverTime")
    fig = px.bar(ot_df, x="OverTime", y="Rate", color="OverTime", text="Rate", color_discrete_map={"Yes": STATUS_COLORS["Left"], "No": STATUS_COLORS["Stayed"]})
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_f))

with c4:
    st.subheader("Business Travel vs Attrition")
    bt_df = attrition_rate(df_f, "BusinessTravel")
    fig = px.bar(bt_df, x="BusinessTravel", y="Rate", color="Rate", color_continuous_scale=RATE_SCALE, text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df_f))

section_divider("Stagnation Risk")
st.subheader("Stagnation x Tenure Heatmap")
stagnation = df_f.copy()
stagnation["PromotionBand"] = pd.cut(
    stagnation["YearsSinceLastPromotion"],
    bins=PROMOTION_STAGNATION_BINS,
    labels=PROMOTION_STAGNATION_LABELS,
)
heat = stagnation.groupby(["TenureBucket", "PromotionBand"], observed=False).agg(Total=("Attrition", "count"), Left=("Attrition", "sum")).reset_index()
heat["Rate"] = (heat["Left"] / heat["Total"] * 100).fillna(0).round(1)
pivot = heat.pivot(index="TenureBucket", columns="PromotionBand", values="Rate").fillna(0)
fig = px.imshow(pivot, color_continuous_scale=RATE_SCALE, text_auto=True, aspect="auto", labels=dict(color="Attrition %"))
polish(fig, 420, title="Stagnation x Tenure Heatmap")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))
insight_card("Key Observation", "Promotion stagnation is most actionable where high attrition overlaps with longer tenure buckets.")

section_divider("Workload Lift")
st.subheader("Attrition Lift Waterfall")
stress_rate = stress_df[stress_df["WorkloadStress"] == 1]["Attrition"].mean() * 100 if (stress_df["WorkloadStress"] == 1).any() else 0
rest_rate = stress_df[stress_df["WorkloadStress"] == 0]["Attrition"].mean() * 100 if (stress_df["WorkloadStress"] == 0).any() else 0
fig = waterfall(
    ["Baseline", "Overtime Lift", "Stress Cohort Lift"],
    [df_f["Attrition"].mean() * 100, ot_rate - non_ot_rate, stress_rate - rest_rate],
    title="Workload-Related Attrition Lift",
)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))

st.subheader("Distance from Home vs Attrition with Confidence Intervals")
db = attrition_with_ci(df_f, "DistanceBand")
fig = px.bar(db, x="DistanceBand", y="Rate", error_y=db["CI_Upper"] - db["Rate"], error_y_minus=db["Rate"] - db["CI_Lower"], color="Rate", color_continuous_scale=RATE_SCALE, text="Rate")
fig.update_traces(texttemplate="%{text}%", textposition="outside")
polish(fig, 380, title="Distance from Home vs Attrition with Confidence Intervals")
fig.update_layout(coloraxis_showscale=False, yaxis_title="Attrition Rate (%)")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))

st.subheader("Promotion Stagnation vs Attrition")
fig = px.box(df_f, x="Attrition_Label", y="YearsSinceLastPromotion", color="Attrition_Label", color_discrete_map=STATUS_COLORS, points="all", notched=True)
polish(fig, 380, title="Promotion Stagnation vs Attrition")
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))

with st.expander("Analytical Findings"):
    top_tenure = attrition_rate(df_f, "TenureBucket").sort_values("Rate", ascending=False).iloc[0]
    top_travel = attrition_rate(df_f, "BusinessTravel").sort_values("Rate", ascending=False).iloc[0]
    stress_rate = stress_df[stress_df["WorkloadStress"] == 1]["Attrition"].mean() * 100 if (stress_df["WorkloadStress"] == 1).any() else 0
    rest_rate = stress_df[stress_df["WorkloadStress"] == 0]["Attrition"].mean() * 100 if (stress_df["WorkloadStress"] == 0).any() else 0
    st.markdown(
        f"""
        - Highest tenure-bucket attrition: **{top_tenure['TenureBucket']}** at **{top_tenure['Rate']:.1f}%**.
        - Overtime lift: **{ot_rate - non_ot_rate:.1f} percentage points** versus non-overtime employees.
        - Workload stress cohort attrition lift: **{stress_rate - rest_rate:.1f} percentage points** versus all others.
        - Highest travel-risk category: **{top_travel['BusinessTravel']}** at **{top_travel['Rate']:.1f}%**.
        - Promotion stagnation is most actionable where high attrition overlaps with 3+ years since last promotion.
        """
    )

download_filtered_data(df_f, "tenure_workload_filtered_data.csv")
