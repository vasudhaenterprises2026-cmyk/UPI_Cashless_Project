import plotly.express as px
import streamlit as st

from src.ui import apply_plotly, banner, field_label, get_prepared_data, page_setup, sidebar_filters

page_setup("Interactive Charts")
banner(
    "Interactive Charts",
    "Filter the synthetic table and choose what to plot. Charts update from the filtered rows only.",
)

_, _, scored = get_prepared_data()
df = sidebar_filters(scored)
if len(df) == 0:
    st.stop()

st.markdown("## Build a chart")
st.write("Choose the visual form and fields. The chart updates from the records currently selected in the sidebar.")
numeric = [
    "upi_adoption_score",
    "trust_score",
    "security_concern_score",
    "weekly_upi_txns",
    "weekly_cash_txns",
    "upi_share_weekly",
    "months_using_upi",
    "age",
]
categorical = [
    "area_type",
    "gender",
    "age_group",
    "occupation",
    "education",
    "preferred_mode",
    "has_upi_account",
    "adoption_band",
    "merchant_acceptance_nearby",
]

chart_type = st.selectbox("Chart type", ["Scatter", "Box", "Bar (mean)", "Histogram"])
c1, c2, c3 = st.columns(3)
with c1:
    x = st.selectbox("X-axis field", categorical + numeric, index=0, format_func=field_label)
with c2:
    y = st.selectbox("Y-axis measure", numeric, index=0, format_func=field_label)
with c3:
    colour = st.selectbox(
        "Colour grouping",
        ["(none)"] + categorical,
        index=1,
        format_func=lambda value: "No grouping" if value == "(none)" else field_label(value),
    )

color_arg = None if colour == "(none)" else colour

if chart_type == "Scatter":
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color_arg,
        hover_data=["respondent_id"],
        title=f"{field_label(y)} by {field_label(x)}",
    )
elif chart_type == "Box":
    fig = px.box(
        df,
        x=x,
        y=y,
        color=color_arg,
        title=f"Distribution of {field_label(y)} by {field_label(x)}",
    )
elif chart_type == "Bar (mean)":
    group_cols = [x] if color_arg is None else [x, color_arg]
    grouped = df.groupby(group_cols, as_index=False)[y].mean()
    fig = px.bar(
        grouped,
        x=x,
        y=y,
        color=color_arg,
        barmode="group",
        title=f"Mean {field_label(y)} by {field_label(x)}",
    )
else:
    fig = px.histogram(
        df,
        x=y,
        color=color_arg,
        nbins=20,
        title=f"Distribution of {field_label(y)}",
    )

st.plotly_chart(apply_plotly(fig), width="stretch")

st.markdown("## Relationships among trust, concern and adoption")
fig = px.scatter_matrix(
    df,
    dimensions=["trust_score", "security_concern_score", "upi_adoption_score", "weekly_upi_txns"],
    color="area_type",
    title="Pairwise relationships: trust, security concern, adoption and weekly UPI use",
)
st.plotly_chart(apply_plotly(fig), width="stretch")
