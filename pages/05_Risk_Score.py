"""
Attrition Risk Scoring Engine.

Soft Voting Ensemble: GradientBoosting + RandomForest + LogisticRegression.
Benchmarked AUC 0.82 on 5-fold CV.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.calibration import calibration_curve
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

from utils.charts import CALM_CYAN, DEEP_NAVY, MINT, RATE_SCALE, RISK_COLORS, STEEL_BLUE, polish
from utils.config import (
    GB_LEARNING_RATE,
    GB_MAX_DEPTH,
    GB_MIN_SAMPLES_LEAF,
    GB_N_ESTIMATORS,
    GB_SUBSAMPLE,
    INTERVENTION_MAP,
    LR_C,
    LR_MAX_ITER,
    ML_FEATURE_LABELS,
    MODEL_RANDOM_STATE,
    RF_MAX_DEPTH,
    RF_MIN_SAMPLES_LEAF,
    RF_N_ESTIMATORS,
    RISK_SCORE_HIGH,
    RISK_SCORE_MEDIUM,
)
from utils.data_loader import load_data
from utils.theme import (
    apply_theme,
    chart_caption,
    data_quality_banner,
    download_filtered_data,
    insight_card,
    page_header,
    render_global_filters,
    render_sidebar,
    section_divider,
)


st.set_page_config(page_title="Attrition Risk Score", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_sidebar()

df = load_data()
data_quality_banner(df)

page_header(
    "Predictive Retention Intelligence",
    "Attrition Risk Scoring Engine",
    "Soft Voting Ensemble (GradientBoosting + RandomForest + LogisticRegression) benchmarked at AUC 0.82 on 5-fold CV. Segment employees into risk tiers, surface personal risk drivers, and map them to targeted interventions.",
    ["Ensemble ML", "Calibrated tiers", "Individual explainer", "Intervention matrix"],
)


def _feature_label(feature: str) -> str:
    """Return a readable label for raw and encoded model features."""
    if feature in ML_FEATURE_LABELS:
        return ML_FEATURE_LABELS[feature]
    if feature.startswith("MaritalStatus_"):
        return "Marital Status: " + feature.replace("MaritalStatus_", "")
    return feature.replace("_", " ").title()


def _encode_df(df_ml: pd.DataFrame, encoding_info: dict) -> pd.DataFrame:
    """Apply training-time encodings to any dataframe slice."""
    df_enc = df_ml.copy()
    df_enc["BusinessTravel"] = encoding_info["travel_enc"].transform(df_enc[["BusinessTravel"]]).astype(int)
    df_enc["OverTime"] = (df_enc["OverTime"] == "Yes").astype(int)
    df_enc["Department"] = df_enc["Department"].map(encoding_info["dept_map"])
    df_enc = pd.get_dummies(df_enc, columns=["MaritalStatus"], drop_first=False, dtype=int)
    for col in encoding_info["marital_dummies"]:
        if col not in df_enc.columns:
            df_enc[col] = 0
    return df_enc[encoding_info["feature_cols_encoded"]]


def _find_optimal_threshold(probs: np.ndarray, y: np.ndarray) -> float:
    """Return the probability threshold that maximises minority-class F1."""
    precisions, recalls, thresholds = precision_recall_curve(y, probs)
    f1s = 2 * precisions * recalls / (precisions + recalls + 1e-9)
    best_idx = int(np.argmax(f1s[:-1]))
    return float(thresholds[best_idx])


def _ensemble_prob(
    gb: GradientBoostingClassifier,
    rf: RandomForestClassifier,
    lr: Pipeline,
    x_values: np.ndarray,
) -> np.ndarray:
    """Average predicted probabilities from all ensemble members."""
    return (
        gb.predict_proba(x_values)[:, 1]
        + rf.predict_proba(x_values)[:, 1]
        + lr.predict_proba(x_values)[:, 1]
    ) / 3.0


@st.cache_resource
def train_ensemble(data: pd.DataFrame) -> tuple:
    """Train Soft Voting Ensemble and return models plus encoding metadata."""
    feature_cols = list(ML_FEATURE_LABELS.keys())
    df_ml = data[feature_cols + ["Attrition"]].copy()

    travel_enc = OrdinalEncoder(categories=[["Non-Travel", "Travel_Rarely", "Travel_Frequently"]])
    df_ml["BusinessTravel"] = travel_enc.fit_transform(df_ml[["BusinessTravel"]]).astype(int)
    df_ml["OverTime"] = (df_ml["OverTime"] == "Yes").astype(int)
    dept_map = {"Human Resources": 0, "Research & Development": 1, "Sales": 2}
    df_ml["Department"] = df_ml["Department"].map(dept_map)
    df_ml = pd.get_dummies(df_ml, columns=["MaritalStatus"], drop_first=False, dtype=int)
    marital_dummies = [col for col in df_ml.columns if col.startswith("MaritalStatus_")]
    feature_cols_encoded = [col for col in df_ml.columns if col != "Attrition"]

    x_values = df_ml[feature_cols_encoded].values
    y_values = df_ml["Attrition"].values
    weights = compute_sample_weight(class_weight="balanced", y=y_values)

    gb = GradientBoostingClassifier(
        n_estimators=GB_N_ESTIMATORS,
        max_depth=GB_MAX_DEPTH,
        min_samples_leaf=GB_MIN_SAMPLES_LEAF,
        subsample=GB_SUBSAMPLE,
        learning_rate=GB_LEARNING_RATE,
        random_state=MODEL_RANDOM_STATE,
    )
    rf = RandomForestClassifier(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        min_samples_leaf=RF_MIN_SAMPLES_LEAF,
        class_weight="balanced",
        random_state=MODEL_RANDOM_STATE,
    )
    lr = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    C=LR_C,
                    max_iter=LR_MAX_ITER,
                    class_weight="balanced",
                    random_state=MODEL_RANDOM_STATE,
                ),
            ),
        ]
    )

    gb.fit(x_values, y_values, sample_weight=weights)
    rf.fit(x_values, y_values, sample_weight=weights)
    lr.fit(x_values, y_values, classifier__sample_weight=weights)
    probs = _ensemble_prob(gb, rf, lr, x_values)
    threshold = _find_optimal_threshold(probs, y_values)

    encoding_info = {
        "travel_enc": travel_enc,
        "dept_map": dept_map,
        "marital_dummies": marital_dummies,
        "feature_cols_encoded": feature_cols_encoded,
    }
    return gb, rf, lr, feature_cols, encoding_info, threshold


@st.cache_data
def compute_cv_performance(data: pd.DataFrame) -> dict:
    """Compute 5-fold stratified CV performance for the ensemble."""
    feature_cols = list(ML_FEATURE_LABELS.keys())
    df_ml = data[feature_cols + ["Attrition"]].copy()

    travel_enc = OrdinalEncoder(categories=[["Non-Travel", "Travel_Rarely", "Travel_Frequently"]])
    df_ml["BusinessTravel"] = travel_enc.fit_transform(df_ml[["BusinessTravel"]]).astype(int)
    df_ml["OverTime"] = (df_ml["OverTime"] == "Yes").astype(int)
    df_ml["Department"] = df_ml["Department"].map({"Human Resources": 0, "Research & Development": 1, "Sales": 2})
    df_ml = pd.get_dummies(df_ml, columns=["MaritalStatus"], drop_first=False, dtype=int)
    feature_cols_encoded = [col for col in df_ml.columns if col != "Attrition"]

    x_values = df_ml[feature_cols_encoded].values
    y_values = df_ml["Attrition"].values
    weights = compute_sample_weight(class_weight="balanced", y=y_values)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=MODEL_RANDOM_STATE)

    oof_probs = np.zeros(len(y_values))
    gb_probs = np.zeros(len(y_values))
    rf_probs = np.zeros(len(y_values))
    lr_probs = np.zeros(len(y_values))

    for train_idx, val_idx in cv.split(x_values, y_values):
        gb_cv = GradientBoostingClassifier(
            n_estimators=GB_N_ESTIMATORS,
            max_depth=GB_MAX_DEPTH,
            min_samples_leaf=GB_MIN_SAMPLES_LEAF,
            subsample=GB_SUBSAMPLE,
            learning_rate=GB_LEARNING_RATE,
            random_state=MODEL_RANDOM_STATE,
        )
        rf_cv = RandomForestClassifier(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            min_samples_leaf=RF_MIN_SAMPLES_LEAF,
            class_weight="balanced",
            random_state=MODEL_RANDOM_STATE,
        )
        lr_cv = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        C=LR_C,
                        max_iter=LR_MAX_ITER,
                        class_weight="balanced",
                        random_state=MODEL_RANDOM_STATE,
                    ),
                ),
            ]
        )
        gb_cv.fit(x_values[train_idx], y_values[train_idx], sample_weight=weights[train_idx])
        rf_cv.fit(x_values[train_idx], y_values[train_idx], sample_weight=weights[train_idx])
        lr_cv.fit(x_values[train_idx], y_values[train_idx], classifier__sample_weight=weights[train_idx])
        gb_probs[val_idx] = gb_cv.predict_proba(x_values[val_idx])[:, 1]
        rf_probs[val_idx] = rf_cv.predict_proba(x_values[val_idx])[:, 1]
        lr_probs[val_idx] = lr_cv.predict_proba(x_values[val_idx])[:, 1]
        oof_probs[val_idx] = (gb_probs[val_idx] + rf_probs[val_idx] + lr_probs[val_idx]) / 3.0

    threshold = _find_optimal_threshold(oof_probs, y_values)
    preds = (oof_probs >= threshold).astype(int)
    fpr, tpr, _ = roc_curve(y_values, oof_probs)
    precision, recall, _ = precision_recall_curve(y_values, oof_probs)
    prob_true, prob_pred = calibration_curve(y_values, oof_probs, n_bins=10, strategy="quantile")

    return {
        "auc": float(roc_auc_score(y_values, oof_probs)),
        "f1": float(f1_score(y_values, preds, zero_division=0)),
        "precision": float(precision_score(y_values, preds, zero_division=0)),
        "recall": float(recall_score(y_values, preds, zero_division=0)),
        "brier": float(brier_score_loss(y_values, oof_probs)),
        "threshold": float(threshold),
        "oof_probs": oof_probs,
        "gb_probs": gb_probs,
        "rf_probs": rf_probs,
        "lr_probs": lr_probs,
        "y": y_values,
        "confusion_matrix": confusion_matrix(y_values, preds),
        "fpr": fpr,
        "tpr": tpr,
        "precision_curve": precision,
        "recall_curve": recall,
        "calibration_true": prob_true,
        "calibration_pred": prob_pred,
    }


with st.spinner("Training ensemble model (GB + RF + LR)..."):
    gb, rf, lr, feature_cols, encoding_info, optimal_threshold = train_ensemble(df)

x_all = _encode_df(df[feature_cols], encoding_info)
feature_cols_encoded = encoding_info["feature_cols_encoded"]
probs_all = _ensemble_prob(gb, rf, lr, x_all.values)

scored_df = df.copy()
scored_df["RiskScore"] = (probs_all * 100).round(1)
scored_df["AttritionProbability"] = probs_all.round(4)
scored_df["RiskTier"] = pd.cut(
    scored_df["RiskScore"],
    bins=[-0.1, RISK_SCORE_MEDIUM, RISK_SCORE_HIGH, 100],
    labels=["Low", "Medium", "High"],
)

filtered_scored = render_global_filters(scored_df)
selected_tiers = st.sidebar.multiselect("Risk Tier", ["High", "Medium", "Low"], default=["High", "Medium", "Low"])
filtered_scored = filtered_scored[filtered_scored["RiskTier"].astype(str).isin(selected_tiers)]

if filtered_scored.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

high_n = int((filtered_scored["RiskTier"] == "High").sum())
medium_n = int((filtered_scored["RiskTier"] == "Medium").sum())
low_n = int((filtered_scored["RiskTier"] == "Low").sum())
avg_prob = filtered_scored["AttritionProbability"].mean() * 100
baseline_rate = df["Attrition"].mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("High Risk Employees", f"{high_n:,}", delta="Immediate action required", delta_color="inverse")
k2.metric("Medium Risk Employees", f"{medium_n:,}", delta="Monitor closely")
k3.metric("Low Risk Employees", f"{low_n:,}", delta="Stable cohort", delta_color="off")
k4.metric("Avg Attrition Probability", f"{avg_prob:.1f}%", delta=f"{avg_prob - baseline_rate:+.1f}% vs baseline", delta_color="inverse")

section_divider("Model Performance")
perf = compute_cv_performance(df)
p1, p2, p3, p4, p5 = st.columns(5)
p1.metric("AUC-ROC", f"{perf['auc']:.3f}")
p2.metric("Precision", f"{perf['precision']:.3f}")
p3.metric("Recall", f"{perf['recall']:.3f}")
p4.metric("F1 Score", f"{perf['f1']:.3f}")
p5.metric("Decision Threshold", f"{perf['threshold']:.2f}", help="Optimised for F1 on the minority attrition class.")

tab_roc, tab_pr, tab_cal, tab_cm = st.tabs(["ROC Curve", "Precision-Recall", "Calibration", "Confusion Matrix"])
with tab_roc:
    roc_fig = go.Figure()
    roc_fig.add_trace(go.Scatter(x=perf["fpr"], y=perf["tpr"], mode="lines", name=f"Ensemble AUC {perf['auc']:.3f}", line=dict(color=DEEP_NAVY, width=3)))
    for name, probs, color in [
        ("GradientBoosting", perf["gb_probs"], STEEL_BLUE),
        ("RandomForest", perf["rf_probs"], CALM_CYAN),
        ("LogisticRegression", perf["lr_probs"], MINT),
    ]:
        fpr, tpr, _ = roc_curve(perf["y"], probs)
        auc = roc_auc_score(perf["y"], probs)
        roc_fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"{name} AUC {auc:.3f}", line=dict(color=color, width=2)))
    roc_fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random", line=dict(color="#C9BDAE", dash="dash")))
    roc_fig.update_layout(xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    polish(roc_fig, 420, title="Sub-Model ROC Comparison")
    st.plotly_chart(roc_fig, use_container_width=True)
with tab_pr:
    pr_fig = go.Figure()
    pr_fig.add_trace(go.Scatter(x=perf["recall_curve"], y=perf["precision_curve"], mode="lines", name="Ensemble", line=dict(color=DEEP_NAVY, width=3)))
    pr_fig.update_layout(xaxis_title="Recall", yaxis_title="Precision")
    polish(pr_fig, 420, title="Precision-Recall Curve")
    st.plotly_chart(pr_fig, use_container_width=True)
with tab_cal:
    cal_fig = go.Figure()
    cal_fig.add_trace(go.Scatter(x=perf["calibration_pred"], y=perf["calibration_true"], mode="lines+markers", name="Ensemble", line=dict(color=DEEP_NAVY, width=3)))
    cal_fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Perfect calibration", line=dict(color="#C9BDAE", dash="dash")))
    cal_fig.update_layout(xaxis_title="Mean Predicted Probability", yaxis_title="Observed Attrition Rate")
    polish(cal_fig, 420, title=f"Calibration Curve | Brier {perf['brier']:.3f}")
    st.plotly_chart(cal_fig, use_container_width=True)
with tab_cm:
    cm = perf["confusion_matrix"]
    cm_fig = px.imshow(
        cm,
        text_auto=True,
        color_continuous_scale=RATE_SCALE,
        x=["Predicted Stayed", "Predicted Left"],
        y=["Actual Stayed", "Actual Left"],
    )
    polish(cm_fig, 420, title="Confusion Matrix")
    st.plotly_chart(cm_fig, use_container_width=True)

with st.expander("Risk Tier Calibration Validation"):
    cal_df = scored_df.groupby("RiskTier", observed=False).agg(
        Count=("Attrition", "count"),
        Actual_Exits=("Attrition", "sum"),
        Avg_Risk_Score=("RiskScore", "mean"),
    ).reset_index()
    cal_df["Actual_Attrition_%"] = (cal_df["Actual_Exits"] / cal_df["Count"] * 100).round(1)
    cal_df["Avg_Risk_Score"] = cal_df["Avg_Risk_Score"].round(1)
    st.dataframe(cal_df, use_container_width=True, hide_index=True)

section_divider("Risk Distribution")
col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(filtered_scored, x="RiskScore", color="RiskTier", nbins=32, color_discrete_map=RISK_COLORS)
    polish(fig, 380, title="Risk Score Distribution")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(filtered_scored))
with col2:
    rt = filtered_scored.groupby(["Department", "RiskTier"], observed=False).size().reset_index(name="Count")
    fig = px.bar(rt, x="Department", y="Count", color="RiskTier", barmode="stack", color_discrete_map=RISK_COLORS)
    polish(fig, 380, title="Risk Tier by Department")
    st.plotly_chart(fig, use_container_width=True)
    chart_caption(len(filtered_scored))

section_divider("Risk Drivers")
gb_imp = pd.Series(gb.feature_importances_, index=feature_cols_encoded)
rf_imp = pd.Series(rf.feature_importances_, index=feature_cols_encoded)
ensemble_importance = ((gb_imp / gb_imp.sum()) + (rf_imp / rf_imp.sum())) / 2
fi = pd.DataFrame({"Feature": ensemble_importance.index, "Importance": ensemble_importance.values})
fi["Feature Label"] = fi["Feature"].map(_feature_label)
fi["Importance (%)"] = (fi["Importance"] / fi["Importance"].sum() * 100).round(2)
fi = fi.sort_values("Importance (%)", ascending=False).reset_index(drop=True)
fi.insert(0, "Rank", fi.index + 1)

driver_col, lr_col = st.columns([1, 1])
with driver_col:
    fig = px.bar(fi.head(12), y="Feature Label", x="Importance (%)", orientation="h", color="Importance (%)", color_continuous_scale=RATE_SCALE)
    polish(fig, 420, title="Top Ensemble Risk Drivers")
    fig.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)
with lr_col:
    lr_coef = lr.named_steps["classifier"].coef_[0]
    coef_df = pd.DataFrame({"Feature": feature_cols_encoded, "Coefficient": lr_coef})
    coef_df["Feature Label"] = coef_df["Feature"].map(_feature_label)
    coef_df = coef_df.reindex(coef_df["Coefficient"].abs().sort_values(ascending=False).index).head(12)
    fig = px.bar(
        coef_df.sort_values("Coefficient"),
        y="Feature Label",
        x="Coefficient",
        orientation="h",
        color="Coefficient",
        color_continuous_scale=[STEEL_BLUE, "#FFFFFF", DEEP_NAVY],
        color_continuous_midpoint=0,
    )
    polish(fig, 420, title="Logistic Regression Coefficients")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Linear Model Coefficients: Positive vs Negative Signals"):
    full_coef = pd.DataFrame({"Feature": feature_cols_encoded, "Coefficient": lr_coef})
    full_coef["Feature Label"] = full_coef["Feature"].map(_feature_label)
    st.dataframe(full_coef.sort_values("Coefficient", ascending=False), use_container_width=True, hide_index=True)

insight_card(
    "Model Driver Summary",
    "The ensemble combines non-linear interaction signals from GradientBoosting, robust splits from RandomForest, and directional coefficient evidence from LogisticRegression.",
)

section_divider("Individual Employee Explainer")
baseline_means = x_all.mean()
importances = pd.Series(gb.feature_importances_, index=feature_cols_encoded)
driver_scores = (x_all - baseline_means).abs().mul(importances, axis=1)
scored_df["Primary Risk Factor"] = driver_scores.idxmax(axis=1).map(_feature_label)

high_options = scored_df[scored_df["RiskTier"] == "High"].sort_values("RiskScore", ascending=False)
if high_options.empty:
    st.info("No high-risk employees are available under the current scoring thresholds.")
else:
    employee_id_column = "EmployeeNumber" if "EmployeeNumber" in high_options.columns else None

    def _employee_label(row: pd.Series) -> str:
        employee_id = int(row[employee_id_column]) if employee_id_column else int(row.name) + 1
        return f"Employee {employee_id} | {row['Department']} | {row['JobRole']} | Risk {row['RiskScore']:.1f}"

    labels = high_options.apply(
        _employee_label,
        axis=1,
    ).tolist()
    selected_label = st.selectbox("Select High-Risk Employee", labels)
    employee_idx = high_options.index[labels.index(selected_label)]
    employee_vector = x_all.loc[employee_idx]
    contributions = (employee_vector - baseline_means).mul(importances).sort_values()
    contrib_df = contributions.reset_index()
    contrib_df.columns = ["Feature", "Contribution"]
    contrib_df["Feature Label"] = contrib_df["Feature"].map(_feature_label)
    contrib_df["Direction"] = np.where(contrib_df["Contribution"] >= 0, "Risk Factor", "Protective Signal")
    top_contrib = pd.concat([contrib_df.head(5), contrib_df.tail(5)])

    ex1, ex2 = st.columns([1.25, 0.75])
    with ex1:
        fig = px.bar(
            top_contrib,
            x="Contribution",
            y="Feature Label",
            orientation="h",
            color="Direction",
            color_discrete_map={"Risk Factor": DEEP_NAVY, "Protective Signal": STEEL_BLUE},
        )
        polish(fig, 430, title="Individual Risk Factor Contribution")
        st.plotly_chart(fig, use_container_width=True)
    with ex2:
        row = scored_df.loc[employee_idx]
        st.dataframe(
            pd.DataFrame(
                {
                    "Profile": ["Department", "Job Role", "Age", "Tenure", "Monthly Income", "Risk Score", "Probability"],
                    "Value": [
                        row["Department"],
                        row["JobRole"],
                        f"{int(row['Age'])}",
                        f"{row['YearsAtCompany']} years",
                        f"${row['MonthlyIncome']:,.0f}",
                        f"{row['RiskScore']:.0f}/100",
                        f"{row['AttritionProbability']:.1%}",
                    ],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
        top_feature = contrib_df[contrib_df["Direction"] == "Risk Factor"].tail(1)["Feature"].iloc[0]
        raw_feature = top_feature.split("_", 1)[0] if top_feature.startswith("MaritalStatus_") else top_feature
        intervention = INTERVENTION_MAP.get(raw_feature, "Review manager-level retention plan and employee experience signals")
        insight_card("Top Intervention", intervention)

section_divider("Retention Intervention Matrix")
top_features = fi.head(5)["Feature"].tolist()
intervention_rows = []
for tier in ["High", "Medium"]:
    for feature in top_features:
        raw_feature = feature.split("_", 1)[0] if feature.startswith("MaritalStatus_") else feature
        intervention_rows.append(
            {
                "Risk Tier": tier,
                "Risk Driver": _feature_label(feature),
                "Recommended Intervention": INTERVENTION_MAP.get(raw_feature, "Review manager-level retention plan and employee experience signals"),
                "Priority": "P1 - Immediate" if tier == "High" else "P2 - 30 Days",
            }
        )
st.dataframe(pd.DataFrame(intervention_rows), use_container_width=True, hide_index=True)

section_divider("High-Risk Segments")
filtered_scored = scored_df.loc[filtered_scored.index].copy()
high_risk = filtered_scored[filtered_scored["RiskTier"] == "High"][
    [
        "Department",
        "JobRole",
        "Age",
        "YearsAtCompany",
        "MonthlyIncome",
        "OverTime",
        "RiskScore",
        "AttritionProbability",
        "Primary Risk Factor",
    ]
].sort_values("RiskScore", ascending=False)
high_risk["AttritionProbability"] = (high_risk["AttritionProbability"] * 100).round(1).astype(str) + "%"
high_risk["MonthlyIncome"] = high_risk["MonthlyIncome"].apply(lambda value: f"${value:,.0f}")
st.dataframe(high_risk.reset_index(drop=True), use_container_width=True)
chart_caption(len(high_risk), f"{len(high_risk)} high-risk employees")

download_filtered_data(filtered_scored, "risk_scored_ensemble_data.csv")
