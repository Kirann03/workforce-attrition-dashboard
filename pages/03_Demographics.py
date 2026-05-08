import plotly.express as px
import streamlit as st

from utils.charts import CALM_CYAN, DEEP_NAVY, RATE_SCALE, STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate, chi_square_test
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, page_header, render_global_filters, render_sidebar, section_divider


st.set_page_config(page_title="Demographic Analysis", page_icon="👥", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)

page_header(
    "People Segmentation",
    "Demographic Attrition Explorer",
    "Compare demographic patterns individually and intersectionally to reveal whether attrition is concentrated in specific workforce cohorts.",
    ["Age groups", "Education field", "Significance tests", "Intersectional matrix"],
)

df_f = render_global_filters(df)

if df_f.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


def sig_caption(group_col):
    test = chi_square_test(df_f, group_col)
    label = "Significant (p < 0.05)" if test["significant"] else "Not significant"
    st.caption(f"{label} | p = {test['p_value']:.4f}")


c1, c2 = st.columns([1, 1])
with c1:
    st.subheader("Attrition by Age Group")
    ag = attrition_rate(df_f, "AgeGroup")
    fig = px.bar(ag, x="AgeGroup", y="Rate", color="Rate", color_continuous_scale=RATE_SCALE, text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    sig_caption("AgeGroup")
    chart_caption(len(df_f))

with c2:
    st.subheader("Attrition by Gender")
    gg = attrition_rate(df_f, "Gender")
    fig = px.bar(gg, x="Gender", y="Rate", color="Gender", color_discrete_sequence=[DEEP_NAVY, CALM_CYAN], text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    sig_caption("Gender")
    chart_caption(len(df_f))

c3, c4 = st.columns([1, 1])
with c3:
    st.subheader("Attrition by Marital Status")
    ms = attrition_rate(df_f, "MaritalStatus")
    fig = px.bar(ms, x="MaritalStatus", y="Rate", color="Rate", color_continuous_scale=RATE_SCALE, text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    sig_caption("MaritalStatus")
    chart_caption(len(df_f))

with c4:
    st.subheader("Attrition by Education Level")
    edu = attrition_rate(df_f, "EducationLabel")
    fig = px.bar(edu, x="EducationLabel", y="Rate", color="Rate", color_continuous_scale=RATE_SCALE, text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    sig_caption("EducationLabel")
    chart_caption(len(df_f))

section_divider()
st.subheader("Attrition by Education Field")
ef = attrition_rate(df_f, "EducationField").sort_values("Rate", ascending=True)
fig = px.bar(ef, y="EducationField", x="Rate", orientation="h", color="Rate", color_continuous_scale=RATE_SCALE, text="Rate")
fig.update_traces(texttemplate="%{text}%", textposition="outside")
polish(fig, 380)
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)
sig_caption("EducationField")
chart_caption(len(df_f))

section_divider()
st.subheader("Intersectional Risk Matrix")
matrix = df_f.groupby(["JobRole", "MaritalStatus"], observed=False).agg(Total=("Attrition", "count"), Left=("Attrition", "sum")).reset_index()
matrix["Rate"] = (matrix["Left"] / matrix["Total"] * 100).fillna(0).round(1)
pivot = matrix.pivot(index="JobRole", columns="MaritalStatus", values="Rate").fillna(0)
fig = px.imshow(pivot, color_continuous_scale=RATE_SCALE, text_auto=True, aspect="auto", labels=dict(color="Attrition %"))
polish(fig, 460)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))

st.subheader("Job Level x Age Group Bubble Chart")
bubble = df_f.groupby(["JobLevelLabel", "AgeGroup"], observed=False).agg(Total=("Attrition", "count"), Left=("Attrition", "sum")).reset_index()
bubble["Rate"] = (bubble["Left"] / bubble["Total"] * 100).fillna(0).round(1)
fig = px.scatter(bubble, x="AgeGroup", y="JobLevelLabel", size="Left", color="Rate", color_continuous_scale=RATE_SCALE, hover_data=["Total", "Left"], labels={"Rate": "Attrition %"})
polish(fig, 420)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))

st.subheader("Age Distribution by Department and Attrition")
fig = px.violin(df_f, x="Department", y="Age", color="Attrition_Label", box=True, points="outliers", color_discrete_map=STATUS_COLORS)
polish(fig, 400)
fig.update_layout(legend_title="Status")
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))

download_filtered_data(df_f, "demographics_filtered_data.csv")
