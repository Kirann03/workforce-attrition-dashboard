import streamlit as st

from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_summary
from utils.theme import apply_theme, hero, render_sidebar


st.set_page_config(
    page_title="PAN Workforce Intelligence",
    page_icon="PAN",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()

df = load_data()
summary = attrition_summary(df)
dept_hotspot = attrition_rate(df, "Department").sort_values("Rate", ascending=False).iloc[0]
role_hotspot = attrition_rate(df, "JobRole").sort_values("Rate", ascending=False).iloc[0]

hero(
    "Workforce Attrition Pattern Intelligence",
    "A leadership-grade analytics platform for identifying attrition concentration, workforce risk hotspots, and retention signals across departments, job roles, demographics, tenure, and workload factors.",
    "Palo Alto Networks | HR Analytics Command Center",
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Employee Population", f"{summary['total']:,}")
k2.metric("Employees Exited", f"{summary['left']:,}", delta=f"{summary['rate']}% baseline", delta_color="inverse")
k3.metric("Highest-Risk Department", str(dept_hotspot["Department"]), delta=f"{dept_hotspot['Rate']:.1f}%")
k4.metric("Highest-Risk Role", str(role_hotspot["JobRole"]), delta=f"{role_hotspot['Rate']:.1f}%")

st.markdown("### Executive Focus")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="pan-panel">
            <h3>Business Problem</h3>
            <p>High-skill cybersecurity teams cannot manage retention reactively. The platform identifies where attrition is concentrated before leadership commits hiring, compensation, or workload interventions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """
        <div class="pan-panel">
            <h3>Analytical Method</h3>
            <p>Validated workforce records are segmented by department, role, demographics, tenure, compensation, overtime, travel, mobility, and satisfaction indicators.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """
        <div class="pan-panel">
            <h3>Decision Outcome</h3>
            <p>HR leaders can move from generalized retention programs to targeted, evidence-led actions for the specific employee groups most exposed to exit risk.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Intelligence Modules")
m1, m2, m3 = st.columns(3)
m4, m5, m6 = st.columns(3)

modules = [
    (m1, "Overview Dashboard", "Organizational attrition baseline, retention ratio, department rates, income distribution, and satisfaction score comparison."),
    (m2, "Department & Role Analysis", "Department selector, job role filter, role heatmaps, and functional hotspot identification for targeted leadership action."),
    (m3, "Demographic Explorer", "Age, gender, marital status, education, and education-field attrition patterns with department-level filtering."),
    (m4, "Tenure & Workload", "Early-tenure exits, career stage trends, overtime, business travel, promotion stagnation, and distance-from-home effects."),
    (m5, "Risk Scoring Engine", "Gradient Boosting model estimates employee-level attrition probability and ranks major risk drivers."),
    (m6, "Compensation Analysis", "Income bands, salary hike patterns, stock-option levels, and experience-to-income relationships."),
]

for col, title, body in modules:
    with col:
        st.markdown(
            f"""
            <div class="pan-module">
                <strong>{title}</strong>
                <span>{body}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("### Stakeholder Deliverables")
d1, d2 = st.columns([1.15, 0.85])
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
