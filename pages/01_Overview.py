import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_summary
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(page_title="Attrition Overview", layout="wide")
apply_theme()
render_sidebar()
page_header(
    "Organizational Baseline",
    "Attrition Overview Dashboard",
    "Monitor overall workforce turnover, retained-versus-exited distribution, department-level attrition, compensation spread, and satisfaction gaps.",
    ["Attrition rate", "Department baseline", "Satisfaction signals"],
)

df = load_data()
summary = attrition_summary(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Employees", f"{summary['total']:,}")
c2.metric("Employees Left", f"{summary['left']:,}", delta=f"{summary['rate']}% attrition", delta_color="inverse")
c3.metric("Employees Retained", f"{summary['stayed']:,}")
c4.metric("Attrition Rate", f"{summary['rate']}%")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Retained vs Exited Employees")
    fig = px.pie(
        names=["Retained", "Exited"],
        values=[summary["stayed"], summary["left"]],
        color=["Retained", "Exited"],
        color_discrete_map={"Retained": "#00CC96", "Exited": "#EF553B"},
        hole=0.45,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    polish(fig, 350)
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Attrition Rate by Department")
    dept_df = attrition_rate(df, "Department")
    fig = px.bar(
        dept_df,
        x="Department",
        y="Rate",
        color="Rate",
        color_continuous_scale="RdYlGn_r",
        text="Rate",
        labels={"Rate": "Attrition Rate (%)"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 350)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Age Distribution: Left vs Stayed")
    fig = px.histogram(
        df,
        x="Age",
        color="Attrition_Label",
        barmode="overlay",
        nbins=20,
        color_discrete_map=STATUS_COLORS,
        opacity=0.75,
    )
    polish(fig, 350)
    fig.update_layout(legend_title="Status")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Monthly Income Distribution")
    fig = px.box(
        df,
        x="Attrition_Label",
        y="MonthlyIncome",
        color="Attrition_Label",
        color_discrete_map=STATUS_COLORS,
        points="outliers",
    )
    polish(fig, 350)
    fig.update_layout(showlegend=False, xaxis_title="Status")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Satisfaction & Engagement Scores: Left vs Stayed")

sat_cols = [
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "WorkLifeBalance",
    "JobInvolvement",
    "RelationshipSatisfaction",
]
left_avg = df[df["Attrition"] == 1][sat_cols].mean().round(2).tolist()
stay_avg = df[df["Attrition"] == 0][sat_cols].mean().round(2).tolist()

fig = go.Figure()
fig.add_trace(
    go.Scatterpolar(
        r=left_avg + [left_avg[0]],
        theta=sat_cols + [sat_cols[0]],
        fill="toself",
        name="Left",
        line_color="#EF553B",
    )
)
fig.add_trace(
    go.Scatterpolar(
        r=stay_avg + [stay_avg[0]],
        theta=sat_cols + [sat_cols[0]],
        fill="toself",
        name="Stayed",
        line_color="#00CC96",
    )
)
polish(fig, 400)
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[1, 4])), showlegend=True)
st.plotly_chart(fig, use_container_width=True)
