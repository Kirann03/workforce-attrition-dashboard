import numpy as np
import pandas as pd
from scipy import stats

from utils.config import MIN_GROUP_SIZE


def attrition_summary(df: pd.DataFrame) -> dict[str, float]:
    total = len(df)
    left = int(df["Attrition"].sum())
    stayed = total - left
    rate = round(left / total * 100, 2) if total else 0.0
    return {"total": total, "left": left, "stayed": stayed, "rate": rate}


def attrition_rate(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    grouped = df.groupby(group_col, observed=False).agg(
        Total=("Attrition", "count"),
        Left=("Attrition", "sum"),
    ).reset_index()
    grouped["Rate"] = (grouped["Left"] / grouped["Total"] * 100).fillna(0).round(2)
    return grouped


def attrition_with_ci(df: pd.DataFrame, group_col: str, confidence: float = 0.95) -> pd.DataFrame:
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    grouped = attrition_rate(df, group_col)
    n = grouped["Total"].astype(float)
    p = (grouped["Left"] / grouped["Total"]).fillna(0)
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    grouped["CI_Lower"] = ((center - margin).clip(0, 1) * 100).round(2)
    grouped["CI_Upper"] = ((center + margin).clip(0, 1) * 100).round(2)
    return grouped


def baseline_comparison(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    grouped = attrition_rate(df, group_col)
    baseline = df["Attrition"].mean() * 100 if len(df) else 0
    grouped["Baseline"] = round(baseline, 2)
    grouped["Delta"] = (grouped["Rate"] - baseline).round(2)
    grouped["BaselineFlag"] = np.where(grouped["Delta"] > 0, "Above Baseline", "Below Baseline")
    return grouped


def chi_square_test(df: pd.DataFrame, group_col: str) -> dict:
    if df.empty or df[group_col].nunique(dropna=True) < 2:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "significant": False,
            "interpretation": "Not enough group variation to test independence.",
        }
    table = pd.crosstab(df[group_col], df["Attrition"])
    statistic, p_value, _, _ = stats.chi2_contingency(table)
    significant = bool(p_value < 0.05)
    interpretation = (
        f"{group_col} is statistically associated with attrition at alpha=0.05."
        if significant
        else f"No statistically significant association detected between {group_col} and attrition."
    )
    return {
        "statistic": round(float(statistic), 4),
        "p_value": round(float(p_value), 4),
        "significant": significant,
        "interpretation": interpretation,
    }


def top_n_risk_groups(df: pd.DataFrame, group_col: str, n: int = 3) -> pd.DataFrame:
    grouped = attrition_rate(df, group_col)
    return grouped[grouped["Total"] >= MIN_GROUP_SIZE].sort_values("Rate", ascending=False).head(n)


def loyalty_attrition_split(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    df2["LoyaltyTier"] = pd.cut(
        df2["LoyaltyScore"],
        bins=[0, 0.33, 0.66, 1.01],
        labels=["Low (<33%)", "Mid (33-66%)", "High (>66%)"],
        include_lowest=True,
    )
    return attrition_rate(df2, "LoyaltyTier")


def satisfaction_risk_matrix(df: pd.DataFrame, sat_col: str, workload_col: str) -> pd.DataFrame:
    df2 = df.copy()
    df2["SatBand"] = df2[sat_col].apply(lambda value: "Low (1-2)" if value <= 2 else "High (3-4)")
    df2["WorkloadBand"] = df2[workload_col].map({"Yes": "Overtime", "No": "No Overtime"})
    grouped = df2.groupby(["SatBand", "WorkloadBand"], observed=False).agg(
        Total=("Attrition", "count"),
        Left=("Attrition", "sum"),
    ).reset_index()
    grouped["Rate"] = (grouped["Left"] / grouped["Total"] * 100).fillna(0).round(2)
    return grouped
