import numpy as np
import pandas as pd
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
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

from utils.config import (
    GB_LEARNING_RATE,
    GB_MAX_DEPTH,
    GB_MIN_SAMPLES_LEAF,
    GB_N_ESTIMATORS,
    GB_SUBSAMPLE,
    LR_C,
    LR_MAX_ITER,
    ML_FEATURE_LABELS,
    MODEL_RANDOM_STATE,
    RF_MAX_DEPTH,
    RF_MIN_SAMPLES_LEAF,
    RF_N_ESTIMATORS,
)


def feature_label(feature: str) -> str:
    """Return a readable label for raw and encoded model features."""
    if feature in ML_FEATURE_LABELS:
        return ML_FEATURE_LABELS[feature]
    if feature.startswith("MaritalStatus_"):
        return "Marital Status: " + feature.replace("MaritalStatus_", "")
    return feature.replace("_", " ").title()


def encode_df(df_ml: pd.DataFrame, encoding_info: dict) -> pd.DataFrame:
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


def find_optimal_threshold(probs: np.ndarray, y: np.ndarray) -> float:
    """Return the probability threshold that maximises minority-class F1."""
    precisions, recalls, thresholds = precision_recall_curve(y, probs)
    f1s = 2 * precisions * recalls / (precisions + recalls + 1e-9)
    best_idx = int(np.argmax(f1s[:-1]))
    return float(thresholds[best_idx])


def ensemble_prob(
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


def make_lr_pipeline() -> Pipeline:
    """Create the scaled logistic regression member of the ensemble."""
    return Pipeline(
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
    lr = make_lr_pipeline()

    gb.fit(x_values, y_values, sample_weight=weights)
    rf.fit(x_values, y_values, sample_weight=weights)
    lr.fit(x_values, y_values, classifier__sample_weight=weights)
    probs = ensemble_prob(gb, rf, lr, x_values)
    threshold = find_optimal_threshold(probs, y_values)

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
        lr_cv = make_lr_pipeline()
        gb_cv.fit(x_values[train_idx], y_values[train_idx], sample_weight=weights[train_idx])
        rf_cv.fit(x_values[train_idx], y_values[train_idx], sample_weight=weights[train_idx])
        lr_cv.fit(x_values[train_idx], y_values[train_idx], classifier__sample_weight=weights[train_idx])
        gb_probs[val_idx] = gb_cv.predict_proba(x_values[val_idx])[:, 1]
        rf_probs[val_idx] = rf_cv.predict_proba(x_values[val_idx])[:, 1]
        lr_probs[val_idx] = lr_cv.predict_proba(x_values[val_idx])[:, 1]
        oof_probs[val_idx] = (gb_probs[val_idx] + rf_probs[val_idx] + lr_probs[val_idx]) / 3.0

    threshold = find_optimal_threshold(oof_probs, y_values)
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
