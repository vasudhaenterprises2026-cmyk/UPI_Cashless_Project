import plotly.express as px
import streamlit as st

from src.analysis import crosstab_percent, summary_metrics, value_share_table
from src.ui import apply_plotly, banner, get_prepared_data, page_setup, sidebar_filters

page_setup("Cash vs UPI")
banner(
    "Cash vs UPI Analysis",
    "Preferred payment mode and weekly transaction counts in the synthetic file. "
    "Cashless behaviour here means a higher UPI share, not the disappearance of cash.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

m = summary_metrics(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Prefer UPI", f"{m['prefer_upi']}%")
c2.metric("Prefer both", f"{m['prefer_both']}%")
c3.metric("Prefer cash", f"{m['prefer_cash']}%")
c4.metric("Mean UPI share of weekly transactions", f"{m['mean_upi_share']}%")
st.caption("Preference reflects a stated mode; the weekly UPI share is calculated from transaction counts.")

left, right = st.columns(2)
with left:
    pref = value_share_table(df, "preferred_mode")
    fig = px.pie(
        pref,
        names="category",
        values="count",
        title="Preferred payment mode",
        labels={"category": "Payment mode", "count": "Records"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")
with right:
    grouped = df.groupby("area_type", as_index=False)[["weekly_cash_txns", "weekly_upi_txns"]].mean().round(2)
    long = grouped.melt(id_vars="area_type", var_name="mode", value_name="mean_weekly_txns")
    long["mode"] = long["mode"].map({"weekly_cash_txns": "Cash", "weekly_upi_txns": "UPI"})
    fig = px.bar(
        long,
        x="area_type",
        y="mean_weekly_txns",
        color="mode",
        barmode="group",
        title="Average weekly transactions by area and payment mode",
        labels={"area_type": "Area type", "mean_weekly_txns": "Mean transactions per week", "mode": "Payment mode"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Weekly transaction volume")
c1, c2 = st.columns(2)
c1.metric("Mean weekly cash transactions", f"{m['mean_weekly_cash']}")
c2.metric("Mean weekly UPI transactions", f"{m['mean_weekly_upi']}")

fig = px.scatter(
    df,
    x="weekly_cash_txns",
    y="weekly_upi_txns",
    color="preferred_mode",
    hover_data=["respondent_id", "area_type", "age_group"],
    title="Weekly cash and UPI transactions by synthetic record",
)
st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Preferred payment mode within each area")
st.caption("Cross-tabulated percentages are row-wise: each area's preference shares sum to 100%.")
ct = crosstab_percent(df, "area_type", "preferred_mode")
st.dataframe(ct, width="stretch")
long_ct = ct.reset_index().melt(id_vars="area_type", var_name="preferred_mode", value_name="percent")
fig = px.bar(
    long_ct,
    x="area_type",
    y="percent",
    color="preferred_mode",
    barmode="stack",
    title="Payment preference mix by area",
    labels={"area_type": "Area type", "percent": "Records within area (%)", "preferred_mode": "Preferred mode"},
)
st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Nearby merchant acceptance")
merch = value_share_table(df, "merchant_acceptance_nearby")
fig = px.bar(
    merch,
    x="category",
    y="percent",
    text="percent",
    title="Reported nearby merchant acceptance",
    labels={"category": "Acceptance level", "percent": "Records (%)"},
)
st.plotly_chart(apply_plotly(fig), width="stretch")
