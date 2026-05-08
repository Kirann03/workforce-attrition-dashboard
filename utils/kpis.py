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
            "warning": "Insufficient data.",
        }
    table = pd.crosstab(df[group_col], df["Attrition"])
    _, _, _, expected = stats.chi2_contingency(table)
    cells_below_5 = int((expected < 5).sum())
    total_cells = int(expected.size)
    if total_cells and cells_below_5 / total_cells > 0.2:
        return {
            "statistic": None,
            "p_value": None,
            "significant": False,
            "interpretation": (
                f"Chi-square test unreliable: {cells_below_5}/{total_cells} expected cells < 5. "
                "Increase sample size by relaxing filters."
            ),
            "warning": f"{cells_below_5} cells have expected count < 5.",
        }

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
        "warning": None,
    }


def cross_attrition_rate(
    df: pd.DataFrame,
    row_col: str,
    col_col: str,
    min_n: int = MIN_GROUP_SIZE,
) -> pd.DataFrame:
    """
    Compute attrition rate for a two-way cross-tab.

    Groups with fewer than min_n employees are set to NaN so heatmaps can
    distinguish insufficient data from a genuine 0% attrition rate.
    """
    grouped = df.groupby([row_col, col_col], observed=False).agg(
        Total=("Attrition", "count"),
        Left=("Attrition", "sum"),
    ).reset_index()
    grouped["Rate"] = (grouped["Left"] / grouped["Total"] * 100).round(1)
    grouped.loc[grouped["Total"] < min_n, "Rate"] = float("nan")
    return grouped


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


def cost_of_attrition(
    df: pd.DataFrame,
    replacement_pct: float = 0.50,
    recruitment_cost: float = 5000,
    training_cost: float = 3000,
    productivity_months: int = 3,
    productivity_pct: float = 0.25,
) -> dict:
    """Compute estimated total annual cost of attrition."""
    n_exits = int(df["Attrition"].sum())
    avg_annual_salary = df["MonthlyIncome"].mean() * 12 if len(df) else 0
    cost_per_exit = (
        avg_annual_salary * replacement_pct
        + recruitment_cost
        + training_cost
        + (avg_annual_salary / 12) * productivity_months * productivity_pct
    )
    total_cost = cost_per_exit * n_exits
    return {
        "n_exits": n_exits,
        "avg_annual_salary": round(avg_annual_salary, 0),
        "cost_per_exit": round(cost_per_exit, 0),
        "total_annual_cost": round(total_cost, 0),
    }


def cramers_v(df: pd.DataFrame, col1: str, col2: str) -> float:
    """Compute Cramer's V effect size for two categorical variables."""
    table = pd.crosstab(df[col1], df[col2])
    if table.empty or min(table.shape) < 2:
        return 0.0
    chi2, _, _, _ = stats.chi2_contingency(table)
    n = table.sum().sum()
    r, c = table.shape
    denom = n * (min(r, c) - 1)
    return float(np.sqrt(chi2 / denom)) if denom else 0.0


def retention_roi(current_cost: float, reduction_pct: float, program_cost: float) -> dict:
    """Compute ROI of a proposed retention program."""
    savings = current_cost * (reduction_pct / 100)
    net = savings - program_cost
    roi = (net / program_cost * 100) if program_cost > 0 else 0
    return {
        "gross_savings": round(savings, 0),
        "net_savings": round(net, 0),
        "roi_pct": round(roi, 1),
        "break_even": roi > 0,
    }
