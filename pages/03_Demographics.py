import plotly.express as px
import streamlit as st

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate, chi_square_test
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, page_header, render_sidebar


st.set_page_config(page_title="Demographic Analysis", page_icon="📊", layout="wide")
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

st.sidebar.header("Workforce Filters")
genders = sorted(df["Gender"].dropna().unique().tolist())
departments = sorted(df["Department"].dropna().unique().tolist())
gender_filter = st.sidebar.multiselect("Gender", genders, default=genders)
dept_filter = st.sidebar.multiselect("Department", departments, default=departments)
roles = sorted(df[df["Department"].isin(dept_filter)]["JobRole"].dropna().unique().tolist())
role_filter = st.sidebar.multiselect("Job Role", roles, default=roles)
tenure_range = st.sidebar.slider(
    "Years at Company",
    int(df["YearsAtCompany"].min()),
    int(df["YearsAtCompany"].max()),
    (int(df["YearsAtCompany"].min()), int(df["YearsAtCompany"].max())),
)
df_f = df[
    df["Gender"].isin(gender_filter)
    & df["Department"].isin(dept_filter)
    & df["JobRole"].isin(role_filter)
    & df["YearsAtCompany"].between(tenure_range[0], tenure_range[1])
]
st.sidebar.metric("Filtered Records", len(df_f))

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
    fig = px.bar(ag, x="AgeGroup", y="Rate", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    sig_caption("AgeGroup")
    chart_caption(len(df_f))

with c2:
    st.subheader("Attrition by Gender")
    gg = attrition_rate(df_f, "Gender")
    fig = px.bar(gg, x="Gender", y="Rate", color="Gender", color_discrete_sequence=["#335C81", "#D83A22"], text="Rate")
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
    fig = px.bar(ms, x="MaritalStatus", y="Rate", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    sig_caption("MaritalStatus")
    chart_caption(len(df_f))

with c4:
    st.subheader("Attrition by Education Level")
    edu = attrition_rate(df_f, "EducationLabel")
    fig = px.bar(edu, x="EducationLabel", y="Rate", color="Rate", color_continuous_scale="Blues_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    sig_caption("EducationLabel")
    chart_caption(len(df_f))

st.markdown("---")
st.subheader("Attrition by Education Field")
ef = attrition_rate(df_f, "EducationField").sort_values("Rate", ascending=True)
fig = px.bar(ef, y="EducationField", x="Rate", orientation="h", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
fig.update_traces(texttemplate="%{text}%", textposition="outside")
polish(fig, 380)
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)
sig_caption("EducationField")
chart_caption(len(df_f))

st.markdown("---")
st.subheader("Intersectional Risk Matrix")
matrix = df_f.groupby(["JobRole", "MaritalStatus"], observed=False).agg(Total=("Attrition", "count"), Left=("Attrition", "sum")).reset_index()
matrix["Rate"] = (matrix["Left"] / matrix["Total"] * 100).fillna(0).round(1)
pivot = matrix.pivot(index="JobRole", columns="MaritalStatus", values="Rate").fillna(0)
fig = px.imshow(pivot, color_continuous_scale="RdYlGn_r", text_auto=True, aspect="auto", labels=dict(color="Attrition %"))
polish(fig, 460)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df_f))

st.subheader("Job Level x Age Group Bubble Chart")
bubble = df_f.groupby(["JobLevelLabel", "AgeGroup"], observed=False).agg(Total=("Attrition", "count"), Left=("Attrition", "sum")).reset_index()
bubble["Rate"] = (bubble["Left"] / bubble["Total"] * 100).fillna(0).round(1)
fig = px.scatter(bubble, x="AgeGroup", y="JobLevelLabel", size="Left", color="Rate", color_continuous_scale="RdYlGn_r", hover_data=["Total", "Left"], labels={"Rate": "Attrition %"})
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
