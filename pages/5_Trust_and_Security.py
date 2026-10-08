import plotly.express as px
import streamlit as st

from src.analysis import summary_metrics, value_share_table
from src.ui import apply_plotly, banner, get_prepared_data, page_setup, sidebar_filters

page_setup("Trust and Security")
banner(
    "Trust & Security Analysis",
    "Trust (1–5), security concern (1–5) and a synthetic fraud-experience flag. "
    "These scores were generated so that distrust tends to follow the fraud flag — they are not interview results.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

m = summary_metrics(df)
c1, c2, c3 = st.columns(3)
c1.metric("Mean trust score", f"{m['mean_trust']} / 5")
c2.metric("Mean security concern", f"{m['mean_security_concern']} / 5")
c3.metric("Fraud-experience flag", f"{m['fraud_rate']}%")
st.caption("Scores range from 1 to 5. Fraud experience is a generated flag, not a verified real-world event.")

st.markdown("## Trust and security-score distributions")
left, right = st.columns(2)
with left:
    trust_tab = value_share_table(df, "trust_score")
    fig = px.bar(
        trust_tab,
        x="category",
        y="percent",
        text="percent",
        title="Distribution of trust scores",
        labels={"category": "Trust score (1–5)", "percent": "Records (%)"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")
with right:
    sec_tab = value_share_table(df, "security_concern_score")
    fig = px.bar(
        sec_tab,
        x="category",
        y="percent",
        text="percent",
        title="Distribution of security-concern scores",
        labels={"category": "Security-concern score (1–5)", "percent": "Records (%)"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Trust and concern by fraud-experience flag")
st.caption("Group means are descriptive comparisons within the filtered synthetic records.")
by_fraud = df.groupby("fraud_experience", as_index=False).agg(
    mean_trust=("trust_score", "mean"),
    mean_concern=("security_concern_score", "mean"),
    n=("respondent_id", "count"),
).round(2)
st.dataframe(by_fraud, hide_index=True, width="stretch")

fig = px.box(
    df,
    x="fraud_experience",
    y="trust_score",
    color="fraud_experience",
    title="Trust-score distribution by synthetic fraud-experience flag",
)
st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Trust and UPI Adoption Score")
fig = px.scatter(
    df,
    x="trust_score",
    y="upi_adoption_score",
    color="area_type",
    size="weekly_upi_txns",
    hover_data=["respondent_id", "has_upi_account"],
    title="Trust score and adoption score (bubble size = weekly UPI transactions)",
)
st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Mean trust by area and account ownership")
grid = df.groupby(["area_type", "has_upi_account"], as_index=False)["trust_score"].mean().round(2)
fig = px.bar(
    grid,
    x="area_type",
    y="trust_score",
    color="has_upi_account",
    barmode="group",
    title="Mean trust score by area and UPI-account ownership",
    labels={"area_type": "Area type", "trust_score": "Mean trust score (1–5)", "has_upi_account": "Has a UPI account"},
)
st.plotly_chart(apply_plotly(fig), width="stretch")
