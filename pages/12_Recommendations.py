from datetime import date

import pandas as pd
import streamlit as st

from utils.data_loader import load_data
from utils.kpis import attrition_rate, cost_of_attrition
from utils.theme import apply_theme, data_quality_banner, page_header, render_sidebar, section_divider


st.set_page_config(page_title="HR Action Plan", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)
page_header(
    "Action Planning",
    "Auto-Generated HR Action Plan",
    "Translate attrition signals into prioritized, evidence-backed retention actions for leadership review.",
    ["P1/P2/P3 priorities", "Evidence citations", "CSV/PDF export"],
)


def build_recommendations(data: pd.DataFrame) -> list[dict]:
    baseline = data["Attrition"].mean() * 100
    recs = []
    ot_rate = data[data["OverTime"] == "Yes"]["Attrition"].mean() * 100
    if ot_rate > 1.5 * baseline:
        recs.append({
            "priority": "P1 - Immediate",
            "area": "Workload",
            "finding": f"Overtime employees show {ot_rate:.1f}% attrition, {ot_rate / baseline:.1f}x baseline.",
            "action": "Implement overtime caps and weekly workload balancing.",
            "metric": "Reduce overtime attrition to <= 1.2x baseline within 90 days.",
            "evidence": "Tenure & Workload - Overtime analysis",
        })
    stock0 = data[data["StockOptionLevel"] == 0]["Attrition"].mean() * 100
    if stock0 > baseline:
        recs.append({
            "priority": "P2 - Short-term",
            "area": "Compensation",
            "finding": f"Employees without stock options show {stock0:.1f}% attrition.",
            "action": "Pilot equity refresh grants for Level 0 employees in high-exit roles.",
            "metric": "Reduce Level 0 attrition by 20% in two quarters.",
            "evidence": "Compensation - Stock option analysis",
        })
    early = data[data["YearsAtCompany"] <= 1]["Attrition"].mean() * 100
    if early > baseline:
        recs.append({
            "priority": "P1 - Immediate",
            "area": "Early Tenure",
            "finding": f"Employees in their first year show {early:.1f}% attrition.",
            "action": "Launch a 30/60/90-day onboarding and manager check-in program.",
            "metric": "Reduce first-year exits by 25%.",
            "evidence": "Tenure & Workload - Tenure bucket analysis",
        })
    travel = data[data["BusinessTravel"] == "Travel_Frequently"]["Attrition"].mean() * 100
    if travel > baseline:
        recs.append({
            "priority": "P2 - Short-term",
            "area": "Travel Load",
            "finding": f"Frequent travelers show {travel:.1f}% attrition.",
            "action": "Offer travel rotation, remote alternatives, and recovery days.",
            "metric": "Lower travel-related attrition lift below 5 percentage points.",
            "evidence": "Tenure & Workload - Business travel analysis",
        })
    top_dept = attrition_rate(data, "Department").sort_values("Rate", ascending=False).iloc[0]
    top_role = attrition_rate(data, "JobRole").sort_values("Rate", ascending=False).iloc[0]
    recs.append({
        "priority": "P1 - Immediate",
        "area": "Department Hotspot",
        "finding": f"{top_dept['Department']} is the highest-risk department at {top_dept['Rate']:.1f}% attrition.",
        "action": "Run a department-specific retention sprint with role-level root cause review.",
        "metric": "Bring department attrition within 2 points of company baseline.",
        "evidence": "Department & Role - Benchmark comparison",
    })
    recs.append({
        "priority": "P2 - Short-term",
        "area": "Role Hotspot",
        "finding": f"{top_role['JobRole']} is the highest-risk role at {top_role['Rate']:.1f}% attrition.",
        "action": "Review role design, manager coverage, pay bands, and career path clarity.",
        "metric": "Reduce top-role attrition by 30%.",
        "evidence": "Department & Role - Role heatmap",
    })
    low_sat = data[data["SatisfactionIndex"] <= 2.25]["Attrition"].mean() * 100
    if low_sat > baseline:
        recs.append({
            "priority": "P3 - Strategic",
            "area": "Employee Experience",
            "finding": f"Low-satisfaction employees show {low_sat:.1f}% attrition.",
            "action": "Create targeted engagement plans for low-satisfaction teams.",
            "metric": "Improve satisfaction index by 0.3 points in 6 months.",
            "evidence": "Overview - Satisfaction gap analysis",
        })
    return recs


recommendations = build_recommendations(df)
for priority in ["P1 - Immediate", "P2 - Short-term", "P3 - Strategic"]:
    section_divider(priority)
    for rec in [item for item in recommendations if item["priority"] == priority]:
        st.markdown(
            f"""
            <div class="pan-insight-card">
                <div class="pan-insight-icon">{rec['priority'].split()[0]}</div>
                <div>
                    <div class="pan-insight-title">{rec['area']}: {rec['finding']}</div>
                    <div class="pan-insight-body"><strong>Action:</strong> {rec['action']}<br><strong>Metric:</strong> {rec['metric']}<br><strong>Evidence:</strong> {rec['evidence']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

rec_df = pd.DataFrame(recommendations)
st.download_button("Download Action Plan as CSV", rec_df.to_csv(index=False), "hr_action_plan.csv", "text/csv")

try:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Palo Alto Networks Workforce Retention Brief", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {date.today().isoformat()}", ln=True)
    costs = cost_of_attrition(df)
    pdf.cell(0, 8, f"Headcount: {len(df):,} | Exits: {costs['n_exits']:,} | Estimated Cost: ${costs['total_annual_cost']:,.0f}", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Top Recommendations", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for rec in recommendations[:5]:
        pdf.multi_cell(190, 6, f"- {rec['priority']} | {rec['area']}: {rec['action']}")
    pdf_bytes = bytes(pdf.output(dest="S"))
    st.download_button("Download Executive Brief as PDF", pdf_bytes, "retention_action_brief.pdf", "application/pdf")
except ImportError:
    st.info("Install fpdf2 to enable PDF export: pip install fpdf2>=2.7.0")
