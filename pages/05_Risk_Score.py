import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight

from utils.charts import DEEP_NAVY, RATE_SCALE, RISK_COLORS, polish
from utils.config import (
    INTERVENTION_MAP,
    ML_FEATURE_LABELS,
    MODEL_MAX_DEPTH,
    MODEL_N_ESTIMATORS,
    MODEL_RANDOM_STATE,
    RISK_SCORE_HIGH,
    RISK_SCORE_MEDIUM,
)
from utils.data_loader import load_data
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, insight_card, page_header, render_sidebar, section_divider


st.set_page_config(page_title="Attrition Risk Score", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)

page_header(
    "Predictive Retention Signal",
    "Attrition Risk Scoring Engine",
    "Estimate attrition probability with a balanced Gradient Boosting model, segment employees into risk tiers, and surface action-oriented retention drivers.",
    ["ML risk score", "Model performance", "Feature importance", "Intervention matrix"],
)


@st.cache_resource
def train_model(data):
    feature_cols = list(ML_FEATURE_LABELS.keys())
    df_ml = data[feature_cols + ["Attrition"]].copy()
    le_dict = {}
    for col in ["OverTime", "BusinessTravel", "Department", "MaritalStatus"]:
        le = LabelEncoder()
        df_ml[col] = le.fit_transform(df_ml[col])
        le_dict[col] = le
    X = df_ml[feature_cols]
    y = df_ml["Attrition"]
    sample_weight = compute_sample_weight(class_weight="balanced", y=y)
    model = GradientBoostingClassifier(
        n_estimators=MODEL_N_ESTIMATORS,
        max_depth=MODEL_MAX_DEPTH,
        random_state=MODEL_RANDOM_STATE,
    )
    model.fit(X, y, sample_weight=sample_weight)
    return model, feature_cols, le_dict


@st.cache_data
def model_performance(data):
    model, feature_cols, le_dict = train_model(data)
    df_ml = data[feature_cols + ["Attrition"]].copy()
    for col, le in le_dict.items():
        df_ml[col] = le.transform(df_ml[col])
    X = df_ml[feature_cols]
    y = df_ml["Attrition"]
    sample_weight = compute_sample_weight(class_weight="balanced", y=y)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=MODEL_RANDOM_STATE)
    cv_model = GradientBoostingClassifier(
        n_estimators=MODEL_N_ESTIMATORS,
        max_depth=MODEL_MAX_DEPTH,
        random_state=MODEL_RANDOM_STATE,
    )
    probs = cross_val_predict(
        cv_model,
        X,
        y,
        cv=cv,
        method="predict_proba",
        params={"sample_weight": sample_weight},
    )[:, 1]
    preds = (probs >= 0.5).astype(int)
    return {
        "auc": roc_auc_score(y, probs),
        "precision": precision_score(y, preds, zero_division=0),
        "recall": recall_score(y, preds, zero_division=0),
        "f1": f1_score(y, preds, zero_division=0),
    }


with st.spinner("Training risk model..."):
    model, feature_cols, le_dict = train_model(df)

model_df = df.copy()
for col, le in le_dict.items():
    model_df[col] = le.transform(model_df[col])

scored_df = df.copy()
scored_df["RiskScore"] = (model.predict_proba(model_df[feature_cols])[:, 1] * 100).round(1)
scored_df["RiskTier"] = pd.cut(
    scored_df["RiskScore"],
    bins=[-0.1, RISK_SCORE_MEDIUM, RISK_SCORE_HIGH, 100],
    labels=["Low", "Medium", "High"],
)

st.sidebar.header("Workforce Filters")
departments = sorted(scored_df["Department"].dropna().unique().tolist())
selected_depts = st.sidebar.multiselect("Department", departments, default=departments)
roles = sorted(scored_df[scored_df["Department"].isin(selected_depts)]["JobRole"].dropna().unique().tolist())
selected_roles = st.sidebar.multiselect("Job Role", roles, default=roles)
risk_tiers = ["High", "Medium", "Low"]
selected_tiers = st.sidebar.multiselect("Risk Tier", risk_tiers, default=risk_tiers)
filtered_scored = scored_df[
    scored_df["Department"].isin(selected_depts)
    & scored_df["JobRole"].isin(selected_roles)
    & scored_df["RiskTier"].astype(str).isin(selected_tiers)
]
st.sidebar.metric("Filtered Records", len(filtered_scored))

if filtered_scored.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

k1, k2, k3 = st.columns([1, 1, 1])
k1.metric("High Risk Employees", f"{(filtered_scored['RiskTier'] == 'High').sum():,}")
k2.metric("Medium Risk Employees", f"{(filtered_scored['RiskTier'] == 'Medium').sum():,}")
k3.metric("Low Risk Employees", f"{(filtered_scored['RiskTier'] == 'Low').sum():,}")

