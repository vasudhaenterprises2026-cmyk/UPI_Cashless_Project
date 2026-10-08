import pandas as pd
import streamlit as st

from src.analysis import summary_metrics
from src.insights import recommendations
from src.ui import banner, get_prepared_data, page_setup, sidebar_filters

page_setup("Recommendations")
banner(
    "Recommendations",
    "Suggestions below are cautious interpretations of the demonstration file. "
    "They are written as ideas a student might discuss in a viva, not as policy advice based on real interviews.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

m = summary_metrics(df)
st.markdown("## Evidence-led recommendations")
st.write(
    "These are conditional ideas for discussion, not policy recommendations. Each is linked to a "
    "calculated pattern in the filtered synthetic records and should be tested with real, appropriately "
    "sampled data before drawing practical conclusions."
)

recommendation_items = recommendations(df, m)
for start in range(0, len(recommendation_items), 2):
    columns = st.columns(2)
    for column, rec in zip(columns, recommendation_items[start : start + 2]):
        with column:
            with st.container(border=True):
                st.markdown(f"### {rec['title']}")
                st.write(rec["text"])
                st.markdown("**Supporting evidence**")
                st.caption(rec["evidence"])

st.markdown("## Research integrity and limitations")
st.write(
    "It does not estimate national UPI adoption, does not evaluate any bank or app, "
    "and does not replace a supervised field survey. If the project is later extended with real consent-based data, "
    "keep that file separate from `synthetic_upi_survey.csv`."
)

st.markdown("### Download centre")
st.download_button(
    "Download filtered synthetic data (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="beyond_cash_filtered_synthetic.csv",
    mime="text/csv",
)

rec_table = pd.DataFrame(recommendations(df, m))
st.download_button(
    "Download recommendation text (CSV)",
    data=rec_table.to_csv(index=False).encode("utf-8"),
    file_name="beyond_cash_recommendations_synthetic.csv",
    mime="text/csv",
)
