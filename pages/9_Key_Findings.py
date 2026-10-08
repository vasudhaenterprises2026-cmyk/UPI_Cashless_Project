import pandas as pd
import streamlit as st

from src.analysis import crosstab_percent, summary_metrics, value_share_table
from src.insights import key_findings
from src.ui import banner, get_prepared_data, page_setup, sidebar_filters

page_setup("Key Findings")
banner(
    "Key Findings",
    "These bullets are generated from the filtered synthetic table. "
    "They describe this file only. They are not findings from a field survey.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

m = summary_metrics(df)
area_rates = crosstab_percent(df, "area_type", "has_upi_account")
age_scores = df.groupby("age_group", observed=False)["upi_adoption_score"].mean().dropna()
top_age = age_scores.idxmax() if len(age_scores) else "—"
low_age = age_scores.idxmin() if len(age_scores) else "—"
urban_rate = area_rates.loc["Urban", "Yes"] if "Urban" in area_rates.index and "Yes" in area_rates.columns else None
rural_rate = area_rates.loc["Rural", "Yes"] if "Rural" in area_rates.index and "Yes" in area_rates.columns else None

st.markdown("## Major findings")
st.caption("These summaries describe the currently filtered synthetic records only.")
adoption_and_payments = st.columns(2)
with adoption_and_payments[0]:
    with st.container(border=True):
        st.markdown("### UPI adoption")
        st.metric("UPI account holders", f"{m['upi_adoption_rate']}%")
        st.write(
            f"The mean project-defined adoption score is **{m['mean_adoption_score']} / 100** "
            f"(median **{m['median_adoption_score']}**); **{m['smartphone_rate']}%** are smartphone users."
        )
with adoption_and_payments[1]:
    with st.container(border=True):
        st.markdown("### Cash and UPI payment patterns")
        st.write(
            f"Preference is split across cash (**{m['prefer_cash']}%**), UPI (**{m['prefer_upi']}%**) "
            f"and both (**{m['prefer_both']}%**)."
        )
        st.write(
            f"Mean weekly transactions: **{m['mean_weekly_cash']} cash** and "
            f"**{m['mean_weekly_upi']} UPI**."
        )
trust_and_groups = st.columns(2)
with trust_and_groups[0]:
    with st.container(border=True):
        st.markdown("### Trust and security")
        st.write(
            f"Mean trust is **{m['mean_trust']} / 5** and mean security concern is "
            f"**{m['mean_security_concern']} / 5**."
        )
        st.write(f"A synthetic fraud-experience flag appears in **{m['fraud_rate']}%** of records.")
with trust_and_groups[1]:
    with st.container(border=True):
        st.markdown("### Differences between groups")
        if urban_rate is not None and rural_rate is not None:
            st.write(
                f"UPI-account ownership is **{urban_rate:.1f}%** in urban and "
                f"**{rural_rate:.1f}%** in rural records."
            )
        st.write(
            f"The highest group mean adoption score is for **{top_age}** and the lowest is for **{low_age}**."
        )

st.markdown("## Supporting evidence")
left, right = st.columns(2)
with left:
    st.markdown("### UPI-account ownership by area")
    st.dataframe(area_rates, width="stretch")
with right:
    st.markdown("### Mean adoption score by age group")
    age_evidence = age_scores.rename("Mean adoption score (0–100)").round(1).rename_axis("Age group").reset_index()
    st.dataframe(age_evidence, hide_index=True, width="stretch")

st.markdown("### Sample distributions")
left, right = st.columns(2)
with left:
    st.markdown("#### Adoption-score bands")
    st.dataframe(value_share_table(df, "adoption_band"), hide_index=True, width="stretch")
with right:
    st.markdown("#### Preferred payment mode")
    st.dataframe(value_share_table(df, "preferred_mode"), hide_index=True, width="stretch")

st.markdown("## What these findings mean")
st.markdown(
    """
- Account ownership and the project-defined score describe different aspects of adoption; neither is a
  population estimate.
- Cash and UPI both appear in the weekly transaction measures. The synthetic results do not support
  assuming that one mode has replaced the other.
- Group differences can identify questions for a properly designed follow-up study. They do not establish
  why a difference occurs or whether it exists in real communities.
"""
)

with st.expander("Show all calculated narrative findings"):
    for i, line in enumerate(key_findings(df, m), start=1):
        st.markdown(f"**{i}.** {line}")

summary = pd.DataFrame(
    [
        {"metric": "n (synthetic)", "value": m["n"]},
        {"metric": "UPI account rate (%)", "value": m["upi_adoption_rate"]},
        {"metric": "Mean adoption score", "value": m["mean_adoption_score"]},
        {"metric": "Mean weekly UPI txns", "value": m["mean_weekly_upi"]},
        {"metric": "Mean weekly cash txns", "value": m["mean_weekly_cash"]},
        {"metric": "Mean trust (1–5)", "value": m["mean_trust"]},
        {"metric": "Fraud flag (%)", "value": m["fraud_rate"]},
    ]
)
st.download_button(
    "Download findings snapshot (CSV)",
    data=summary.to_csv(index=False).encode("utf-8"),
    file_name="beyond_cash_findings_snapshot_synthetic.csv",
    mime="text/csv",
)
