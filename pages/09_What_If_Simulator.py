import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import DEEP_NAVY, RATE_SCALE, gauge_chart, polish
from utils.config import INTERVENTION_MAP, ML_FEATURE_LABELS, RISK_SCORE_HIGH, RISK_SCORE_MEDIUM
from utils.data_loader import load_data
from utils.ml import encode_df, ensemble_prob, feature_label, train_ensemble
from utils.theme import apply_theme, data_quality_banner, insight_card, page_header, render_sidebar, section_divider


st.set_page_config(page_title="What-If Attrition Simulator", page_icon="🎛", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)
page_header(
    "Scenario Planning",
    "What-If Attrition Simulator",
    "Adjust an employee profile to see how each factor shifts predicted attrition risk.",
    ["Live risk score", "Profile drivers", "Intervention planning"],
)

gb, rf, lr, feature_cols, encoding_info, _ = train_ensemble(df)
x_all = encode_df(df[feature_cols], encoding_info)
baseline_means = x_all.mean()
importances = pd.Series(gb.feature_importances_, index=encoding_info["feature_cols_encoded"])

scored = df.copy()
scored["RiskScore"] = (ensemble_prob(gb, rf, lr, x_all.values) * 100).round(1)
scored["RiskTier"] = pd.cut(
    scored["RiskScore"],
    bins=[-0.1, RISK_SCORE_MEDIUM, RISK_SCORE_HIGH, 100],
    labels=["Low", "Medium", "High"],
)

avg_profile = {col: df[col].mean() if pd.api.types.is_numeric_dtype(df[col]) else df[col].mode().iloc[0] for col in feature_cols}
high_risk = scored[scored["RiskTier"] == "High"]
high_profile = {
    col: high_risk[col].median() if pd.api.types.is_numeric_dtype(df[col]) and not high_risk.empty else avg_profile[col]
    for col in feature_cols
}
for col in feature_cols:
    if not pd.api.types.is_numeric_dtype(df[col]):
        high_profile[col] = high_risk[col].mode().iloc[0] if not high_risk.empty else avg_profile[col]


def set_profile(prefix: str, profile: dict) -> None:
    for feature, value in profile.items():
        st.session_state[f"{prefix}_{feature}"] = int(round(value)) if pd.api.types.is_numeric_dtype(df[feature]) else value


btn1, btn2 = st.columns([1, 1])
with btn1:
    if st.button("Reset to Company Average", use_container_width=True):
        set_profile("sim", avg_profile)
        st.rerun()
with btn2:
    if st.button("Compare with High-Risk Profile", use_container_width=True):
        set_profile("sim", high_profile)
        st.rerun()

left, right = st.columns([0.95, 1.25])
profile = {}
with left:
    st.subheader("Employee Profile Inputs")
    for feature in feature_cols:
        key = f"sim_{feature}"
        label = ML_FEATURE_LABELS[feature]
        if pd.api.types.is_numeric_dtype(df[feature]):
            min_v = int(df[feature].min())
            max_v = int(df[feature].max())
            default = int(round(st.session_state.get(key, avg_profile[feature])))
            profile[feature] = st.slider(label, min_v, max_v, value=max(min_v, min(default, max_v)), key=key)
        else:
            options = sorted(df[feature].dropna().astype(str).unique())
            default = str(st.session_state.get(key, avg_profile[feature]))
            profile[feature] = st.selectbox(label, options, index=options.index(default) if default in options else 0, key=key)

profile_df = pd.DataFrame([profile])
encoded = encode_df(profile_df[feature_cols], encoding_info)
risk_score = float(ensemble_prob(gb, rf, lr, encoded.values)[0] * 100)
risk_tier = "High" if risk_score >= RISK_SCORE_HIGH else ("Medium" if risk_score >= RISK_SCORE_MEDIUM else "Low")
contrib = (encoded.iloc[0] - baseline_means).abs().mul(importances).sort_values(ascending=False).head(5)
top_driver = contrib.index[0]
raw_driver = top_driver.split("_", 1)[0] if top_driver.startswith("MaritalStatus_") else top_driver

with right:
    st.subheader("Live Risk Output")
    fig = gauge_chart(risk_score, "Predicted Attrition Risk")
    st.plotly_chart(fig, use_container_width=True)
    c1, c2 = st.columns(2)
    c1.metric("Risk Score", f"{risk_score:.1f}/100")
    c2.metric("Risk Tier", risk_tier)

    drivers = pd.DataFrame({"Risk Driver": [feature_label(idx) for idx in contrib.index], "Contribution": contrib.values})
    fig = px.bar(drivers, x="Contribution", y="Risk Driver", orientation="h", color="Contribution", color_continuous_scale=RATE_SCALE)
    polish(fig, 340, title="Top 5 Scenario Risk Drivers")
    fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    insight_card("Recommended Intervention", INTERVENTION_MAP.get(raw_driver, "Review manager-level retention plan and employee experience signals"))

section_divider("Current Profile vs Company Average")
comparison_features = ["Age", "MonthlyIncome", "YearsAtCompany", "TotalWorkingYears", "DistanceFromHome", "PercentSalaryHike"]
comparison = pd.DataFrame(
    {
        "Feature": [ML_FEATURE_LABELS[col] for col in comparison_features],
        "Current Profile": [profile[col] for col in comparison_features],
        "Company Average": [round(float(df[col].mean()), 1) for col in comparison_features],
    }
)
st.dataframe(comparison, use_container_width=True, hide_index=True)
