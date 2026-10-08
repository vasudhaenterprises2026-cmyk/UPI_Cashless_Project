import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.analysis import chi_square_from_crosstab, pearson_corr, summary_metrics
from src.ui import banner, field_label, get_prepared_data, page_setup, sidebar_filters, style_matplotlib

page_setup("Statistical Analysis")
banner(
    "Statistical Analysis",
    "Descriptive tables, a chi-square test of association, and Pearson correlation. "
    "Tests are computed from the filtered synthetic rows. They are a methods exercise, not a claim about the population of India.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

m = summary_metrics(df)
st.markdown("## Descriptive statistics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Filtered records (n)", m["n"])
c2.metric("Mean adoption score", f"{m['mean_adoption_score']} / 100")
c3.metric("Mean trust score", f"{m['mean_trust']} / 5")
c4.metric("UPI account holders", f"{m['upi_adoption_rate']}%")

num_cols = [
    "age",
    "months_using_upi",
    "weekly_cash_txns",
    "weekly_upi_txns",
    "upi_share_weekly",
    "trust_score",
    "security_concern_score",
    "upi_adoption_score",
]
desc = df[num_cols].describe().T.round(2)
desc["median"] = df[num_cols].median().round(2)
st.dataframe(desc, width="stretch")

st.markdown("## Chi-square: area type and UPI-account ownership")
st.write(
    "The null hypothesis is that area type and UPI-account ownership are independent in this filtered file. "
    "The statistic is compared with the 5% critical value from the project's reference table. "
    "This test does not establish causation or population-wide significance."
)
observed = pd.crosstab(df["area_type"], df["has_upi_account"])
st.write("Observed counts")
st.dataframe(observed, width="stretch")
chi = chi_square_from_crosstab(observed)
st.write("Expected counts (independence)")
st.dataframe(chi["expected"], width="stretch")
st.caption("Expected counts are the values predicted under the independence assumption.")
c1, c2, c3, c4 = st.columns(4)
c1.metric("χ²", chi["chi_square"])
c2.metric("df", chi["df"])
c3.metric("Cramer's V", chi["cramers_v"])
c4.metric("Critical value (α=0.05)", chi["critical_0.05"] if chi["critical_0.05"] is not None else "—")
st.info(chi["decision"])

st.markdown("## Chi-square: gender and preferred payment mode")
obs2 = pd.crosstab(df["gender"], df["preferred_mode"])
st.dataframe(obs2, width="stretch")
chi2 = chi_square_from_crosstab(obs2)
st.write(f"χ² = {chi2['chi_square']}, df = {chi2['df']}, Cramer's V = {chi2['cramers_v']}")
st.caption(chi2["decision"])

st.markdown("## Pearson correlation")
st.write(
    "Pearson's r describes linear association between two numeric measures (−1 to +1). "
    "It does not imply that one measure causes another."
)
pairs = [
    ("trust_score", "upi_adoption_score"),
    ("trust_score", "weekly_upi_txns"),
    ("security_concern_score", "upi_adoption_score"),
    ("age", "upi_adoption_score"),
    ("months_using_upi", "weekly_upi_txns"),
]
corr_rows = []
for a, b in pairs:
    r = pearson_corr(df[a], df[b])
    strength = "weak" if abs(r) < 0.3 else "moderate" if abs(r) < 0.6 else "strong"
    corr_rows.append({"Measure 1": field_label(a), "Measure 2": field_label(b), "Pearson r": round(r, 3), "|r| reading": strength})
st.dataframe(pd.DataFrame(corr_rows), hide_index=True, width="stretch")
st.caption("|r| < 0.3 weak · 0.3–0.6 moderate · ≥ 0.6 strong (rule of thumb for this project).")

st.markdown("## Correlation heatmap")
heat_cols = num_cols
corr = df[heat_cols].corr()
fig, ax = plt.subplots(figsize=(8.5, 6.2))
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="BrBG",
    center=0,
    ax=ax,
    annot_kws={"size": 8, "color": "white" if st.session_state.get("dark_mode", False) else "#1c2b36"},
)
ax.set_title("Pearson correlation among numeric measures")
ax.set_xticklabels([field_label(label.get_text()) for label in ax.get_xticklabels()], rotation=35, ha="right")
ax.set_yticklabels([field_label(label.get_text()) for label in ax.get_yticklabels()], rotation=0)
style_matplotlib(ax)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.markdown("## Adoption-score spread by area")
fig, ax = plt.subplots(figsize=(7.5, 4.2))
sns.boxplot(data=df, x="area_type", y="upi_adoption_score", hue="area_type", palette="Set2", legend=False, ax=ax)
ax.set_title("Distribution of UPI Adoption Scores by area")
ax.set_xlabel("Area type")
ax.set_ylabel("UPI Adoption Score (0–100)")
style_matplotlib(ax)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
