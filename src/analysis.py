"""Metrics, adoption score and tables computed from the demonstration dataset."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import (
    ADOPTION_BANDS,
    ADOPTION_WEIGHTS,
    FREQUENCY_POINTS,
    PREFERENCE_POINTS,
    TENURE_CAP_MONTHS,
)

CHI2_CRITICAL_05 = {
    1: 3.841,
    2: 5.991,
    3: 7.815,
    4: 9.488,
    5: 11.070,
    6: 12.592,
    8: 15.507,
    9: 16.919,
}


def adoption_components(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["comp_account"] = np.where(out["has_upi_account"].eq("Yes"), 100.0, 0.0)
    out["comp_frequency"] = out["upi_usage_frequency"].map(FREQUENCY_POINTS).fillna(0.0)
    out["comp_digital_share"] = (out["upi_share_weekly"] * 100).clip(0, 100)
    out["comp_tenure"] = (out["months_using_upi"].clip(lower=0) / TENURE_CAP_MONTHS * 100).clip(0, 100)
    out["comp_preference"] = out["preferred_mode"].map(PREFERENCE_POINTS).fillna(0.0)

    w = ADOPTION_WEIGHTS
    out["upi_adoption_score"] = (
        w["account"] * out["comp_account"]
        + w["frequency"] * out["comp_frequency"]
        + w["digital_share"] * out["comp_digital_share"]
        + w["tenure"] * out["comp_tenure"]
        + w["preference"] * out["comp_preference"]
    ).round(1)

    def band(score: float) -> str:
        for lo, hi, label in ADOPTION_BANDS:
            if lo <= score < hi:
                return label
        return "Low"

    out["adoption_band"] = out["upi_adoption_score"].apply(band)
    return out


def pct(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round(100.0 * numerator / denominator, 1)


def value_share_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    counts = df[column].value_counts(dropna=False).reset_index()
    counts.columns = ["category", "count"]
    counts["percent"] = (counts["count"] / counts["count"].sum() * 100).round(1)
    return counts


def crosstab_percent(df: pd.DataFrame, row: str, col: str) -> pd.DataFrame:
    ct = pd.crosstab(df[row], df[col], normalize="index") * 100
    return ct.round(1)


def chi_square_from_crosstab(observed: pd.DataFrame) -> dict:
    obs = observed.to_numpy(dtype=float)
    row_tot = obs.sum(axis=1, keepdims=True)
    col_tot = obs.sum(axis=0, keepdims=True)
    n = obs.sum()
    expected = row_tot @ col_tot / n
    with np.errstate(divide="ignore", invalid="ignore"):
        chi2 = np.nansum((obs - expected) ** 2 / np.where(expected == 0, np.nan, expected))
    r, c = obs.shape
    df = int((r - 1) * (c - 1))
    crit = CHI2_CRITICAL_05.get(df)
    cramer = float(np.sqrt(chi2 / (n * min(r - 1, c - 1)))) if n and min(r, c) > 1 else 0.0
    if crit is None:
        decision = "Compare the statistic with a chi-square table (α = 0.05)."
        significant = None
    else:
        significant = bool(chi2 > crit)
        decision = (
            f"Statistic {chi2:.2f} is greater than critical value {crit} (df = {df}, α = 0.05): "
            "association is statistically detectable in this sample."
            if significant
            else f"Statistic {chi2:.2f} is not greater than critical value {crit} (df = {df}, α = 0.05): "
            "no strong evidence of association in this sample."
        )
    return {
        "chi_square": round(float(chi2), 3),
        "df": df,
        "n": int(n),
        "cramers_v": round(cramer, 3),
        "critical_0.05": crit,
        "significant_0.05": significant,
        "decision": decision,
        "expected": pd.DataFrame(expected.round(2), index=observed.index, columns=observed.columns),
    }


def pearson_corr(x: pd.Series, y: pd.Series) -> float:
    pair = pd.concat([x, y], axis=1).dropna()
    if len(pair) < 3:
        return 0.0
    return float(pair.iloc[:, 0].corr(pair.iloc[:, 1]))


def summary_metrics(df: pd.DataFrame) -> dict:
    n = len(df)
    upi_yes = int(df["has_upi_account"].eq("Yes").sum())
    phone_yes = int(df["smartphone_user"].eq("Yes").sum())
    return {
        "n": n,
        "upi_adoption_rate": pct(upi_yes, n),
        "smartphone_rate": pct(phone_yes, n),
        "mean_trust": round(float(df["trust_score"].mean()), 2),
        "mean_security_concern": round(float(df["security_concern_score"].mean()), 2),
        "mean_adoption_score": round(float(df["upi_adoption_score"].mean()), 1),
        "median_adoption_score": round(float(df["upi_adoption_score"].median()), 1),
        "mean_weekly_upi": round(float(df["weekly_upi_txns"].mean()), 1),
        "mean_weekly_cash": round(float(df["weekly_cash_txns"].mean()), 1),
        "mean_upi_share": round(float(df["upi_share_weekly"].mean() * 100), 1),
        "fraud_rate": pct(int(df["fraud_experience"].eq("Yes").sum()), n),
        "prefer_upi": pct(int(df["preferred_mode"].eq("UPI").sum()), n),
        "prefer_cash": pct(int(df["preferred_mode"].eq("Cash").sum()), n),
        "prefer_both": pct(int(df["preferred_mode"].eq("Both").sum()), n),
    }


def score_formula_text() -> str:
    w = ADOPTION_WEIGHTS
    return (
        "UPI Adoption Score (0–100) = "
        f"{w['account']:.0%} × Account + "
        f"{w['frequency']:.0%} × Frequency + "
        f"{w['digital_share']:.0%} × Digital share + "
        f"{w['tenure']:.0%} × Tenure + "
        f"{w['preference']:.0%} × Preference"
    )
