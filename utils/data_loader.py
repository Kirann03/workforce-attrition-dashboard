from pathlib import Path

import pandas as pd
import streamlit as st

from utils.config import (
    AGE_BINS,
    AGE_LABELS,
    CAREER_BINS,
    CAREER_LABELS,
    DISTANCE_BINS,
    DISTANCE_LABELS,
    EDUCATION_LABELS,
    INCOME_BINS,
    INCOME_LABELS,
    JOB_LEVEL_LABELS,
    PERFORMANCE_RATING_LABELS,
    PROMOTION_STAGNATION_BINS,
    PROMOTION_STAGNATION_LABELS,
    TENURE_BINS,
    TENURE_LABELS,
    TRAVEL_ORDER,
)


CRITICAL_COLUMNS = [
    "Age",
    "Attrition",
    "Department",
    "JobRole",
    "OverTime",
    "BusinessTravel",
    "MonthlyIncome",
    "YearsAtCompany",
]


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate required workforce columns before feature engineering."""
    missing = df[CRITICAL_COLUMNS].isna().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        st.warning("Data quality warning: missing values found in critical columns.")
    return df


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the HR dataset and create reusable analytical features."""
    candidate_paths = [
        Path("Palo_Alto_Networks.csv"),
        Path("Palo Alto Networks.csv"),
        Path(__file__).resolve().parents[1] / "Palo_Alto_Networks.csv",
        Path(__file__).resolve().parents[1] / "Palo Alto Networks.csv",
    ]
    csv_path = next((path for path in candidate_paths if path.exists()), None)
    if csv_path is None:
        raise FileNotFoundError("Place Palo_Alto_Networks.csv in the same directory as app.py.")

    df = pd.read_csv(csv_path)
    df["BusinessTravel"] = pd.Categorical(
        df["BusinessTravel"],
        categories=TRAVEL_ORDER,
        ordered=True,
    )
    assert list(df["BusinessTravel"].cat.categories) == TRAVEL_ORDER and df["BusinessTravel"].cat.ordered

    # Normalise Attrition to integer 0/1 regardless of source encoding.
    if df["Attrition"].dtype == object:
        original_attrition = df["Attrition"].copy()
        attrition_map = {"yes": 1, "no": 0, "true": 1, "false": 0, "1": 1, "0": 0}
        df["Attrition"] = df["Attrition"].str.strip().str.lower().map(attrition_map)
        if df["Attrition"].isna().any():
            bad_values = original_attrition[df["Attrition"].isna()].unique().tolist()
            raise ValueError(
                "Attrition column contains unrecognised values: "
                f"{bad_values}. Expected 0/1 or Yes/No."
            )
    else:
        df["Attrition"] = df["Attrition"].astype(int)
    assert set(df["Attrition"].unique()).issubset({0, 1}), "Attrition must be binary (0/1) after normalisation."

    df["Attrition_Label"] = df["Attrition"].map({1: "Left", 0: "Stayed"})
    validate_data(df)

    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=AGE_BINS,
        labels=AGE_LABELS,
    )
    df["TenureBucket"] = pd.cut(
        df["YearsAtCompany"],
        bins=TENURE_BINS,
        labels=TENURE_LABELS,
    )
    df["CareerStage"] = pd.cut(
        df["TotalWorkingYears"],
        bins=CAREER_BINS,
        labels=CAREER_LABELS,
    )
    df["IncomeBand"] = pd.cut(
        df["MonthlyIncome"],
        bins=INCOME_BINS,
        labels=INCOME_LABELS,
    )

    df["EducationLabel"] = df["Education"].map(EDUCATION_LABELS)
    df["PerformanceLabel"] = df["PerformanceRating"].map(PERFORMANCE_RATING_LABELS)
    assert df["PerformanceLabel"].notna().all(), "Unexpected PerformanceRating values detected."
    df["PromotionBand"] = pd.cut(
        df["YearsSinceLastPromotion"],
        bins=PROMOTION_STAGNATION_BINS,
        labels=PROMOTION_STAGNATION_LABELS,
    )
    assert df["PromotionBand"].isna().sum() == 0, "PromotionBand has NaN rows."
    df["ManagerTenureRatio"] = (df["YearsWithCurrManager"] / df["YearsAtCompany"].replace(0, 1)).round(2)
    df["JobHopper"] = (df["NumCompaniesWorked"] >= 4).astype(int)
    df["WorkloadStress"] = (
        (df["OverTime"] == "Yes")
        & (df["BusinessTravel"] == "Travel_Frequently")
    ).astype(int)
    stress_count = int(df["WorkloadStress"].sum())
    assert 50 <= stress_count <= 200, (
        f"WorkloadStress count {stress_count} is outside expected range [50, 200]. "
        "Check BusinessTravel encoding."
    )
    # SatisfactionIndex is a composite of four satisfaction columns.
    # It is intentionally excluded from ML features to avoid multicollinearity.
    df["SatisfactionIndex"] = df[
        ["JobSatisfaction", "EnvironmentSatisfaction", "WorkLifeBalance", "RelationshipSatisfaction"]
    ].mean(axis=1).round(2)
    assert df["SatisfactionIndex"].between(1.0, 4.0).all(), "SatisfactionIndex out of [1,4] range."

    # IncomeLevelRatio: monthly income relative to job-level salary band baseline.
    # JobLevel min=1, max=5; no zero-division risk.
    df["IncomeLevelRatio"] = (df["MonthlyIncome"] / (df["JobLevel"] * 1000)).round(2)
    assert df["IncomeLevelRatio"].gt(0).all(), "IncomeLevelRatio must be positive."

    # LoyaltyScore: fraction of total career spent at this company (0.0-1.0).
    # TotalWorkingYears=0 guard: treat as 1 to avoid ZeroDivisionError for fresh graduates.
    loyalty_denom = df["TotalWorkingYears"].replace(0, 1)
    df["LoyaltyScore"] = (df["YearsAtCompany"] / loyalty_denom).clip(0.0, 1.0).round(2)
    assert df["LoyaltyScore"].between(0, 1).all(), "LoyaltyScore out of [0,1] range."
    df["DistanceBand"] = pd.cut(
        df["DistanceFromHome"],
        bins=DISTANCE_BINS,
        labels=DISTANCE_LABELS,
        include_lowest=True,
        right=True,
    )
    assert df["DistanceBand"].isna().sum() == 0, "DistanceBand has NaN rows."
    df["TrainingGap"] = (df["TrainingTimesLastYear"] == 0).astype(int)
    df["JobLevelLabel"] = df["JobLevel"].map(JOB_LEVEL_LABELS)
    df["DeptRole"] = df["Department"] + " — " + df["JobRole"]
    stock_rates = df.groupby("StockOptionLevel", observed=False)["Attrition"].mean()
    if {0, 1, 2, 3}.issubset(set(stock_rates.index)):
        assert stock_rates.loc[3] > stock_rates.loc[2], "Expected non-monotonic StockOptionLevel attrition pattern not present."

    level_medians = df.groupby("JobLevel")["MonthlyIncome"].median()
    df["BelowLevelMedian"] = df.apply(
        lambda row: 1 if row["MonthlyIncome"] < level_medians.get(row["JobLevel"], 0) else 0,
        axis=1,
    ).astype(int)
    df["RetentionRiskIndex"] = (
        (df["OverTime"] == "Yes").astype(int) * 2
        + (df["BusinessTravel"] == "Travel_Frequently").astype(int) * 1.5
        + (df["JobSatisfaction"] <= 2).astype(int) * 2
        + (df["YearsSinceLastPromotion"] >= 3).astype(int) * 1.5
        + (df["EnvironmentSatisfaction"] <= 2).astype(int)
        + df["BelowLevelMedian"] * 1.5
        + (df["StockOptionLevel"] == 0).astype(int)
    ).round(2)
    df["ManagerTenureBand"] = pd.cut(
        df["YearsWithCurrManager"],
        bins=[-1, 1, 3, 5, 100],
        labels=["<1 yr", "1-3 yrs", "3-5 yrs", "5+ yrs"],
    )
    return df
