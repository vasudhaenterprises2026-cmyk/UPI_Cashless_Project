import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from src.ui import banner, get_prepared_data, page_setup, style_matplotlib

page_setup("Data Cleaning")
banner(
    "Data Cleaning",
    "The raw file was deliberately messy (missing cells, mixed Yes/No spellings, a few impossible ages) "
    "so that cleaning steps can be shown. Nothing here is a real questionnaire edit.",
)

raw, log, clean = get_prepared_data()

st.markdown("## Quality snapshot")
raw_missing = int(raw.isna().sum().sum())
clean_missing = int(clean.isna().sum().sum())
invalid_age = int(
    (raw["age"].notna() & ~raw["age"].between(18, 90)).sum()
)
retained_rows = len(clean)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows retained", f"{retained_rows:,} / {len(raw):,}", help="Cleaning preserves every input row.")
c2.metric("Missing raw cells", f"{raw_missing:,}", help="Blank cells in the original CSV.")
c3.metric("Missing cleaned cells", f"{clean_missing:,}", help="Some optional fields remain blank when not applicable.")
c4.metric("Out-of-range ages", f"{invalid_age}", help="Non-missing ages outside the cleaning rule of 18–90.")

st.markdown("## Before cleaning")
st.write(
    "The original file intentionally includes missing values, inconsistent text labels, and a small number "
    "of implausible ages so the cleaning workflow can be demonstrated."
)
raw_missing_by_field = raw.isna().sum().rename("Missing before").to_frame()
clean_missing_by_field = clean.isna().sum().rename("Missing after").to_frame()
missing_by_field = raw_missing_by_field.join(clean_missing_by_field)
missing_by_field.index.name = "Field"
missing_by_field = missing_by_field[
    (missing_by_field["Missing before"] > 0) | (missing_by_field["Missing after"] > 0)
].reset_index()
st.dataframe(missing_by_field, hide_index=True, width="stretch")

st.markdown("## Cleaning actions")
st.markdown(
    """
- **Standardised text:** trimmed whitespace and mapped gender aliases and Yes/No variants.
- **Checked ages:** values outside 18–90 were treated as missing; missing ages were filled with the median.
- **Handled missing categories:** occupation was filled with its mode; missing income bands were labelled “Not reported”.
- **Prepared analysis fields:** converted numeric measures, bounded trust/security scores, and derived age group,
  weekly transaction totals and UPI share.
- **Preserved observations:** no rows were removed.
"""
)

st.markdown("## After cleaning")
st.write(
    "The cleaned table keeps the same number of rows. Missing values that remain are in optional or "
    "not-applicable fields (such as app names or typical UPI amount for records without UPI use)."
)
st.dataframe(log, hide_index=True, width="stretch")

st.markdown("## Missingness map in the raw file")
fig, ax = plt.subplots(figsize=(10, 4.2))
sns.heatmap(raw.isna(), cbar=False, yticklabels=False, cmap=["#1a7a6d", "#f4d6c6"], ax=ax)
ax.set_title("Raw dataset completeness · green = present · peach = missing")
ax.set_ylabel("Synthetic record")
ax.set_xlabel("Dataset field")
style_matplotlib(ax)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.caption(
    "Missing-cell totals count cells, not records. Not-applicable blanks are retained where they carry "
    "meaning; they are not automatically treated as cleaning failures."
)
