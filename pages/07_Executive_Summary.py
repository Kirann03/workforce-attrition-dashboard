import plotly.express as px
import streamlit as st

from utils.charts import RATE_SCALE, STATUS_COLORS, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate, attrition_summary
from utils.theme import apply_theme, chart_caption, page_header, render_sidebar, risk_badge, section_divider


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

st.button("Print this page (Ctrl+P / Cmd+P)", type="secondary")
st.caption("Tip: Use Ctrl+P and save as PDF to export this executive summary.")
