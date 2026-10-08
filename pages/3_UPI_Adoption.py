import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import score_formula_text, summary_metrics, value_share_table
from src.config import ADOPTION_WEIGHTS, FREQUENCY_POINTS, PREFERENCE_POINTS, TENURE_CAP_MONTHS
from src.ui import apply_plotly, banner, get_prepared_data, page_setup, sidebar_filters

page_setup("UPI Adoption")
banner(
    "UPI Adoption Analysis",
    "Account ownership, usage frequency, apps, barriers, and a transparent UPI Adoption Score "
    "built only from this synthetic table.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

m = summary_metrics(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("UPI account holders", f"{m['upi_adoption_rate']}%", help="Share of filtered records with a UPI account.")
c2.metric("Mean adoption score", f"{m['mean_adoption_score']} / 100")
c3.metric("Median adoption score", f"{m['median_adoption_score']} / 100")
c4.metric("Smartphone users", f"{m['smartphone_rate']}%")

st.markdown("## UPI Adoption Score: definition")
st.write(
    "This project-defined index combines account ownership, usage frequency, weekly digital share, "
    "tenure and preferred mode. It is a teaching measure, not an official UPI indicator."
)
st.markdown(f'<div class="formula-box"><strong>{score_formula_text()}</strong></div>', unsafe_allow_html=True)

w = ADOPTION_WEIGHTS
formula_table = pd.DataFrame(
    [
        {
            "Component": "Account",
            "Weight": f"{w['account']:.0%}",
            "Scale (0–100)": "100 if has_upi_account is Yes, else 0",
        },
        {
            "Component": "Frequency",
            "Weight": f"{w['frequency']:.0%}",
            "Scale (0–100)": ", ".join(f"{k}={v}" for k, v in FREQUENCY_POINTS.items()),
        },
        {
            "Component": "Digital share",
            "Weight": f"{w['digital_share']:.0%}",
            "Scale (0–100)": "100 × weekly UPI txns / (weekly UPI + weekly cash)",
        },
        {
            "Component": "Tenure",
            "Weight": f"{w['tenure']:.0%}",
            "Scale (0–100)": f"min(months_using_upi, {TENURE_CAP_MONTHS}) / {TENURE_CAP_MONTHS} × 100",
        },
        {
            "Component": "Preference",
            "Weight": f"{w['preference']:.0%}",
            "Scale (0–100)": ", ".join(f"{k}={v}" for k, v in PREFERENCE_POINTS.items()),
        },
    ]
)
st.dataframe(formula_table, hide_index=True, width="stretch")
st.caption(
    "Bands: Low (0–39.9), Moderate (40–69.9), High (70–100). "
    "The score is a project-defined index, not an official NPCI or RBI measure."
)

st.markdown("## Worked example from the filtered sample")
example = df.iloc[0]
st.write(
    f"Record `{example['respondent_id']}` (synthetic): "
    f"account component {example['comp_account']:.0f}, "
    f"frequency {example['comp_frequency']:.0f}, "
    f"digital share {example['comp_digital_share']:.1f}, "
    f"tenure {example['comp_tenure']:.1f}, "
    f"preference {example['comp_preference']:.0f} → "
    f"**score {example['upi_adoption_score']}** ({example['adoption_band']})."
)

left, right = st.columns(2)
with left:
    acc = value_share_table(df, "has_upi_account")
    fig = px.pie(
        acc,
        names="category",
        values="count",
        title="UPI account ownership",
        labels={"category": "Account status", "count": "Records"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")
with right:
    freq = value_share_table(df, "upi_usage_frequency")
    fig = px.bar(
        freq,
        x="category",
        y="percent",
        title="UPI usage frequency in the filtered sample",
        text="percent",
        labels={"category": "Usage frequency", "percent": "Records (%)"},
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Adoption profile and barriers")
st.caption("The following percentages use the currently filtered records.")
left, right = st.columns(2)
with left:
    bands = value_share_table(df, "adoption_band")
    order = ["Low", "Moderate", "High"]
    bands["category"] = pd.Categorical(bands["category"], order, ordered=True)
    bands = bands.sort_values("category")
    fig = px.bar(
        bands,
        x="category",
        y="percent",
        title="Distribution across adoption-score bands",
        text="percent",
        labels={"category": "Adoption-score band", "percent": "Records (%)"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")
with right:
    barriers = value_share_table(df, "main_barrier")
    fig = px.bar(
        barriers,
        y="category",
        x="percent",
        orientation="h",
        title="Most common stated barriers",
        labels={"category": "Main stated barrier", "percent": "Records (%)"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Apps named among UPI-account records")
apps = (
    df.loc[df["has_upi_account"].eq("Yes"), "upi_apps_used"]
    .fillna("")
    .str.split(",")
    .explode()
    .str.strip()
)
apps = apps[apps.ne("") & apps.ne("None")]
if len(apps):
    app_tab = apps.value_counts().rename("mentions").reset_index()
    app_tab.columns = ["app", "mentions"]
    fig = px.bar(
        app_tab,
        x="app",
        y="mentions",
        title="UPI app mentions (a record can list multiple apps)",
        labels={"app": "UPI app", "mentions": "Mentions"},
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")
else:
    st.write("No UPI-account rows in the current filter.")

st.markdown("## Mean adoption score by area")
by_area = df.groupby("area_type", as_index=False)["upi_adoption_score"].mean().round(1)
fig = px.bar(
    by_area,
    x="area_type",
    y="upi_adoption_score",
    text="upi_adoption_score",
    title="Mean UPI Adoption Score by area",
)
st.plotly_chart(apply_plotly(fig), width="stretch")
