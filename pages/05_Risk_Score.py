import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import OrdinalEncoder
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
from utils.theme import apply_theme, chart_caption, data_quality_banner, download_filtered_data, insight_card, page_header, render_global_filters, render_sidebar, section_divider


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


def _feature_label(feature: str) -> str:
    """Return a display label for raw and encoded model features."""
    if feature in ML_FEATURE_LABELS:
        return ML_FEATURE_LABELS[feature]
    if feature.startswith("MaritalStatus_"):
        return "Marital Status: " + feature.replace("MaritalStatus_", "")
    return feature.replace("_", " ")


def _encode_for_model(df_ml: pd.DataFrame, encoding_info: dict) -> pd.DataFrame:
    """Apply the same encoding used during model training."""
    df_enc = df_ml.copy()
    df_enc["BusinessTravel"] = encoding_info["travel_enc"].transform(
        df_enc[["BusinessTravel"]]
    ).astype(int)
    df_enc["OverTime"] = (df_enc["OverTime"] == "Yes").astype(int)
    df_enc = pd.get_dummies(df_enc, columns=["MaritalStatus"], drop_first=True, dtype=int)
    for col in encoding_info["marital_dummies"]:
        if col not in df_enc.columns:
            df_enc[col] = 0
    df_enc["Department"] = df_enc["Department"].map(encoding_info["dept_map"])
    return df_enc[encoding_info["feature_cols_encoded"]]


def find_optimal_threshold(model: GradientBoostingClassifier, X: pd.DataFrame, y: pd.Series) -> float:
    """Find the probability threshold that maximises F1 for the minority class."""
    probs = model.predict_proba(X)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y, probs)
    f1_scores = 2 * precisions * recalls / (precisions + recalls + 1e-9)
    best_idx = int(np.argmax(f1_scores[:-1]))
    return float(thresholds[best_idx])


@st.cache_resource
def train_model(data: pd.DataFrame) -> tuple[GradientBoostingClassifier, list[str], dict, float]:
    feature_cols = list(ML_FEATURE_LABELS.keys())
    df_ml = data[feature_cols + ["Attrition"]].copy()

    travel_enc = OrdinalEncoder(categories=[["Non-Travel", "Travel_Rarely", "Travel_Frequently"]])
    df_ml["BusinessTravel"] = travel_enc.fit_transform(df_ml[["BusinessTravel"]]).astype(int)
    df_ml["OverTime"] = (df_ml["OverTime"] == "Yes").astype(int)
    df_ml = pd.get_dummies(df_ml, columns=["MaritalStatus"], drop_first=True, dtype=int)
    dept_map = {"Human Resources": 0, "Research & Development": 1, "Sales": 2}
    df_ml["Department"] = df_ml["Department"].map(dept_map)
    feature_cols_encoded = [col for col in df_ml.columns if col != "Attrition"]

    X = df_ml[feature_cols_encoded]
    y = df_ml["Attrition"]
    sample_weight = compute_sample_weight(class_weight="balanced", y=y)
    model = GradientBoostingClassifier(
        n_estimators=MODEL_N_ESTIMATORS,
        max_depth=MODEL_MAX_DEPTH,
        random_state=MODEL_RANDOM_STATE,
    )
    model.fit(X, y, sample_weight=sample_weight)
    optimal_threshold = find_optimal_threshold(model, X, y)
    encoding_info = {
        "travel_enc": travel_enc,
        "dept_map": dept_map,
        "marital_dummies": [col for col in feature_cols_encoded if col.startswith("MaritalStatus_")],
        "feature_cols_encoded": feature_cols_encoded,
    }
    return model, feature_cols, encoding_info, optimal_threshold


@st.cache_data
def model_performance(data: pd.DataFrame) -> dict[str, float]:
    model, feature_cols, encoding_info, optimal_threshold = train_model(data)
    df_ml = data[feature_cols + ["Attrition"]].copy()
    X = _encode_for_model(df_ml[feature_cols], encoding_info)
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
    preds = (probs >= optimal_threshold).astype(int)
    return {
        "auc": roc_auc_score(y, probs),
        "precision": precision_score(y, preds, zero_division=0),
        "recall": recall_score(y, preds, zero_division=0),
        "f1": f1_score(y, preds, zero_division=0),
        "threshold": optimal_threshold,
    }


with st.spinner("Training risk model..."):
    model, feature_cols, encoding_info, optimal_threshold = train_model(df)

X_all = _encode_for_model(df[feature_cols], encoding_info)

