from pathlib import Path

import pandas as pd
import streamlit as st


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

    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[17, 25, 35, 45, 55, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "55+"],
    )
    df["TenureBucket"] = pd.cut(
        df["YearsAtCompany"],
        bins=[-1, 1, 3, 5, 10, 100],
        labels=["0-1 yr", "1-3 yrs", "3-5 yrs", "5-10 yrs", "10+ yrs"],
    )
    df["CareerStage"] = pd.cut(
        df["TotalWorkingYears"],
        bins=[-1, 5, 15, 100],
        labels=["Early (0-5 yrs)", "Mid (6-15 yrs)", "Senior (15+ yrs)"],
    )
    df["IncomeBand"] = pd.cut(
        df["MonthlyIncome"],
        bins=[0, 3000, 6000, 10000, 100000],
        labels=["Low (<3K)", "Mid (3-6K)", "High (6-10K)", "Very High (>10K)"],
    )

    edu_map = {1: "Below College", 2: "College", 3: "Bachelor", 4: "Master", 5: "Doctor"}
    df["EducationLabel"] = df["Education"].map(edu_map)
    return df
