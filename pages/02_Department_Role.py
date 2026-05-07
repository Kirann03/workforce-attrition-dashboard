import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(page_title="Department & Role Analysis", layout="wide")
apply_theme()
render_sidebar()
page_header(
    "Functional Hotspots",
    "Department & Role Attrition Analysis",
    "Identify functional areas and job roles with concentrated exits so retention actions can be targeted instead of generalized.",
    ["Department selector", "Job role filter", "Heatmap intensity"],
)

df = load_data()

st.sidebar.header("Filters")
departments = df["Department"].dropna().unique().tolist()
selected_depts = st.sidebar.multiselect("Select Departments", options=departments, default=departments)
roles = df[df["Department"].isin(selected_depts)]["JobRole"].dropna().unique().tolist()
selected_roles = st.sidebar.multiselect("Select Job Roles", options=roles, default=roles)
df_filtered = df[df["Department"].isin(selected_depts) & df["JobRole"].isin(selected_roles)]

if df_filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Attrition Count by Department")
    dept_att = df_filtered.groupby(["Department", "Attrition_Label"], observed=False).size().reset_index(name="Count")
    fig = px.bar(
        dept_att,
        x="Department",
        y="Count",
        color="Attrition_Label",
        barmode="group",
        color_discrete_map=STATUS_COLORS,
    )
    polish(fig, 380)
    fig.update_layout(legend_title="Status")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Department Attrition Rate (%)")
    dept_rate = attrition_rate(df_filtered, "Department")
    fig = px.funnel(dept_rate, x="Rate", y="Department", color="Department", text="Rate")
    fig.update_traces(texttemplate="%{text}%")
    polish(fig, 380)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Job Role Attrition Heatmap")
role_dept = df_filtered.groupby(["JobRole", "Department"], observed=False).agg(
    Total=("Attrition", "count"),
    Left=("Attrition", "sum"),
).reset_index()
role_dept["Rate"] = (role_dept["Left"] / role_dept["Total"] * 100).fillna(0).round(1)
pivot = role_dept.pivot(index="JobRole", columns="Department", values="Rate").fillna(0)
fig = px.imshow(
    pivot,
    color_continuous_scale="RdYlGn_r",
    text_auto=True,
    aspect="auto",
    labels=dict(color="Attrition %"),
)
polish(fig, 420)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Attrition Rate by Job Role")
role_rate = attrition_rate(df_filtered, "JobRole").sort_values("Rate", ascending=True)
fig = px.bar(
    role_rate,
    y="JobRole",
    x="Rate",
    orientation="h",
    color="Rate",
    color_continuous_scale="RdYlGn_r",
    text="Rate",
    labels={"Rate": "Attrition Rate (%)"},
)
fig.update_traces(texttemplate="%{text}%", textposition="outside")
polish(fig, 450)
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)
