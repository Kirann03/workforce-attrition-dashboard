import pandas as pd


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
