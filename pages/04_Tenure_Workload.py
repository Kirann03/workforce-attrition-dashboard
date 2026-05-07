import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(page_title="Tenure & Workload Analysis", layout="wide")
apply_theme()
render_sidebar()
page_header(
    "Workload & Mobility Impact",
    "Tenure & Workload Analysis",
    "Assess early-career exits, tenure concentration, overtime exposure, business travel, promotion stagnation, and distance-from-home effects.",
    ["Tenure range", "Overtime", "Business travel", "Promotion stagnation"],
)

df = load_data()

st.sidebar.header("Filters")
overtime_options = ["Yes", "No"]
travel_options = df["BusinessTravel"].dropna().unique().tolist()
ot_toggle = st.sidebar.multiselect("OverTime", overtime_options, default=overtime_options)
travel_toggle = st.sidebar.multiselect("Business Travel", travel_options, default=travel_options)
tenure_range = st.sidebar.slider(
    "Years at Company",
    min_value=int(df["YearsAtCompany"].min()),
    max_value=int(df["YearsAtCompany"].max()),
    value=(int(df["YearsAtCompany"].min()), int(df["YearsAtCompany"].max())),
)
df_f = df[
    df["OverTime"].isin(ot_toggle)
    & df["BusinessTravel"].isin(travel_toggle)
    & df["YearsAtCompany"].between(tenure_range[0], tenure_range[1])
]

if df_f.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

ot_rate = df[df["OverTime"] == "Yes"]["Attrition"].mean() * 100
non_ot_rate = df[df["OverTime"] == "No"]["Attrition"].mean() * 100
early_rate = df[df["YearsAtCompany"] <= 1]["Attrition"].mean() * 100

k1, k2, k3 = st.columns(3)
k1.metric("Overtime Attrition Rate", f"{ot_rate:.1f}%")
k2.metric("Non-Overtime Attrition Rate", f"{non_ot_rate:.1f}%")
k3.metric("Early Tenure (<1yr) Attrition", f"{early_rate:.1f}%")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    st.subheader("Attrition by Tenure Bucket")
    tb = attrition_rate(df_f, "TenureBucket")
    fig = px.bar(tb, x="TenureBucket", y="Rate", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Attrition by Career Stage")
    cs = attrition_rate(df_f, "CareerStage")
    fig = px.bar(cs, x="CareerStage", y="Rate", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.subheader("Overtime vs Attrition")
    ot_df = attrition_rate(df, "OverTime")
    fig = px.bar(ot_df, x="OverTime", y="Rate", color="OverTime", text="Rate", color_discrete_map={"Yes": "#EF553B", "No": "#00CC96"})
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Business Travel vs Attrition")
    bt_df = attrition_rate(df, "BusinessTravel")
    fig = px.bar(bt_df, x="BusinessTravel", y="Rate", color="Rate", color_continuous_scale="Oranges", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Promotion Stagnation vs Attrition")
fig = px.box(
    df,
    x="Attrition_Label",
    y="YearsSinceLastPromotion",
    color="Attrition_Label",
    color_discrete_map=STATUS_COLORS,
    points="all",
    notched=True,
)
polish(fig, 380)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Distance from Home vs Attrition")
dist_bins = df.copy()
dist_bins["DistBand"] = pd.cut(
    df["DistanceFromHome"],
    bins=[0, 5, 15, 30, 100],
    labels=["<5km", "5-15km", "15-30km", "30+km"],
    include_lowest=True,
)
db = attrition_rate(dist_bins, "DistBand")
fig = px.line(db, x="DistBand", y="Rate", markers=True, text="Rate", color_discrete_sequence=["#AB63FA"])
fig.update_traces(textposition="top center", texttemplate="%{text}%")
polish(fig, 340)
st.plotly_chart(fig, use_container_width=True)