section_divider("Model Performance Deep Dive")
with st.expander("Model Performance & ROC Curve", expanded=True):
    perf = model_performance(df)
    m1, m2, m3, m4 = st.columns([1, 1, 1, 1])
    m1.metric("AUC-ROC", f"{perf['auc']:.3f}")
    m2.metric("Precision", f"{perf['precision']:.3f}")
    m3.metric("Recall", f"{perf['recall']:.3f}")
    m4.metric("F1 Score", f"{perf['f1']:.3f}")
    fpr, tpr, _ = roc_curve(df["Attrition"], model.predict_proba(model_df[feature_cols])[:, 1])
    roc_fig = go.Figure()
    roc_fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"AUC = {perf['auc']:.3f}", line=dict(color=DEEP_NAVY, width=3)))
    roc_fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random", line=dict(color="#C0CDD8", dash="dash")))
    roc_fig.update_layout(xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    polish(roc_fig, 380, title="ROC Curve")
    st.plotly_chart(roc_fig, use_container_width=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Risk Score Distribution")
    fig = px.histogram(filtered_scored, x="RiskScore", color="RiskTier", nbins=30, color_discrete_map=RISK_COLORS)
    polish(fig, 360, title="Risk Score Distribution")
    fig.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(filtered_scored))

with col2:
    st.subheader("Risk Tier by Department")
    rt = filtered_scored.groupby(["Department", "RiskTier"], observed=False).size().reset_index(name="Count")
    fig = px.bar(rt, x="Department", y="Count", color="RiskTier", barmode="stack", color_discrete_map=RISK_COLORS)
    polish(fig, 360, title="Risk Tier by Department")
    fig.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(filtered_scored))

section_divider("Risk Score Distribution by Segment")
rs_col1, rs_col2 = st.columns([1, 1])
with rs_col1:
    fig = px.box(
        filtered_scored,
        x="JobLevelLabel",
        y="RiskScore",
        color="RiskTier",
        color_discrete_map=RISK_COLORS,
        labels={"JobLevelLabel": "Job Level", "RiskScore": "Risk Score (0-100)"},
    )
    polish(fig, 380, title="Risk Score by Job Level")
    fig.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(filtered_scored))

with rs_col2:
    fig = px.violin(
        filtered_scored,
        x="Department",
        y="RiskScore",
        color="RiskTier",
        color_discrete_map=RISK_COLORS,
        box=True,
        points=False,
        labels={"RiskScore": "Risk Score (0-100)"},
    )
    polish(fig, 380, title="Risk Score Distribution by Department")
    fig.update_layout(legend_title="Risk Tier")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(filtered_scored))

section_divider("Risk Drivers & Interventions")
st.subheader("Ranked Attrition Risk Drivers")
fi = pd.DataFrame({"Feature": feature_cols, "Importance": model.feature_importances_})
fi["Importance (%)"] = (fi["Importance"] / fi["Importance"].sum() * 100).round(2)
fi["Feature Label"] = fi["Feature"].map(ML_FEATURE_LABELS)
fi = fi.sort_values("Importance (%)", ascending=False).reset_index(drop=True)
fi.insert(0, "Rank", fi.index + 1)
feat_col1, feat_col2 = st.columns([1, 1])
with feat_col1:
    st.dataframe(
        fi[["Rank", "Feature Label", "Importance (%)"]].rename(columns={"Feature Label": "Driver"}),
        use_container_width=True,
        hide_index=True,
    )
with feat_col2:
    fig = px.bar(
        fi.head(10),
        y="Feature Label",
        x="Importance (%)",
        orientation="h",
        color="Importance (%)",
        color_continuous_scale=RATE_SCALE,
    )
    polish(fig, 360, title="Top 10 Risk Drivers")
    fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
insight_card("Model Driver Summary", "The ranked drivers combine model importance with workforce context so HR can prioritize interventions against the strongest attrition signals.")

st.subheader("Retention Intervention Matrix")
top_raw_features = pd.DataFrame({"Feature": feature_cols, "Importance": model.feature_importances_}).sort_values("Importance", ascending=False)["Feature"].head(3)
intervention_rows = []
for tier in ["High", "Medium"]:
    for feature in top_raw_features:
        intervention_rows.append(
            {
                "Risk Tier": tier,
                "Risk Driver": ML_FEATURE_LABELS.get(feature, feature),
                "Recommended Intervention": INTERVENTION_MAP.get(feature, "Review manager-level retention plan and employee experience signals"),
            }
        )
st.dataframe(pd.DataFrame(intervention_rows), use_container_width=True, hide_index=True)

section_divider("High-Risk Segments")
st.subheader("High-Risk Employee Segments")
means = model_df[feature_cols].mean()
importances = pd.Series(model.feature_importances_, index=feature_cols)
driver_scores = (model_df[feature_cols] - means).abs().mul(importances, axis=1)
scored_df["Primary Risk Factor"] = driver_scores.idxmax(axis=1).map(ML_FEATURE_LABELS)
filtered_scored = scored_df.loc[filtered_scored.index].copy()
filtered_scored["Primary Risk Factor"] = scored_df.loc[filtered_scored.index, "Primary Risk Factor"]
high_risk = filtered_scored[filtered_scored["RiskTier"] == "High"][
    ["Department", "JobRole", "Age", "YearsAtCompany", "MonthlyIncome", "OverTime", "RiskScore", "Primary Risk Factor"]
].sort_values("RiskScore", ascending=False)
st.dataframe(high_risk.reset_index(drop=True), use_container_width=True)

download_filtered_data(filtered_scored, "risk_scored_filtered_data.csv")