scored_df = df.copy()
scored_probs = model.predict_proba(X_all)[:, 1]
scored_df["RiskScore"] = (scored_probs * 100).round(1)
scored_df["RiskTier"] = pd.cut(
    scored_df["RiskScore"],
    bins=[-0.1, RISK_SCORE_MEDIUM, RISK_SCORE_HIGH, 100],
    labels=["Low", "Medium", "High"],
)

filtered_scored = render_global_filters(scored_df)
risk_tiers = ["High", "Medium", "Low"]
selected_tiers = st.sidebar.multiselect("Risk Tier", risk_tiers, default=risk_tiers)
filtered_scored = filtered_scored[filtered_scored["RiskTier"].astype(str).isin(selected_tiers)]

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
    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1])
    m1.metric("AUC-ROC", f"{perf['auc']:.3f}")
    m2.metric("Precision", f"{perf['precision']:.3f}")
    m3.metric("Recall", f"{perf['recall']:.3f}")
    m4.metric("F1 Score", f"{perf['f1']:.3f}")
    m5.metric(
        "Decision Threshold",
        f"{perf['threshold']:.2f}",
        help="Optimised for F1 on the minority attrition class. Default 0.5 under-detects attrition risk.",
    )
    fpr, tpr, _ = roc_curve(df["Attrition"], scored_probs)
    roc_fig = go.Figure()
    roc_fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"AUC = {perf['auc']:.3f}", line=dict(color=DEEP_NAVY, width=3)))
    roc_fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random", line=dict(color="#C0CDD8", dash="dash")))
    roc_fig.update_layout(xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    polish(roc_fig, 380, title="ROC Curve")
    st.plotly_chart(roc_fig, use_container_width=True)

with st.expander("Risk Tier Calibration Validation"):
    tier_val = scored_df.copy()
    tier_val["RiskTier"] = pd.cut(
        tier_val["RiskScore"],
        bins=[-0.1, RISK_SCORE_MEDIUM, RISK_SCORE_HIGH, 100],
        labels=["Low", "Medium", "High"],
    )
    cal_df = tier_val.groupby("RiskTier", observed=False).agg(
        Count=("Attrition", "count"),
        Actual_Exits=("Attrition", "sum"),
    ).reset_index()
    cal_df["Actual_Attrition_%"] = (cal_df["Actual_Exits"] / cal_df["Count"] * 100).round(1)
    st.dataframe(cal_df, use_container_width=True, hide_index=True)
    st.caption(
        "Validation: each Risk Tier's actual attrition rate confirms threshold behavior. "
        "High tier should show substantially higher attrition than the 16.1% baseline."
    )

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
feature_cols_encoded = encoding_info["feature_cols_encoded"]
fi = pd.DataFrame({"Feature": feature_cols_encoded, "Importance": model.feature_importances_})
fi["Importance (%)"] = (fi["Importance"] / fi["Importance"].sum() * 100).round(2)
fi["Feature Label"] = fi["Feature"].map(_feature_label)
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
top_raw_features = pd.DataFrame({"Feature": feature_cols_encoded, "Importance": model.feature_importances_}).sort_values("Importance", ascending=False)["Feature"].head(3)
intervention_rows = []
for tier in ["High", "Medium"]:
    for feature in top_raw_features:
        raw_feature = feature.split("_", 1)[0] if feature.startswith("MaritalStatus_") else feature
        intervention_rows.append(
            {
                "Risk Tier": tier,
                "Risk Driver": _feature_label(feature),
                "Recommended Intervention": INTERVENTION_MAP.get(raw_feature, "Review manager-level retention plan and employee experience signals"),
            }
        )
st.dataframe(pd.DataFrame(intervention_rows), use_container_width=True, hide_index=True)

section_divider("High-Risk Segments")
st.subheader("High-Risk Employee Segments")
means = X_all.mean()
importances = pd.Series(model.feature_importances_, index=feature_cols_encoded)
driver_scores = (X_all - means).abs().mul(importances, axis=1)
scored_df["Primary Risk Factor"] = driver_scores.idxmax(axis=1).map(_feature_label)
filtered_scored = scored_df.loc[filtered_scored.index].copy()
filtered_scored["Primary Risk Factor"] = scored_df.loc[filtered_scored.index, "Primary Risk Factor"]
high_risk = filtered_scored[filtered_scored["RiskTier"] == "High"][
    ["Department", "JobRole", "Age", "YearsAtCompany", "MonthlyIncome", "OverTime", "RiskScore", "Primary Risk Factor"]
].sort_values("RiskScore", ascending=False)
st.dataframe(high_risk.reset_index(drop=True), use_container_width=True)

download_filtered_data(filtered_scored, "risk_scored_filtered_data.csv")
