from datetime import date

import plotly.express as px
import streamlit as st

from utils.charts import RATE_SCALE, STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_summary, cost_of_attrition
from utils.theme import apply_theme, benchmark_table, chart_caption, page_header, render_sidebar, risk_badge, section_divider


st.set_page_config(page_title="Executive Summary", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

st.markdown(
    """
    <style>
    @media print {
        [data-testid="stSidebar"], [data-testid="stToolbar"],
        [data-testid="stDecoration"], button, .stDownloadButton {
            display: none !important;
        }
        .block-container {
            max-width: 100% !important;
            padding: 0 !important;
        }
        div[data-testid="stPlotlyChart"] {
            box-shadow: none !important;
            border: 1px solid #ddd !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

stakeholder_col1, stakeholder_col2 = st.columns([1.2, 0.8])
with stakeholder_col1:
    st.markdown(
        """
        <div class="pan-panel">
            <h3>What this dashboard answers</h3>
            <ul>
                <li>Which departments and job roles experience the highest attrition?</li>
                <li>Is attrition concentrated among age groups, tenure bands, or career stages?</li>
                <li>Do overtime, travel, distance, and promotion stagnation contribute to workforce risk?</li>
                <li>Which compensation and satisfaction signals separate exits from retained employees?</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
with stakeholder_col2:
    st.markdown(
        """
        <div class="pan-panel">
            <h3>Operating Principle</h3>
            <p>Every page is designed as a diagnostic module: filter the workforce, locate
            the hotspot, compare against baseline attrition, and convert the evidence into
            a focused retention action.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

page_header(
    "Leadership Briefing",
    "Executive Summary - Workforce Attrition",
    "A single-page, print-ready diagnostic for HR leadership and stakeholders summarising critical attrition KPIs and action priorities.",
    ["Print-ready", "Leadership KPIs", "Action priorities"],
)

df = load_data()
summary = attrition_summary(df)
baseline = df["Attrition"].mean() * 100
dept_rates = attrition_rate(df, "Department")
role_rates = attrition_rate(df, "JobRole")
dept_hotspot = dept_rates.sort_values("Rate", ascending=False).iloc[0]
role_hotspot = role_rates.sort_values("Rate", ascending=False).iloc[0]
ot_rate = df[df["OverTime"] == "Yes"]["Attrition"].mean() * 100
non_ot_rate = df[df["OverTime"] == "No"]["Attrition"].mean() * 100
early_rate = df[df["YearsAtCompany"] <= 1]["Attrition"].mean() * 100
stock_zero = df[df["StockOptionLevel"] == 0]["Attrition"].mean() * 100
stock_any = df[df["StockOptionLevel"] > 0]["Attrition"].mean() * 100
costs = cost_of_attrition(df)

k1, k2, k3, k4, k5, k6 = st.columns([1, 1, 1, 1, 1, 1])
k1.metric("Headcount", f"{summary['total']:,}")
k2.metric("Exits", f"{summary['left']:,}")
k3.metric("Attrition Rate", f"{summary['rate']}%")
k4.metric("Retention Rate", f"{100 - summary['rate']:.1f}%")
k5.metric("Overtime Attrition", f"{ot_rate:.1f}%")
k6.metric("Early-Tenure Attrition", f"{early_rate:.1f}%")

section_divider("Key Findings")
f1, f2 = st.columns([1, 1])
with f1:
    st.markdown('<div class="pan-panel"><h3>Critical Department Hotspots</h3>', unsafe_allow_html=True)
    table = dept_rates.copy()
    table["Risk"] = table["Rate"].apply(lambda rate: risk_badge(rate, baseline))
    table = table.rename(columns={"Rate": "Attrition %", "Total": "Headcount"})[
        ["Department", "Headcount", "Attrition %", "Risk"]
    ]
    st.write(table.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with f2:
    st.markdown(
        f"""
        <div class="pan-panel">
            <h3>Headline Insights</h3>
            <ul>
                <li><strong>{dept_hotspot['Department']}</strong> is the highest-risk department at <strong>{dept_hotspot['Rate']:.1f}%</strong>.</li>
                <li><strong>{role_hotspot['JobRole']}</strong> is the highest-risk role at <strong>{role_hotspot['Rate']:.1f}%</strong>.</li>
                <li>Overtime employees show <strong>{ot_rate:.1f}%</strong> attrition versus <strong>{non_ot_rate:.1f}%</strong> without overtime.</li>
                <li>No-stock-option employees leave at <strong>{stock_zero:.1f}%</strong> versus <strong>{stock_any:.1f}%</strong> for option holders.</li>
                <li>Early-tenure employees exit at <strong>{early_rate:.1f}%</strong>.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

section_divider("Supporting Charts")
ch1, ch2, ch3 = st.columns([1, 1, 1])
with ch1:
    fig = px.pie(
        names=["Retained", "Exited"],
        values=[summary["stayed"], summary["left"]],
        color=["Retained", "Exited"],
        color_discrete_map={"Retained": STATUS_COLORS["Stayed"], "Exited": STATUS_COLORS["Left"]},
        hole=0.55,
    )
    polish(fig, 300, title="Workforce Retention Mix")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

with ch2:
    fig = px.bar(
        dept_rates.sort_values("Rate"),
        x="Rate",
        y="Department",
        orientation="h",
        color="Rate",
        color_continuous_scale=RATE_SCALE,
        text="Rate",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    polish(fig, 300, title="Attrition by Department")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

with ch3:
    top_roles = role_rates.sort_values("Rate", ascending=True).tail(8)
    fig = px.bar(
        top_roles,
        x="Rate",
        y="JobRole",
        orientation="h",
        color="Rate",
        color_continuous_scale=RATE_SCALE,
        text="Rate",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    polish(fig, 300, title="Top 8 Roles by Attrition Rate")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(df))

section_divider("Recommended Priority Actions")
actions = [
    ("P1 - Immediate", f"Review workload caps for overtime employees at {ot_rate:.1f}% attrition."),
    ("P1 - Immediate", f"Conduct role-level retention review for {role_hotspot['JobRole']}."),
    ("P2 - 30 days", "Accelerate promotion pipeline for employees with 3+ years since last promotion."),
    ("P2 - 30 days", f"Expand stock option review; level 0 employees leave at {stock_zero:.1f}%."),
    ("P3 - 90 days", f"Strengthen onboarding and 90-day retention; early-tenure attrition is {early_rate:.1f}%."),
]
for priority, action in actions:
    st.markdown(
        f"""
        <div style="display:flex;gap:12px;align-items:flex-start;padding:0.7rem 0;border-bottom:1px solid var(--pan-border)">
            <span style="font-size:0.75rem;font-weight:700;color:var(--pan-muted);min-width:110px">{priority}</span>
            <span style="font-size:0.91rem;color:var(--pan-text)">{action}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    target_page = "pages/04_Tenure_Workload.py" if "overtime" in action.lower() or "onboarding" in action.lower() else ("pages/06_Compensation.py" if "stock" in action.lower() else "pages/02_Department_Role.py")
    st.page_link(target_page, label="Open supporting analysis")

section_divider("Benchmark Comparison")
benchmark_rows = [
    {"metric": "Attrition Rate", "company": f"{summary['rate']}%", "industry": "13.0%", "status": "warn" if summary["rate"] <= 18 else "risk"},
    {"metric": "Early Tenure Attrition", "company": f"{early_rate:.1f}%", "industry": "18.0%", "status": "warn" if early_rate <= 25 else "risk"},
    {"metric": "Overtime Attrition", "company": f"{ot_rate:.1f}%", "industry": "22.0%", "status": "risk" if ot_rate > 22 else "good"},
    {"metric": "Training Sessions", "company": f"{df['TrainingTimesLastYear'].mean():.1f}", "industry": "2.5", "status": "good" if df["TrainingTimesLastYear"].mean() >= 2.5 else "warn"},
    {"metric": "Promotion Rate", "company": f"{(df['YearsSinceLastPromotion'] == 0).mean() * 100:.1f}%", "industry": "16.0%", "status": "good"},
]
benchmark_table(benchmark_rows)

try:
    from fpdf import FPDF

    pdf = FPDF()
    for page_no in range(1, 4):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Palo Alto Networks Workforce Attrition Report", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"Generated: {date.today().isoformat()} | Page {page_no}", ln=True)
        pdf.ln(4)
        if page_no == 1:
            for label, value in [
                ("Headcount", f"{summary['total']:,}"),
                ("Exits", f"{summary['left']:,}"),
                ("Attrition Rate", f"{summary['rate']}%"),
                ("Overtime Attrition", f"{ot_rate:.1f}%"),
                ("Early Tenure Attrition", f"{early_rate:.1f}%"),
                ("Estimated Annual Cost", f"${costs['total_annual_cost']:,.0f}"),
            ]:
                pdf.cell(0, 8, f"{label}: {value}", ln=True)
        elif page_no == 2:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Critical Findings", ln=True)
            pdf.set_font("Helvetica", "", 10)
            findings = [
                f"{dept_hotspot['Department']} is the highest-risk department at {dept_hotspot['Rate']:.1f}%.",
                f"{role_hotspot['JobRole']} is the highest-risk role at {role_hotspot['Rate']:.1f}%.",
                f"Overtime employees show {ot_rate:.1f}% attrition.",
                f"Level 0 stock option employees show {stock_zero:.1f}% attrition.",
                f"Early-tenure employees exit at {early_rate:.1f}%.",
            ]
            for finding in findings:
                pdf.multi_cell(190, 6, f"- {finding}")
        else:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "Recommended Priority Actions", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for priority, action in actions:
                pdf.multi_cell(190, 6, f"- {priority}: {action}")
    pdf_bytes = bytes(pdf.output(dest="S"))
    st.download_button("Download PDF Report", pdf_bytes, "executive_attrition_report.pdf", "application/pdf")
except ImportError:
    st.info("Install fpdf2 to enable PDF export: pip install fpdf2>=2.7.0")

st.button("Print this page (Ctrl+P / Cmd+P)", type="secondary")
st.caption("Tip: Use Ctrl+P and save as PDF to export this executive summary.")

section_divider("Analytics Navigation Hub")
st.markdown("### Analytics Modules")
st.markdown(
    '<p style="color:var(--pan-muted);font-size:0.9rem;margin-bottom:1rem">'
    "Navigate directly to any analytical module below.</p>",
    unsafe_allow_html=True,
)

modules = [
    (
        "01",
        "Overview Dashboard",
        "Organizational baseline, retention mix, satisfaction gaps, and workload-risk interpretation.",
        "pages/01_Overview.py",
        "#82A9C7",
    ),
    (
        "02",
        "Department & Role",
        "Hotspot matrix, benchmark comparison, role scatter, and intervention callout.",
        "pages/02_Department_Role.py",
        "#ACCCD8",
    ),
    (
        "03",
        "Demographic Explorer",
        "Age, gender, marital status, education, and intersectional risk analysis.",
        "pages/03_Demographics.py",
        "#313A55",
    ),
    (
        "04",
        "Tenure & Workload",
        "Overtime, travel, promotion bands, distance confidence intervals, and key findings.",
        "pages/04_Tenure_Workload.py",
        "#F0E2CD",
    ),
    (
        "05",
        "Risk Scoring Engine",
        "Balanced ML model, risk tiers, performance metrics, feature drivers, and intervention matrix.",
        "pages/05_Risk_Score.py",
        "#C9BDAE",
    ),
    (
        "06",
        "Compensation Analysis",
        "Pay equity, hike-performance patterns, stock-option gaps, and salary-band risk.",
        "pages/06_Compensation.py",
        "#82A9C7",
    ),
    (
        "09",
        "What-If Simulator",
        "Interactive scenario planning for individual attrition risk and intervention design.",
        "pages/09_What_If_Simulator.py",
        "#313A55",
    ),
    (
        "10",
        "Survival Analysis",
        "Kaplan-Meier tenure survival curves and hazard spike detection.",
        "pages/10_Survival_Analysis.py",
        "#82A9C7",
    ),
    (
        "11",
        "Retention ROI",
        "Financial cost of attrition and retention program ROI modeling.",
        "pages/11_Retention_ROI.py",
        "#C9BDAE",
    ),
    (
        "12",
        "Action Plan",
        "Auto-generated HR recommendations with evidence citations and exports.",
        "pages/12_Recommendations.py",
        "#ACCCD8",
    ),
    (
        "08",
        "Cohort Analysis",
        "Custom two-dimensional cohort matrices, top-risk combinations, and statistical validation.",
        "pages/08_Cohort_Analysis.py",
        "#ACCCD8",
    ),
]

module_rows = [st.columns(3) for _ in range((len(modules) + 2) // 3)]
for idx, (num, title, body, page, color) in enumerate(modules):
    with module_rows[idx // 3][idx % 3]:
        st.markdown(
            f"""
            <div class="pan-module" style="border-left:3px solid {color}">
                <span class="pan-module-number">{num}</span>
                <strong>{title}</strong>
                <span>{body}</span>
                <div class="pan-module-cta">Open module &rarr;</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label=f"Open {title}", use_container_width=True)
