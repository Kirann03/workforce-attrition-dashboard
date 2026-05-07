import pandas as pd
import streamlit as st

from utils.config import ATTRITION_HIGH_THRESHOLD
from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_summary
from utils.theme import apply_theme, data_quality_banner, hero, render_sidebar, risk_badge


st.set_page_config(
    page_title="PAN Workforce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)

summary = attrition_summary(df)
baseline_rate = df["Attrition"].mean() * 100
dept_rates = attrition_rate(df, "Department").sort_values("Rate", ascending=False)
role_rates = attrition_rate(df, "JobRole").sort_values("Rate", ascending=False)
dept_hotspot = dept_rates.iloc[0]
role_hotspot = role_rates.iloc[0]

hero(
    "Workforce Attrition Pattern Intelligence",
    "A leadership-grade analytics platform for identifying attrition concentration, workforce risk hotspots, and retention signals across departments, job roles, demographics, tenure, workload, compensation, and predictive risk segments.",
    "Palo Alto Networks | HR Analytics Command Center",
)

k1, k2, k3, k4 = st.columns([1, 1, 1.2, 1.2])
k1.metric("Employee Population", f"{summary['total']:,}")
k2.metric("Employees Exited", f"{summary['left']:,}", delta=f"{summary['rate']}% baseline", delta_color="inverse")
k3.metric("Highest-Risk Department", str(dept_hotspot["Department"]), delta=f"{dept_hotspot['Rate']:.1f}%")
k4.metric("Highest-Risk Role", str(role_hotspot["JobRole"]), delta=f"{role_hotspot['Rate']:.1f}%")

st.markdown("### Critical Alerts")
alerts = []
for _, row in dept_rates.iterrows():
    if row["Rate"] / 100 > ATTRITION_HIGH_THRESHOLD:
        alerts.append(f"{row['Department']} department is above the 30% high-risk threshold at {row['Rate']:.1f}% attrition.")
for _, row in role_rates.iterrows():
    if row["Rate"] / 100 > ATTRITION_HIGH_THRESHOLD:
        alerts.append(f"{row['JobRole']} role is above the 30% high-risk threshold at {row['Rate']:.1f}% attrition.")

if alerts:
    for alert in alerts[:4]:
        st.warning(alert)
else:
    st.success("No department or role exceeds the 30% high-risk attrition threshold.")

st.markdown("### At-a-Glance Department Summary")
top_role_by_dept = (
    df.groupby(["Department", "JobRole"], observed=False)
    .agg(Total=("Attrition", "count"), Left=("Attrition", "sum"))
    .reset_index()
)
top_role_by_dept["Rate"] = (top_role_by_dept["Left"] / top_role_by_dept["Total"] * 100).fillna(0)
top_role_by_dept = top_role_by_dept.sort_values(["Department", "Rate"], ascending=[True, False])
top_role_by_dept = top_role_by_dept.drop_duplicates("Department").set_index("Department")["JobRole"]

summary_table = dept_rates.rename(columns={"Rate": "Attrition %", "Total": "Total Employees"}).copy()
summary_table["Risk Level"] = summary_table["Attrition %"].apply(lambda rate: risk_badge(rate, baseline_rate))
summary_table["Top Exit Role"] = summary_table["Department"].map(top_role_by_dept)
summary_table = summary_table[["Department", "Total Employees", "Attrition %", "Risk Level", "Top Exit Role"]]
st.write(
    summary_table.to_html(escape=False, index=False),
    unsafe_allow_html=True,
)

st.markdown("### Intelligence Modules")
modules = [
    ("Overview Dashboard", "Organizational baseline, retention mix, satisfaction gaps, and workload-risk interpretation.", "pages/01_Overview.py"),
    ("Department & Role Analysis", "Hotspot matrix, benchmark comparison, role scatter, and intervention callout.", "pages/02_Department_Role.py"),
    ("Demographic Explorer", "Age, gender, marital status, education, and intersectional risk analysis.", "pages/03_Demographics.py"),
    ("Tenure & Workload", "Overtime, travel, promotion stagnation, distance confidence intervals, and key findings.", "pages/04_Tenure_Workload.py"),
    ("Risk Scoring Engine", "Balanced ML model, risk tiers, performance metrics, feature drivers, and intervention matrix.", "pages/05_Risk_Score.py"),
    ("Compensation Analysis", "Pay equity, hike-performance patterns, stock-option gaps, and salary-band risk.", "pages/06_Compensation.py"),
]

rows = [st.columns([1, 1, 1]), st.columns([1, 1, 1])]
for idx, (title, body, page) in enumerate(modules):
    with rows[idx // 3][idx % 3]:
        st.markdown(
            f"""
            <div class="pan-module">
                <strong>{title}</strong>
                <span>{body}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label=f"Open {title}", use_container_width=True)

st.markdown("### Stakeholder Deliverables")
d1, d2 = st.columns([1.2, 0.8])
with d1:
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
with d2:
    st.markdown(
        """
        <div class="pan-panel">
            <h3>Operating Principle</h3>
            <p>Every page is designed as a diagnostic module: filter the workforce, locate the hotspot, compare against baseline attrition, and convert the evidence into a focused retention action.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
