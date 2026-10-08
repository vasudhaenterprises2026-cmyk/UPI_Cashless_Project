"""Beyond Cash — Streamlit home page (project overview)."""

import streamlit as st

from src.analysis import summary_metrics
from src.config import APP_SUBTITLE, APP_TITLE, COURSE_LINE
from src.ui import banner, get_prepared_data, page_setup

page_setup("Project Overview")

banner(
    APP_TITLE,
    APP_SUBTITLE,
)

_, _, df = get_prepared_data()
m = summary_metrics(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Synthetic records", f"{m['n']:,}", help="Rows in the bundled demonstration dataset.")
c2.metric("UPI account holders", f"{m['upi_adoption_rate']}%", help="Share of records with a UPI account.")
c3.metric("Mean adoption score", f"{m['mean_adoption_score']} / 100", help="Project-defined index; see the UPI Adoption page.")
c4.metric("Mean trust score", f"{m['mean_trust']} / 5", help="Average self-reported-style trust value generated in the synthetic data.")

st.markdown("## Project objective")
st.write(
    "Examine how UPI adoption, payment preferences, trust and security concerns vary across a "
    "demonstration sample, and show a transparent data-science workflow from cleaning through "
    "descriptive and inferential analysis."
)
st.caption(f"Course context: {COURSE_LINE} · Research topic: {APP_TITLE}: {APP_SUBTITLE}")

st.markdown("## Dataset and scope")
left, right = st.columns([1.2, 1])
with left:
    st.markdown(
        """
**Data source:** a fixed-seed, generated CSV with labelled synthetic records.  
**Unit of analysis:** one generated record per row.  
**Scope:** methods demonstration only; it is not a survey or a representative sample.
"""
    )
with right:
    st.warning(
        "Important: all records and results are synthetic/demo data. No field survey was conducted. "
        "Do not interpret these figures as evidence about real people or the wider population."
    )

st.markdown("## Research questions")
q1, q2, q3 = st.columns(3)
with q1:
    st.markdown(
        '<div class="evidence-card"><p class="eyebrow">01 · Adoption</p>'
        "<h3>How does UPI use vary?</h3>"
        "<p>How do account ownership, frequency and the project-defined adoption score differ across groups?</p></div>",
        unsafe_allow_html=True,
    )
with q2:
    st.markdown(
        '<div class="evidence-card"><p class="eyebrow">02 · Payment choice</p>'
        "<h3>How do cash and UPI coexist?</h3>"
        "<p>How do preferred mode and weekly transaction volumes compare in this dataset?</p></div>",
        unsafe_allow_html=True,
    )
with q3:
    st.markdown(
        '<div class="evidence-card"><p class="eyebrow">03 · Trust and differences</p>'
        "<h3>What patterns appear in trust?</h3>"
        "<p>How are trust, security concerns and adoption distributed across the generated groups?</p></div>",
        unsafe_allow_html=True,
    )

st.markdown("## Analysis areas")
st.write(
    "Dataset overview · data cleaning · UPI adoption · cash vs UPI · trust and security · "
    "demographic comparisons · interactive charts · statistical analysis · key findings · recommendations."
)
st.caption(
    "Use Streamlit’s sidebar navigation to open each section. Analysis-page filters subset the same "
    "dataset, and displayed results are recalculated for the selected records."
)

st.markdown(
    '<p class="footer-note">Beyond Cash · B.Sc. Data Science project prototype · synthetic data · '
    "descriptive and inferential methods demonstration, not a real-world estimate.</p>",
    unsafe_allow_html=True,
)
