import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.charts import STATUS_COLORS, polish
from utils.config import SATISFACTION_COLS, SATISFACTION_LABELS
from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_summary
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, page_header, render_sidebar


st.set_page_config(page_title="Attrition Overview", page_icon="📊", layout="wide")
apply_theme()
render_sidebar()

df_all = load_data()
data_quality_banner(df_all)

st.sidebar.header("Workforce Filters")
departments = sorted(df_all["Department"].dropna().unique().tolist())
selected_depts = st.sidebar.multiselect("Department", departments, default=departments)
roles = sorted(df_all[df_all["Department"].isin(selected_depts)]["JobRole"].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect("Job Role", roles, default=roles)
tenure_range = st.sidebar.slider(
    "Years at Company",
    int(df_all["YearsAtCompany"].min()),
    int(df_all["YearsAtCompany"].max()),
    (int(df_all["YearsAtCompany"].min()), int(df_all["YearsAtCompany"].max())),
)
overtime = st.sidebar.multiselect("OverTime", ["Yes", "No"], default=["Yes", "No"])
travel = sorted(df_all["BusinessTravel"].dropna().unique().tolist())
selected_travel = st.sidebar.multiselect("Business Travel", travel, default=travel)
df = df_all[
    df_all["Department"].isin(selected_depts)
    & df_all["JobRole"].isin(selected_roles)
    & df_all["YearsAtCompany"].between(tenure_range[0], tenure_range[1])
    & df_all["OverTime"].isin(overtime)
    & df_all["BusinessTravel"].isin(selected_travel)
]
st.sidebar.metric("Filtered Records", len(df))

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

page_header(
    "Organizational Baseline",
    "Attrition Overview Dashboard",
    "Monitor workforce turnover, retained-versus-exited distribution, department-level attrition, compensation spread, and satisfaction gaps.",
    ["Attrition rate", "Department baseline", "Satisfaction signals"],
)

summary = attrition_summary(df)
risk_flag = int(df["WorkloadStress"].sum())

c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1.1])
c1.metric("Total Employees", f"{summary['total']:,}")
c2.metric("Employees Left", f"{summary['left']:,}", delta=f"{summary['rate']}% attrition", delta_color="inverse")
c3.metric("Employees Retained", f"{summary['stayed']:,}")
c4.metric("Attrition Rate", f"{summary['rate']}%")
c5.metric("Risk-Flag Employees", f"{risk_flag:,}", delta="Overtime + frequent travel", delta_color="inverse")

dept_df = attrition_rate(df, "Department")
top_dept = dept_df.sort_values("Rate", ascending=False).iloc[0]
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
        color_continuous_scale="RdYlGn_r",
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

st.markdown("---")
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
