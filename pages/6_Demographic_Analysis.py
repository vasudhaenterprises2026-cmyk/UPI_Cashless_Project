import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import crosstab_percent, summary_metrics
from src.ui import apply_plotly, banner, get_prepared_data, page_setup, sidebar_filters

page_setup("Demographic Analysis")
banner(
    "Demographic Analysis",
    "Adoption score and UPI-account rate across age, gender, occupation, education and income in the synthetic file.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

m = summary_metrics(df)
st.caption(
    f"Filtered synthetic records: {m['n']}. All percentages and group means below use this subset."
)

age_order = ["18–24", "25–34", "35–44", "45–54", "55+"]

st.markdown("## Mean adoption score by age group")
by_age = df.groupby("age_group", as_index=False).agg(
    mean_score=("upi_adoption_score", "mean"),
    upi_rate=("has_upi_account", lambda s: (s.eq("Yes").mean() * 100)),
    n=("respondent_id", "count"),
)
present = [c for c in age_order if c in set(by_age["age_group"])]
by_age["age_group"] = pd.Categorical(by_age["age_group"], categories=present, ordered=True)
by_age = by_age.sort_values("age_group").round(1)
st.dataframe(by_age, hide_index=True, width="stretch")
fig = px.bar(
    by_age,
    x="age_group",
    y="mean_score",
    text="mean_score",
    title="Mean UPI Adoption Score by age group",
    labels={"age_group": "Age group", "mean_score": "Mean UPI Adoption Score (0–100)"},
)
st.plotly_chart(apply_plotly(fig), width="stretch")

left, right = st.columns(2)
with left:
    st.markdown("### UPI-account ownership by gender")
    st.dataframe(crosstab_percent(df, "gender", "has_upi_account"), width="stretch")
    g = df.groupby("gender", as_index=False)["upi_adoption_score"].mean().round(1)
    fig = px.bar(
        g,
        x="gender",
        y="upi_adoption_score",
        title="Mean UPI Adoption Score by gender",
    )
    st.plotly_chart(apply_plotly(fig), width="stretch")
with right:
    st.markdown("### UPI-account ownership by occupation")
    st.dataframe(crosstab_percent(df, "occupation", "has_upi_account"), width="stretch")
    o = df.groupby("occupation", as_index=False)["upi_adoption_score"].mean().round(1)
    fig = px.bar(
        o,
        x="occupation",
        y="upi_adoption_score",
        title="Mean UPI Adoption Score by occupation",
    )
    fig.update_xaxes(tickangle=25)
    st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Education and income")
e = df.groupby("education", as_index=False).agg(
    mean_score=("upi_adoption_score", "mean"),
    n=("respondent_id", "count"),
).round(1)
fig = px.bar(
    e,
    x="education",
    y="mean_score",
    title="Mean UPI Adoption Score by education level",
    labels={"education": "Education level", "mean_score": "Mean UPI Adoption Score (0–100)"},
)
st.plotly_chart(apply_plotly(fig), width="stretch")

inc = df.groupby("monthly_income_band", as_index=False)["upi_adoption_score"].mean().round(1)
fig = px.bar(
    inc,
    x="monthly_income_band",
    y="upi_adoption_score",
    title="Mean UPI Adoption Score by monthly income band",
)
fig.update_xaxes(tickangle=20)
st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Area × age: mean adoption score")
st.caption("Cells show the average project-defined adoption score for each area and age-group combination.")
heat = df.pivot_table(index="age_group", columns="area_type", values="upi_adoption_score", aggfunc="mean")
heat = heat.reindex([c for c in age_order if c in heat.index])
st.dataframe(heat.round(1), width="stretch")
fig = px.imshow(
    heat.round(1),
    text_auto=True,
    color_continuous_scale="Teal",
    title="Mean UPI Adoption Score by area and age group",
    labels={"x": "Area type", "y": "Age group", "color": "Mean score (0–100)"},
)
st.plotly_chart(apply_plotly(fig), width="stretch")
