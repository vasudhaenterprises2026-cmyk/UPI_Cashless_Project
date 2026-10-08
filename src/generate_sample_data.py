"""Generate a labelled synthetic UPI behaviour dataset (demonstration only)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import DATA_DIR, DATA_SOURCE_LABEL, N_RESPONDENTS, RANDOM_SEED, RAW_CSV_NAME


def _pick(rng: np.random.Generator, values: list, probs: list, size: int) -> np.ndarray:
    return rng.choice(values, size=size, p=probs)


def generate_synthetic_frame(n: int = N_RESPONDENTS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Create n synthetic rows with plausible associations, then add cleaning issues."""
    rng = np.random.default_rng(seed)

    area_type = _pick(
        rng,
        ["Urban", "Semi-urban", "Rural"],
        [0.42, 0.28, 0.30],
        n,
    )
    gender = _pick(rng, ["Male", "Female", "Other"], [0.49, 0.49, 0.02], n)
    occupation = _pick(
        rng,
        ["Student", "Salaried", "Self-employed", "Homemaker", "Daily-wage worker", "Retired"],
        [0.18, 0.32, 0.18, 0.12, 0.12, 0.08],
        n,
    )
    education = _pick(
        rng,
        ["Secondary", "Higher Secondary", "Graduate", "Postgraduate"],
        [0.18, 0.28, 0.38, 0.16],
        n,
    )
    income_band = _pick(
        rng,
        ["Below 15,000", "15,000–30,000", "30,000–50,000", "50,000–80,000", "Above 80,000"],
        [0.18, 0.30, 0.28, 0.16, 0.08],
        n,
    )

    age = np.empty(n, dtype=float)
    for i, occ in enumerate(occupation):
        if occ == "Student":
            age[i] = rng.integers(18, 25)
        elif occ == "Retired":
            age[i] = rng.integers(58, 76)
        elif occ == "Daily-wage worker":
            age[i] = rng.integers(22, 56)
        else:
            age[i] = rng.integers(21, 62)

    smartphone = np.array(["Yes"] * n, dtype=object)
    for i in range(n):
        p_phone = 0.97 if area_type[i] == "Urban" else 0.90 if area_type[i] == "Semi-urban" else 0.78
        if occupation[i] == "Student":
            p_phone = max(p_phone, 0.96)
        if age[i] >= 60:
            p_phone -= 0.12
        smartphone[i] = "Yes" if rng.random() < p_phone else "No"

    has_upi = np.array(["No"] * n, dtype=object)
    for i in range(n):
        if smartphone[i] == "No":
            has_upi[i] = "No"
            continue
        p = 0.88
        if area_type[i] == "Rural":
            p -= 0.18
        elif area_type[i] == "Semi-urban":
            p -= 0.08
        if occupation[i] in {"Student", "Salaried"}:
            p += 0.06
        if occupation[i] in {"Retired", "Daily-wage worker"}:
            p -= 0.10
        if education[i] in {"Graduate", "Postgraduate"}:
            p += 0.05
        if age[i] >= 55:
            p -= 0.12
        has_upi[i] = "Yes" if rng.random() < min(0.97, max(0.12, p)) else "No"

    upi_apps = []
    months = np.zeros(n, dtype=float)
    frequency = np.array(["Never"] * n, dtype=object)
    weekly_upi = np.zeros(n, dtype=float)
    weekly_cash = np.zeros(n, dtype=float)
    amount_band = np.array(["None"] * n, dtype=object)
    preferred = np.array(["Cash"] * n, dtype=object)
    reasons = np.array(["Not applicable"] * n, dtype=object)

    app_choices = ["Google Pay", "PhonePe", "Paytm", "BHIM", "Amazon Pay"]
    reason_choices = [
        "Speed and convenience",
        "Merchant request / necessity",
        "Cashback or offers",
        "Easier record-keeping",
        "Peer influence",
    ]

    for i in range(n):
        if has_upi[i] == "No":
            upi_apps.append("None")
            months[i] = 0
            frequency[i] = "Never"
            weekly_upi[i] = 0
            weekly_cash[i] = int(rng.integers(6, 22))
            amount_band[i] = "None"
            preferred[i] = "Cash"
            reasons[i] = "Not applicable"
            continue

        k = int(rng.integers(1, 4))
        selected = rng.choice(app_choices, size=k, replace=False)
        upi_apps.append(", ".join(sorted(selected)))
        months[i] = int(rng.integers(1, 49))

        freq_p = [0.42, 0.32, 0.16, 0.10]
        if area_type[i] == "Rural":
            freq_p = [0.22, 0.30, 0.28, 0.20]
        if occupation[i] == "Student":
            freq_p = [0.50, 0.30, 0.14, 0.06]
        frequency[i] = rng.choice(["Daily", "Weekly", "Monthly", "Rarely"], p=freq_p)

        if frequency[i] == "Daily":
            weekly_upi[i] = int(rng.integers(8, 28))
        elif frequency[i] == "Weekly":
            weekly_upi[i] = int(rng.integers(3, 10))
        elif frequency[i] == "Monthly":
            weekly_upi[i] = int(rng.integers(1, 4))
        else:
            weekly_upi[i] = int(rng.integers(0, 2))

        cash_base = 12 if area_type[i] == "Rural" else 8 if area_type[i] == "Semi-urban" else 5
        weekly_cash[i] = max(0, int(rng.normal(cash_base, 3)))
        if frequency[i] == "Daily":
            weekly_cash[i] = max(0, weekly_cash[i] - int(rng.integers(1, 5)))

        amount_band[i] = rng.choice(
            ["Below 200", "200–500", "500–2,000", "Above 2,000"],
            p=[0.22, 0.38, 0.28, 0.12],
        )
        reasons[i] = rng.choice(reason_choices)

        share = weekly_upi[i] / (weekly_upi[i] + weekly_cash[i] + 1e-6)
        if share >= 0.62:
            preferred[i] = "UPI"
        elif share <= 0.28:
            preferred[i] = "Cash"
        else:
            preferred[i] = rng.choice(["Both", "UPI"], p=[0.7, 0.3])

    trust = np.empty(n, dtype=float)
    security = np.empty(n, dtype=float)
    fraud = np.array(["No"] * n, dtype=object)
    barrier = np.array([""] * n, dtype=object)
    merchant = np.array([""] * n, dtype=object)

    barrier_pool = [
        "Fear of fraud / errors",
        "Unstable network",
        "Limited merchant acceptance",
        "Preference for cash habit",
        "No smartphone / low digital skill",
        "No major barrier",
    ]

    for i in range(n):
        merchant[i] = {
            "Urban": rng.choice(["Low", "Medium", "High"], p=[0.08, 0.32, 0.60]),
            "Semi-urban": rng.choice(["Low", "Medium", "High"], p=[0.18, 0.50, 0.32]),
            "Rural": rng.choice(["Low", "Medium", "High"], p=[0.40, 0.42, 0.18]),
        }[area_type[i]]

        p_fraud = 0.08 if has_upi[i] == "Yes" else 0.03
        fraud[i] = "Yes" if rng.random() < p_fraud else "No"

        t = 3.4
        if has_upi[i] == "Yes":
            t += 0.5
        if area_type[i] == "Urban":
            t += 0.2
        if fraud[i] == "Yes":
            t -= 1.4
        if age[i] >= 55:
            t -= 0.4
        trust[i] = int(np.clip(np.round(t + rng.normal(0, 0.7)), 1, 5))

        s = 3.0
        if fraud[i] == "Yes":
            s += 1.2
        if area_type[i] == "Rural":
            s += 0.3
        if education[i] in {"Graduate", "Postgraduate"}:
            s -= 0.2
        security[i] = int(np.clip(np.round(s + rng.normal(0, 0.7)), 1, 5))

        if has_upi[i] == "No":
            if smartphone[i] == "No":
                barrier[i] = "No smartphone / low digital skill"
            else:
                barrier[i] = rng.choice(
                    [
                        "Fear of fraud / errors",
                        "Preference for cash habit",
                        "Limited merchant acceptance",
                        "Unstable network",
                    ]
                )
        else:
            if security[i] >= 4:
                barrier[i] = "Fear of fraud / errors"
            elif merchant[i] == "Low":
                barrier[i] = "Limited merchant acceptance"
            else:
                barrier[i] = rng.choice(barrier_pool, p=[0.18, 0.14, 0.12, 0.16, 0.08, 0.32])

    df = pd.DataFrame(
        {
            "respondent_id": [f"SYN-{i:03d}" for i in range(1, n + 1)],
            "age": age,
            "gender": gender,
            "occupation": occupation,
            "education": education,
            "area_type": area_type,
            "monthly_income_band": income_band,
            "smartphone_user": smartphone,
            "has_upi_account": has_upi,
            "upi_apps_used": upi_apps,
            "months_using_upi": months,
            "upi_usage_frequency": frequency,
            "preferred_mode": preferred,
            "weekly_cash_txns": weekly_cash,
            "weekly_upi_txns": weekly_upi,
            "avg_upi_txn_amount_band": amount_band,
            "trust_score": trust,
            "security_concern_score": security,
            "fraud_experience": fraud,
            "main_barrier": barrier,
            "merchant_acceptance_nearby": merchant,
            "reason_for_upi": reasons,
            "data_source": DATA_SOURCE_LABEL,
            "record_type": "SYNTHETIC / DEMONSTRATION — not a real respondent",
        }
    )

    return _inject_cleaning_issues(df, rng)


