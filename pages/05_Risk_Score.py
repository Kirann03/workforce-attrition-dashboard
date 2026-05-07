import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder
except ModuleNotFoundError:
    GradientBoostingClassifier = None
    LabelEncoder = None

from utils.charts import RISK_COLORS, polish
from utils.data_loader import load_data
from utils.theme import apply_theme, page_header, render_sidebar


st.set_page_config(page_title="Attrition Risk Score", layout="wide")
apply_theme()
render_sidebar()
page_header(
    "Predictive Retention Signal",
    "Attrition Risk Scoring Engine",
    "Estimate attrition probability with a Gradient Boosting model, segment employees into risk tiers, and surface the strongest retention drivers.",
    ["ML risk score", "Feature importance", "High-risk segments"],
)

df = load_data()

if GradientBoostingClassifier is None or LabelEncoder is None:
    st.error("scikit-learn is required for this page. Install it with `pip install -r requirements.txt`.")
    st.stop()


@st.cache_resource
def train_model(data):
    feature_cols = [
        "Age",
        "MonthlyIncome",
        "YearsAtCompany",
        "TotalWorkingYears",
        "JobSatisfaction",
        "EnvironmentSatisfaction",
        "WorkLifeBalance",
        "JobInvolvement",
        "JobLevel",
        "OverTime",
        "BusinessTravel",
        "YearsSinceLastPromotion",
        "NumCompaniesWorked",
        "DistanceFromHome",
        "StockOptionLevel",
        "Department",
        "MaritalStatus",
    ]
    df_ml = data[feature_cols + ["Attrition"]].copy()

    le_dict = {}
    for col in ["OverTime", "BusinessTravel", "Department", "MaritalStatus"]:
        le = LabelEncoder()
        df_ml[col] = le.fit_transform(df_ml[col])
        le_dict[col] = le

    X = df_ml[feature_cols]
    y = df_ml["Attrition"]
    model = GradientBoostingClassifier(n_estimators=150, max_depth=4, random_state=42)
    model.fit(X, y)
    return model, feature_cols, le_dict


with st.spinner("Training risk model..."):
    model, feature_cols, le_dict = train_model(df)

scored_df = df.copy()
model_df = scored_df.copy()
for col, le in le_dict.items():
    model_df[col] = le.transform(model_df[col])

scored_df["RiskScore"] = (model.predict_proba(model_df[feature_cols])[:, 1] * 100).round(1)
scored_df["RiskTier"] = pd.cut(
    scored_df["RiskScore"],
    bins=[-0.1, 30, 60, 100],
    labels=["Low", "Medium", "High"],
)

k1, k2, k3 = st.columns(3)
k1.metric("High Risk Employees", f"{(scored_df['RiskTier'] == 'High').sum():,}")
k2.metric("Medium Risk Employees", f"{(scored_df['RiskTier'] == 'Medium').sum():,}")
k3.metric("Low Risk Employees", f"{(scored_df['RiskTier'] == 'Low').sum():,}")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Risk Score Distribution")
    fig = px.histogram(
        scored_df,
        x="RiskScore",
        color="RiskTier",
        nbins=30,
        color_discrete_map=RISK_COLORS,
    )
    polish(fig, 360)
    fig.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Risk Tier by Department")
    rt = scored_df.groupby(["Department", "RiskTier"], observed=False).size().reset_index(name="Count")
    fig = px.bar(
        rt,
        x="Department",
        y="Count",
        color="RiskTier",
        barmode="stack",
        color_discrete_map=RISK_COLORS,
    )
    polish(fig, 360)
    fig.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Top Attrition Risk Drivers (Feature Importance)")
fi = pd.DataFrame({"Feature": feature_cols, "Importance": model.feature_importances_})
fi = fi.sort_values("Importance", ascending=True).tail(12)
fig = px.bar(
    fi,
    y="Feature",
    x="Importance",
    orientation="h",
    color="Importance",
    color_continuous_scale="RdYlGn_r",
)
polish(fig, 420)
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("High-Risk Employee Segments")
high_risk = scored_df[scored_df["RiskTier"] == "High"][
    ["Department", "JobRole", "Age", "YearsAtCompany", "MonthlyIncome", "OverTime", "RiskScore"]
].sort_values("RiskScore", ascending=False)
st.dataframe(high_risk.reset_index(drop=True), use_container_width=True)
