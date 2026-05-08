import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.charts import RATE_SCALE, STATUS_COLORS, polish
from utils.config import SATISFACTION_COLS, SATISFACTION_LABELS
from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_summary
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, hero, render_global_filters, render_sidebar, section_divider


st.set_page_config(page_title="Attrition Overview", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df_all = load_data()
data_quality_banner(df_all)

df = render_global_filters(df_all)

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

hero(
    "Workforce Attrition Pattern Intelligence",
    "A leadership-grade analytics platform for identifying attrition concentration, workforce risk hotspots, and retention signals across departments, job roles, demographics, tenure, workload, compensation, and predictive risk segments.",
    "Palo Alto Networks | HR Analytics",
)

summary = attrition_summary(df)
risk_flag = int(df["WorkloadStress"].sum())
dept_df = attrition_rate(df, "Department")
role_df = attrition_rate(df, "JobRole")
top_dept = dept_df.sort_values("Rate", ascending=False).iloc[0]
top_role = role_df.sort_values("Rate", ascending=False).iloc[0]

c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 1.15, 1.15])
c1.metric("Total Employees", f"{summary['total']:,}")
c2.metric("Employees Left", f"{summary['left']:,}", delta=f"{summary['rate']}% attrition", delta_color="inverse")
c3.metric("Employees Retained", f"{summary['stayed']:,}")
c4.metric("Attrition Rate", f"{summary['rate']}%")
c5.metric("Highest-Risk Department", str(top_dept["Department"]), delta=f"{top_dept['Rate']:.1f}%", delta_color="inverse")
c6.metric("Highest-Risk Role", str(top_role["JobRole"]), delta=f"{top_role['Rate']:.1f}%", delta_color="inverse")

stress_rate = df[df["WorkloadStress"] == 1]["Attrition"].mean() * 100 if risk_flag else 0
st.info(
    f"The overall attrition rate is {summary['rate']}%. {top_dept['Department']} has the highest department rate "
    f"at {top_dept['Rate']:.1f}%. Employees with overtime plus frequent travel show {stress_rate:.1f}% attrition."
)

col1, col2 = st.columns([0.9, 1.1])
with col1:
    st.subheader("Retained vs Exited Employees")
    fig = px.pie(
        names=["Retained", "Exited"],
        values=[summary["stayed"], summary["left"]],
        color=["Retained", "Exited"],
        color_discrete_map={"Retained": STATUS_COLORS["Stayed"], "Exited": STATUS_COLORS["Left"]},
        hole=0.58,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    polish(fig, 370)
    fig.update_layout(
        annotations=[
            dict(text=f"{summary['rate']}%<br>Attrition", x=0.5, y=0.5, font_size=24, showarrow=False)
        ],
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

with col2:
    st.subheader("Attrition Rate by Department")
    fig = px.bar(
        dept_df,
        x="Department",
        y="Rate",
        color="Rate",
        color_continuous_scale=RATE_SCALE,
        text="Rate",
        labels={"Rate": "Attrition Rate (%)"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    polish(fig, 370)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

col3, col4 = st.columns([1, 1])
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
    chart_caption(len(df))

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
    chart_caption(len(df))

section_divider()
st.subheader("Satisfaction & Engagement Scores: Left vs Stayed")

left_avg = df[df["Attrition"] == 1][SATISFACTION_COLS].mean().round(2)
stay_avg = df[df["Attrition"] == 0][SATISFACTION_COLS].mean().round(2)
labels = [SATISFACTION_LABELS.get(col, col) for col in SATISFACTION_COLS]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(r=left_avg.tolist() + [left_avg.iloc[0]], theta=labels + [labels[0]], fill="toself", name="Left", line_color=STATUS_COLORS["Left"]))
fig.add_trace(go.Scatterpolar(r=stay_avg.tolist() + [stay_avg.iloc[0]], theta=labels + [labels[0]], fill="toself", name="Stayed", line_color=STATUS_COLORS["Stayed"]))
polish(fig, 420)
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[1, 4])), showlegend=True)
st.plotly_chart(fig, use_container_width=True)
chart_caption(len(df))

gap_table = pd.DataFrame(
    {
        "Dimension": labels,
        "Left Mean": left_avg.values,
        "Stayed Mean": stay_avg.values,
    }
)
gap_table["Gap"] = (gap_table["Stayed Mean"] - gap_table["Left Mean"]).round(2)
gap_table = gap_table.sort_values("Gap", ascending=False)
st.subheader("Satisfaction Gap Table")
st.dataframe(gap_table, use_container_width=True, hide_index=True)

download_filtered_data(df, "overview_workforce_data.csv")
