"""Cleaning steps for the synthetic demonstration file."""

from __future__ import annotations

import pandas as pd

from src.config import DATA_SOURCE_LABEL


GENDER_MAP = {
    "m": "Male",
    "male": "Male",
    "f": "Female",
    "female": "Female",
    "other": "Other",
    "o": "Other",
}

YES_NO_MAP = {
    "y": "Yes",
    "yes": "Yes",
    "n": "No",
    "no": "No",
}


def _norm_text(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().replace({"nan": pd.NA, "None": pd.NA})


def _map_yes_no(series: pd.Series) -> pd.Series:
    s = _norm_text(series).str.lower()
    return s.map(YES_NO_MAP)


def clean_dataset(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return cleaned frame and a step log describing each change."""
    df = raw.copy()
    logs = []

    n0 = len(df)
    logs.append({"step": "Start", "detail": f"{n0} synthetic rows loaded.", "rows": n0})

    for col in [
        "gender",
        "occupation",
        "education",
        "area_type",
        "monthly_income_band",
        "smartphone_user",
        "has_upi_account",
        "upi_usage_frequency",
        "preferred_mode",
        "fraud_experience",
        "main_barrier",
        "merchant_acceptance_nearby",
        "reason_for_upi",
        "avg_upi_txn_amount_band",
        "upi_apps_used",
    ]:
        if col in df.columns:
            df[col] = _norm_text(df[col])

    logs.append(
        {
            "step": "Trim text fields",
            "detail": "Removed extra spaces and standardised blank text as missing.",
            "rows": len(df),
        }
    )

    df["gender"] = df["gender"].str.lower().map(GENDER_MAP).fillna(df["gender"])
    logs.append(
        {
            "step": "Standardise gender",
            "detail": "Mapped aliases such as M / F / male / female to Male, Female, Other.",
            "rows": len(df),
        }
    )

    for col in ["smartphone_user", "has_upi_account", "fraud_experience"]:
        df[col] = _map_yes_no(df[col])
    logs.append(
        {
            "step": "Standardise Yes/No fields",
            "detail": "Normalised YES/yes/Y and similar values for smartphone, UPI account and fraud flags.",
            "rows": len(df),
        }
    )

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    invalid_age = df["age"].notna() & ((df["age"] < 18) | (df["age"] > 90))
    n_invalid_age = int(invalid_age.sum())
    df.loc[invalid_age, "age"] = pd.NA
    logs.append(
        {
            "step": "Age range check",
            "detail": f"Set {n_invalid_age} impossible ages (under 18 or over 90) to missing.",
            "rows": len(df),
        }
    )

    age_median = df["age"].median()
    n_age_missing = int(df["age"].isna().sum())
    df["age"] = df["age"].fillna(age_median)
    logs.append(
        {
            "step": "Fill missing age",
            "detail": f"Filled {n_age_missing} missing ages with the median ({age_median:.0f}).",
            "rows": len(df),
        }
    )

    occ_mode = df["occupation"].mode(dropna=True)
    occ_fill = occ_mode.iloc[0] if len(occ_mode) else "Unknown"
    n_occ = int(df["occupation"].isna().sum())
    df["occupation"] = df["occupation"].fillna(occ_fill)
    logs.append(
        {
            "step": "Fill missing occupation",
            "detail": f"Filled {n_occ} missing occupations with the mode ({occ_fill}).",
            "rows": len(df),
        }
    )

    n_inc = int(df["monthly_income_band"].isna().sum())
    df["monthly_income_band"] = df["monthly_income_band"].fillna("Not reported")
    logs.append(
        {
            "step": "Fill missing income band",
            "detail": f"Labelled {n_inc} missing income bands as 'Not reported'.",
            "rows": len(df),
        }
    )

    trust_median = pd.to_numeric(df["trust_score"], errors="coerce").median()
    n_trust = int(pd.to_numeric(df["trust_score"], errors="coerce").isna().sum())
    df["trust_score"] = pd.to_numeric(df["trust_score"], errors="coerce").fillna(trust_median)
    logs.append(
        {
            "step": "Fill missing trust score",
            "detail": f"Filled {n_trust} missing trust scores with the median ({trust_median:.0f}).",
            "rows": len(df),
        }
    )

    numeric_cols = [
        "months_using_upi",
        "weekly_cash_txns",
        "weekly_upi_txns",
        "security_concern_score",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)

    df["age"] = df["age"].round(0).astype(int)
    df["trust_score"] = df["trust_score"].clip(1, 5).round(0).astype(int)
    df["security_concern_score"] = df["security_concern_score"].clip(1, 5).round(0).astype(int)

    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 24, 34, 44, 54, 90],
        labels=["18–24", "25–34", "35–44", "45–54", "55+"],
    ).astype(str)

    df["weekly_total_txns"] = df["weekly_cash_txns"] + df["weekly_upi_txns"]
    df["upi_share_weekly"] = np_safe_share(df["weekly_upi_txns"], df["weekly_total_txns"])

    df["data_source"] = DATA_SOURCE_LABEL
    df["record_type"] = "SYNTHETIC / DEMONSTRATION — not a real respondent"
    df["cleaning_status"] = "cleaned_for_demonstration"

    logs.append(
        {
            "step": "Derived fields",
            "detail": "Added age_group, weekly_total_txns and upi_share_weekly.",
            "rows": len(df),
        }
    )
    return df, pd.DataFrame(logs)


def np_safe_share(numer: pd.Series, denom: pd.Series) -> pd.Series:
    denom = denom.replace(0, pd.NA)
    share = numer / denom
    return share.fillna(0.0)


def get_cleaned_dataset(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return clean_dataset(raw)
