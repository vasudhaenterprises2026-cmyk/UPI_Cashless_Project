import pandas as pd
import streamlit as st

from src.config import DATA_SOURCE_LABEL
from src.ui import banner, get_prepared_data, page_setup

page_setup("Dataset Overview")
banner(
    "Dataset Overview",
    "Inspect the generated file: 300 demonstration rows with a visible SYNTHETIC label on every record.",
)

raw, _, clean = get_prepared_data()

st.markdown("## File facts")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows (raw)", len(raw))
c2.metric("Columns (raw)", raw.shape[1])
c3.metric("Data source label", DATA_SOURCE_LABEL)
c4.metric("Missing cells (raw)", int(raw.isna().sum().sum()))

st.markdown("## Column dictionary")
dictionary = pd.DataFrame(
    [
        ("respondent_id", "Synthetic ID such as SYN-001. Not a real person."),
        ("age", "Generated age in years (some values left missing or invalid on purpose)."),
        ("gender", "Male / Female / Other, with messy aliases in the raw file."),
        ("occupation", "Student, salaried, self-employed, homemaker, daily-wage, retired."),
        ("education", "Secondary through postgraduate."),
        ("area_type", "Urban, Semi-urban, Rural."),
        ("monthly_income_band", "Coarse income groups in rupees."),
        ("smartphone_user", "Yes/No."),
        ("has_upi_account", "Yes/No — main adoption flag."),
        ("upi_apps_used", "One or more app names, or None."),
        ("months_using_upi", "Tenure; zero if no UPI account."),
        ("upi_usage_frequency", "Daily, Weekly, Monthly, Rarely, Never."),
        ("preferred_mode", "Cash, UPI, or Both."),
        ("weekly_cash_txns", "Generated count of cash payments per week."),
        ("weekly_upi_txns", "Generated count of UPI payments per week."),
        ("avg_upi_txn_amount_band", "Typical amount band, or None."),
        ("trust_score", "1 (low) to 5 (high) trust in UPI."),
        ("security_concern_score", "1 (low concern) to 5 (high concern)."),
        ("fraud_experience", "Synthetic Yes/No flag."),
        ("main_barrier", "Main stated obstacle in the generated story."),
        ("merchant_acceptance_nearby", "Low / Medium / High."),
        ("reason_for_upi", "Why UPI is used, or Not applicable."),
        ("data_source", "Always SYNTHETIC_DEMONSTRATION."),
        ("record_type", "Plain-language reminder that the row is not a real respondent."),
    ],
    columns=["Column", "Meaning in this demonstration"],
)
st.dataframe(dictionary, hide_index=True, width="stretch")

st.markdown("## Raw preview (first 15 rows)")
st.dataframe(raw.head(15), width="stretch", hide_index=True)

st.markdown("## Cleaned preview (first 15 rows, including derived fields)")
st.dataframe(clean.head(15), width="stretch", hide_index=True)

st.markdown("## Download")
st.download_button(
    "Download raw synthetic CSV",
    data=raw.to_csv(index=False).encode("utf-8"),
    file_name="beyond_cash_synthetic_raw.csv",
    mime="text/csv",
)
st.download_button(
    "Download cleaned synthetic CSV",
    data=clean.to_csv(index=False).encode("utf-8"),
    file_name="beyond_cash_synthetic_cleaned.csv",
    mime="text/csv",
)

st.caption("Both files remain demonstration data. Do not present them as survey microdata.")
