import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(page_title="Demographic Analysis", layout="wide")
apply_theme()
render_sidebar()
page_header(
    "People Segmentation",
    "Demographic Attrition Explorer",
    "Compare attrition patterns across age, gender, marital status, education, and education fields with department-level filtering.",
    ["Age groups", "Education field", "Department filter"],
)

df = load_data()

st.sidebar.header("Filters")
genders = df["Gender"].dropna().unique().tolist()
departments = df["Department"].dropna().unique().tolist()
gender_filter = st.sidebar.multiselect("Gender", genders, default=genders)
dept_filter = st.sidebar.multiselect("Department", departments, default=departments)
df_f = df[df["Gender"].isin(gender_filter) & df["Department"].isin(dept_filter)]

if df_f.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

c1, c2 = st.columns(2)
with c1:
    st.subheader("Attrition by Age Group")
    ag = attrition_rate(df_f, "AgeGroup")
    fig = px.bar(ag, x="AgeGroup", y="Rate", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Attrition by Gender")
    gg = attrition_rate(df_f, "Gender")
    fig = px.bar(gg, x="Gender", y="Rate", color="Gender", color_discrete_sequence=["#636EFA", "#EF553B"], text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.subheader("Attrition by Marital Status")
    ms = attrition_rate(df_f, "MaritalStatus")
    fig = px.pie(ms, names="MaritalStatus", values="Rate", hole=0.4)
    fig.update_traces(textinfo="percent+label")
    polish(fig, 360)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Attrition by Education Level")
    edu = attrition_rate(df_f, "EducationLabel")
    fig = px.bar(edu, x="EducationLabel", y="Rate", color="Rate", color_continuous_scale="Blues_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Attrition by Education Field")
ef = attrition_rate(df_f, "EducationField").sort_values("Rate", ascending=True)
fig = px.bar(
    ef,
    y="EducationField",
    x="Rate",
    orientation="h",
    color="Rate",
    color_continuous_scale="RdYlGn_r",
    text="Rate",
)
fig.update_traces(texttemplate="%{text}%", textposition="outside")
polish(fig, 380)
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Age Distribution by Department and Attrition")
fig = px.violin(
    df_f,
    x="Department",
    y="Age",
    color="Attrition_Label",
    box=True,
    points="outliers",
    color_discrete_map=STATUS_COLORS,
)
polish(fig, 400)
fig.update_layout(legend_title="Status")
st.plotly_chart(fig, use_container_width=True)