def _inject_cleaning_issues(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Add missing values and inconsistent labels so the cleaning page has work to do."""
    out = df.copy()
    idx = np.arange(len(out))

    miss_age = rng.choice(idx, size=12, replace=False)
    out.loc[miss_age, "age"] = np.nan

    miss_income = rng.choice(idx, size=15, replace=False)
    out.loc[miss_income, "monthly_income_band"] = np.nan

    miss_trust = rng.choice(idx, size=8, replace=False)
    out.loc[miss_trust, "trust_score"] = np.nan

    miss_occ = rng.choice(idx, size=6, replace=False)
    out.loc[miss_occ, "occupation"] = np.nan

    # Inconsistent casing / aliases
    gender_flip = rng.choice(idx, size=18, replace=False)
    for i in gender_flip:
        g = out.at[i, "gender"]
        if g == "Male":
            out.at[i, "gender"] = rng.choice(["male", "M", " Male"])
        elif g == "Female":
            out.at[i, "gender"] = rng.choice(["female", "F", "Female "])

    yesno_cols = ["smartphone_user", "has_upi_account", "fraud_experience"]
    for col in yesno_cols:
        flip = rng.choice(idx, size=10, replace=False)
        for i in flip:
            val = str(out.at[i, col])
            out.at[i, col] = rng.choice([val.lower(), val.upper(), f" {val} "])

    # A few impossible ages (to be clipped / flagged)
    bad_age = rng.choice([i for i in idx if i not in miss_age], size=4, replace=False)
    out.loc[bad_age[:2], "age"] = rng.choice([0, 3, 12])
    out.loc[bad_age[2:], "age"] = rng.choice([118, 143])

    # Extra whitespace in area labels
    area_flip = rng.choice(idx, size=8, replace=False)
    out.loc[area_flip, "area_type"] = out.loc[area_flip, "area_type"].astype(str) + " "

    return out


def write_csv(path: Path | None = None) -> Path:
    path = path or (DATA_DIR / RAW_CSV_NAME)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_synthetic_frame()
    frame.to_csv(path, index=False)
    return path


if __name__ == "__main__":
    out = write_csv()
    print(f"Wrote synthetic demonstration file: {out}")
