import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import RATE_SCALE, polish
from utils.data_loader import load_data
from utils.kpis import cost_of_attrition, retention_roi
from utils.theme import apply_theme, data_quality_banner, page_header, render_sidebar, roi_card, section_divider


st.set_page_config(page_title="Retention ROI", page_icon="💼", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)
page_header(
    "Financial Impact",
    "Cost of Attrition & Retention ROI",
    "Translate workforce exits into business cost, savings potential, and retention investment decisions.",
    ["Cost model", "Savings scenarios", "ROI calculator"],
)

avg_salary = float(df["MonthlyIncome"].mean() * 12)
st.sidebar.markdown("### Attrition Cost Assumptions")
annual_salary = st.sidebar.number_input("Average Annual Salary", min_value=0.0, value=avg_salary, step=1000.0)
replacement_pct = st.sidebar.number_input("Replacement Cost % of Salary", min_value=0.0, value=50.0, step=5.0) / 100
recruitment_cost = st.sidebar.number_input("Recruitment Cost per Hire", min_value=0.0, value=5000.0, step=500.0)
training_cost = st.sidebar.number_input("Training Cost per Hire", min_value=0.0, value=3000.0, step=500.0)
productivity_months = st.sidebar.number_input("Lost Productivity Period (months)", min_value=0, value=3, step=1)
productivity_pct = st.sidebar.number_input("Lost Productivity %", min_value=0.0, value=25.0, step=5.0) / 100

cost_per_exit = (
    annual_salary * replacement_pct
    + recruitment_cost
    + training_cost
    + (annual_salary / 12) * productivity_months * productivity_pct
)
total_cost = cost_per_exit * int(df["Attrition"].sum())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Cost per Exit", f"${cost_per_exit:,.0f}")
k2.metric("Annual Attrition Cost", f"${total_cost:,.0f}")
k3.metric("Employees Exited", f"{int(df['Attrition'].sum()):,}")
k4.metric("20% Reduction Savings", f"${total_cost * 0.20:,.0f}")

section_divider("Cost Breakdown")
breakdown = pd.DataFrame(
    {
        "Cost Component": ["Replacement Search", "Recruitment", "Training", "Productivity Loss"],
        "Cost": [
            annual_salary * replacement_pct,
            recruitment_cost,
            training_cost,
            (annual_salary / 12) * productivity_months * productivity_pct,
        ],
    }
)
fig = px.bar(breakdown, x="Cost Component", y="Cost", color="Cost", color_continuous_scale=RATE_SCALE, text="Cost")
fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
polish(fig, 360, title="Cost Breakdown per Exit")
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

section_divider("Savings Scenarios")
dept_exits = df.groupby("Department").agg(Exits=("Attrition", "sum")).reset_index()
scenario_rows = []
for reduction in [10, 20, 30, 50]:
    for _, row in dept_exits.iterrows():
        scenario_rows.append(
            {
                "Department": row["Department"],
                "Reduction Scenario": f"{reduction}%",
                "Estimated Savings": round(row["Exits"] * cost_per_exit * reduction / 100, 0),
            }
        )
scenario_df = pd.DataFrame(scenario_rows)
st.dataframe(scenario_df.sort_values("Estimated Savings", ascending=False), use_container_width=True, hide_index=True)

section_divider("Retention ROI Calculator")
program_cost = st.number_input("Proposed Retention Program Cost", min_value=0.0, value=150000.0, step=10000.0)
expected_reduction = st.slider("Expected Attrition Reduction (%)", 5, 50, 20)
roi = retention_roi(total_cost, expected_reduction, program_cost)
c1, c2, c3 = st.columns(3)
with c1:
    roi_card(f"${roi['gross_savings']:,.0f}", "Gross Savings", True)
with c2:
    roi_card(f"${roi['net_savings']:,.0f}", "Net Savings", roi["break_even"])
with c3:
    roi_card(f"{roi['roi_pct']:,.1f}%", "Program ROI", roi["break_even"])
st.success("Go recommendation: expected savings exceed program cost.") if roi["break_even"] else st.error("No-Go recommendation: program cost exceeds expected savings.")

section_divider("Department Cost Breakdown")
dept_exits["Estimated Attrition Cost"] = dept_exits["Exits"] * cost_per_exit
dept_exits = dept_exits.sort_values("Estimated Attrition Cost", ascending=False)
st.dataframe(dept_exits, use_container_width=True, hide_index=True)
fig = px.bar(dept_exits, x="Department", y="Estimated Attrition Cost", color="Estimated Attrition Cost", color_continuous_scale=RATE_SCALE)
polish(fig, 360, title="Estimated Attrition Cost by Department")
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)
