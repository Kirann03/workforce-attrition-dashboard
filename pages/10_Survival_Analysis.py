import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import RATE_SCALE, km_curve_chart, polish
from utils.data_loader import load_data
from utils.kpis import attrition_rate
from utils.theme import apply_theme, data_quality_banner, insight_card, page_header, render_global_filters, render_sidebar, section_divider


st.set_page_config(page_title="Survival Analysis", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df_all = load_data()
data_quality_banner(df_all)
page_header(
    "Tenure Survival",
    "Tenure Survival & Flight Risk Curves",
    "Estimate how retention probability changes over tenure and identify the years where exit hazard spikes.",
    ["Kaplan-Meier", "Hazard spikes", "Tenure risk"],
)

df = render_global_filters(df_all)
if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


@st.cache_data
def km_tables(data: pd.DataFrame, group_col: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    from lifelines import KaplanMeierFitter

    km_rows = []
    ci_rows = []
    median_rows = []
    groups = data[group_col].dropna().unique() if group_col else [None]
    for group in groups:
        subset = data[data[group_col] == group] if group_col else data
        if subset.empty:
            continue
        kmf = KaplanMeierFitter()
        kmf.fit(subset["YearsAtCompany"], event_observed=subset["Attrition"], label=str(group) if group_col else "All")
        surv = kmf.survival_function_.reset_index()
        surv.columns = ["timeline", "KM_estimate"]
        ci = kmf.confidence_interval_survival_function_.reset_index()
        ci.columns = ["timeline", "KM_estimate_lower_0.95", "KM_estimate_upper_0.95"]
        if group_col:
            surv[group_col] = group
            ci[group_col] = group
        km_rows.append(surv)
        ci_rows.append(ci)
        median_rows.append({group_col or "Group": group or "All", "Median Survival Years": kmf.median_survival_time_})
    return pd.concat(km_rows, ignore_index=True), pd.concat(ci_rows, ignore_index=True), pd.DataFrame(median_rows)


@st.cache_data
def hazard_table(data: pd.DataFrame) -> pd.DataFrame:
    grouped = data.groupby("YearsAtCompany").agg(AtRisk=("Attrition", "count"), Exits=("Attrition", "sum")).reset_index()
    grouped["HazardRate"] = (grouped["Exits"] / grouped["AtRisk"] * 100).fillna(0).round(2)
    baseline = data["Attrition"].mean() * 100
    grouped["Spike"] = grouped["HazardRate"] > baseline * 2
    return grouped


try:
    import lifelines  # noqa: F401
except ImportError:
    st.error("Install lifelines to run this page: pip install lifelines>=0.27.0")
    st.stop()

section_divider("Kaplan-Meier Survival Curves")
dept_km, dept_ci, dept_median = km_tables(df, "Department")
fig = km_curve_chart(dept_km, dept_ci, "Department", "Survival Probability by Department")
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    ot_km, ot_ci, _ = km_tables(df, "OverTime")
    fig = km_curve_chart(ot_km, ot_ci, "OverTime", "Survival by Overtime Status")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    jl_km, jl_ci, _ = km_tables(df, "JobLevel")
    fig = km_curve_chart(jl_km, jl_ci, "JobLevel", "Survival by Job Level")
    st.plotly_chart(fig, use_container_width=True)

section_divider("Median Survival & Hazard")
median_display = dept_median.replace([np.inf, -np.inf], np.nan)
st.dataframe(median_display, use_container_width=True, hide_index=True)
top_dept = attrition_rate(df, "Department").sort_values("Rate", ascending=False).iloc[0]
insight_card(
    "Flight Risk Concentration",
    f"{top_dept['Department']} currently has the highest observed attrition rate at {top_dept['Rate']:.1f}%, so survival monitoring should start there.",
)

hazard = hazard_table(df)
fig = px.bar(hazard, x="YearsAtCompany", y="HazardRate", color="Spike", color_discrete_map={True: "#313A55", False: "#82A9C7"})
polish(fig, 390, title="Binned Annual Hazard Rate")
st.plotly_chart(fig, use_container_width=True)
spikes = hazard[hazard["Spike"]]
if not spikes.empty:
    st.warning("Spike years detected: " + ", ".join(str(int(year)) for year in spikes["YearsAtCompany"].tolist()))
