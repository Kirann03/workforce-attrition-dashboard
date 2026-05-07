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
    TENURE_BINS,
    TENURE_LABELS,
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


def validate_data(df):
    missing = df[CRITICAL_COLUMNS].isna().sum()
    missing = missing[missing > 0]
    if not missing.empty:
        st.warning("Data quality warning: missing values found in critical columns.")
    return df


@st.cache_data
def load_data():
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
    df["Attrition"] = df["Attrition"].astype(int)
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
    df["PromotionStagnant"] = (df["YearsSinceLastPromotion"] >= 3).astype(int)
    df["ManagerTenureRatio"] = (df["YearsWithCurrManager"] / df["YearsAtCompany"].replace(0, 1)).round(2)
    df["JobHopper"] = (df["NumCompaniesWorked"] >= 4).astype(int)
    df["WorkloadStress"] = (
        (df["OverTime"] == "Yes") & (df["BusinessTravel"] == "Travel_Frequently")
    ).astype(int)
    df["SatisfactionIndex"] = df[
        ["JobSatisfaction", "EnvironmentSatisfaction", "WorkLifeBalance", "RelationshipSatisfaction"]
    ].mean(axis=1).round(2)
    df["IncomeLevelRatio"] = (df["MonthlyIncome"] / (df["JobLevel"] * 1000)).round(2)
    df["LoyaltyScore"] = (
        df["YearsAtCompany"] / df["TotalWorkingYears"].replace(0, 1)
    ).clip(0, 1).round(2)
    df["DistanceBand"] = pd.cut(
        df["DistanceFromHome"],
        bins=DISTANCE_BINS,
        labels=DISTANCE_LABELS,
        include_lowest=True,
    )
    df["TrainingGap"] = (df["TrainingTimesLastYear"] == 0).astype(int)
    df["JobLevelLabel"] = df["JobLevel"].map(JOB_LEVEL_LABELS)
    return df
