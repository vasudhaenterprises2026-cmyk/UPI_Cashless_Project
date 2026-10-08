"""Plain-language findings and recommendations derived from sample metrics."""

from __future__ import annotations

import pandas as pd

from src.analysis import pct, value_share_table


def key_findings(df: pd.DataFrame, metrics: dict) -> list[str]:
    area = pd.crosstab(df["area_type"], df["has_upi_account"], normalize="index") * 100
    urban_upi = float(area.loc["Urban", "Yes"]) if "Urban" in area.index and "Yes" in area.columns else 0
    rural_upi = float(area.loc["Rural", "Yes"]) if "Rural" in area.index and "Yes" in area.columns else 0

    age_scores = df.groupby("age_group", observed=False)["upi_adoption_score"].mean().sort_values(ascending=False)
    top_age = age_scores.index[0] if len(age_scores) else "—"
    low_age = age_scores.index[-1] if len(age_scores) else "—"

    barriers = value_share_table(df, "main_barrier")
    top_barrier = barriers.iloc[0]["category"] if len(barriers) else "—"

    fraud_trust = df.groupby("fraud_experience")["trust_score"].mean()
    trust_yes = float(fraud_trust.get("Yes", 0))
    trust_no = float(fraud_trust.get("No", 0))

    pref = metrics
    return [
        f"In this synthetic sample of {metrics['n']} records, {metrics['upi_adoption_rate']}% have a UPI account "
        f"and {metrics['smartphone_rate']}% are smartphone users.",
        f"The mean UPI Adoption Score is {metrics['mean_adoption_score']} (median {metrics['median_adoption_score']}), "
        "on a 0–100 scale defined in this project.",
        f"Urban UPI-account rate is {urban_upi:.1f}%, compared with {rural_upi:.1f}% in rural records "
        "within this synthetic sample.",
        f"Age group {top_age} has the highest mean adoption score; {low_age} has the lowest.",
        f"Average weekly UPI transactions ({metrics['mean_weekly_upi']}) sit beside "
        f"{metrics['mean_weekly_cash']} cash transactions, so cash still coexists with UPI in the sample.",
        f"Preferred mode: UPI {pref['prefer_upi']}%, both {pref['prefer_both']}%, cash {pref['prefer_cash']}%.",
        f"Mean trust score is {metrics['mean_trust']} / 5. Records flagged with fraud experience "
        f"show mean trust {trust_yes:.2f} versus {trust_no:.2f} without that flag.",
        f"The most common stated barrier in the file is “{top_barrier}”.",
        f"{metrics['fraud_rate']}% of records include a synthetic fraud-experience flag; "
        "this is generated for illustration of trust patterns, not a real incidence rate.",
    ]


def recommendations(df: pd.DataFrame, metrics: dict) -> list[dict]:
    rural = df[df["area_type"].eq("Rural")]
    rural_upi = pct(int(rural["has_upi_account"].eq("Yes").sum()), len(rural)) if len(rural) else 0
    high_concern = pct(int(df["security_concern_score"].ge(4).sum()), len(df))
    older = df[df["age_group"].eq("55+")]
    older_score = float(older["upi_adoption_score"].mean()) if len(older) else 0

    return [
        {
            "title": "Treat cash and UPI as coexisting, not as a sudden replacement",
            "text": (
                "If a future real-world study finds a similar pattern, explain where each payment mode is useful "
                "instead of assuming cash will disappear."
            ),
            "evidence": (
                f"{metrics['prefer_both']}% prefer both modes; mean weekly cash transactions are "
                f"{metrics['mean_weekly_cash']} compared with {metrics['mean_weekly_upi']} UPI transactions."
            ),
        },
        {
            "title": "Focus practical onboarding where adoption scores are lower",
            "text": (
                "If independently confirmed with real data, test assisted registration and local merchant "
                "acceptance support in rural settings."
            ),
            "evidence": f"Rural UPI-account rate in this synthetic sample: {rural_upi}%.",
        },
        {
            "title": "Build trust with simple fraud-safety habits",
            "text": (
                "For a real intervention, evaluate concise guidance on verifying UPI IDs, avoiding unknown "
                "collect requests and using official apps."
            ),
            "evidence": f"{high_concern}% of filtered records have a security-concern score of 4 or 5.",
        },
        {
            "title": "Design for older users and mixed digital skill",
            "text": (
                "If a real study confirms this difference, test large-text walkthroughs and optional assisted setup."
            ),
            "evidence": (
                f"The 55+ age group has a mean adoption score of {older_score:.1f}; "
                f"the overall filtered-sample mean is {metrics['mean_adoption_score']}."
            ),
        },
        {
            "title": "Keep future field work transparent",
            "text": (
                "A future field study should use informed consent and a documented sampling plan, "
                "and should store actual responses separately from the demonstration data."
            ),
            "evidence": "The current dataset is generated synthetic/demo data; no field survey was conducted.",
        },
    ]
