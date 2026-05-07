import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.charts import STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(page_title="Compensation Analysis", layout="wide")
apply_theme()
render_sidebar()
page_header(
    "Rewards & Retention",
    "Compensation & Attrition Analysis",
    "Evaluate whether monthly income, salary hikes, stock options, and experience-to-income patterns are associated with employee exits.",
    ["Income bands", "Salary hike", "Stock options"],
)

df = load_data()

c1, c2 = st.columns(2)
with c1:
    st.subheader("Monthly Income vs Attrition by Job Role")
    fig = px.box(
        df,
        x="JobRole",
        y="MonthlyIncome",
        color="Attrition_Label",
        color_discrete_map=STATUS_COLORS,
        points=False,
    )
    polish(fig, 420)
    fig.update_layout(xaxis_tickangle=-30, legend_title="Status")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Salary Hike % vs Attrition")
    fig = px.violin(
        df,
        x="Attrition_Label",
        y="PercentSalaryHike",
        color="Attrition_Label",
        color_discrete_map=STATUS_COLORS,
        box=True,
        points="outliers",
    )
    polish(fig, 420)
    fig.update_layout(showlegend=False, xaxis_title="Status")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

c3, c4 = st.columns(2)
with c3:
    st.subheader("Income Band Attrition Rate")
    ib = attrition_rate(df, "IncomeBand")
    fig = px.bar(ib, x="IncomeBand", y="Rate", color="Rate", color_continuous_scale="RdYlGn_r", text="Rate")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Stock Options vs Attrition")
    so = attrition_rate(df, "StockOptionLevel")
    so["StockOptionLevel"] = so["StockOptionLevel"].astype(str)
    fig = px.bar(
        so,
        x="StockOptionLevel",
        y="Rate",
        color="Rate",
        color_continuous_scale="Blues_r",
        text="Rate",
        labels={"StockOptionLevel": "Stock Option Level"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 360)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Income vs Years of Experience (colored by Attrition)")
fig = px.scatter(
    df,
    x="TotalWorkingYears",
    y="MonthlyIncome",
    color="Attrition_Label",
    size="YearsAtCompany",
    hover_data=["JobRole", "Department"],
    color_discrete_map=STATUS_COLORS,
    opacity=0.65,
)
polish(fig, 450)
fig.update_layout(legend_title="Status")
st.plotly_chart(fig, use_container_width=True)
