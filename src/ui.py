"""Shared Streamlit layout, filters and Plotly theme."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis import adoption_components
from src.cleaning import get_cleaned_dataset
from src.config import APP_SUBTITLE, APP_TITLE, COURSE_LINE, DATA_DISCLAIMER, TOPIC_LINE
from src.load_data import load_raw_dataset

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,250,252,0.9)",
    font=dict(family="Source Sans 3, Segoe UI, sans-serif", color="#1c2b36", size=13),
    margin=dict(l=58, r=28, t=72, b=88),
    height=430,
    colorway=["#0f3d5e", "#1a7a6d", "#c45c26", "#4c6b8a", "#8a9a5b", "#6b4c7a"],
)


FIELD_LABELS = {
    "age": "Age (years)",
    "age_group": "Age group",
    "area_type": "Area type",
    "adoption_band": "Adoption-score band",
    "avg_upi_txn_amount_band": "Typical UPI transaction amount",
    "category": "Category",
    "count": "Records",
    "mentions": "Mentions",
    "education": "Education",
    "fraud_experience": "Synthetic fraud-experience flag",
    "gender": "Gender",
    "has_upi_account": "Has a UPI account",
    "main_barrier": "Main stated barrier",
    "mean_score": "Mean UPI Adoption Score (0–100)",
    "mean_trust": "Mean trust score (1–5)",
    "mean_concern": "Mean security-concern score (1–5)",
    "mean_weekly_txns": "Mean weekly transactions",
    "mean_weekly_upi_txns": "Mean weekly UPI transactions",
    "mean_weekly_cash_txns": "Mean weekly cash transactions",
    "mean_adoption_score": "Mean UPI Adoption Score (0–100)",
    "merchant_acceptance_nearby": "Nearby merchant acceptance",
    "monthly_income_band": "Monthly income band",
    "months_using_upi": "Months using UPI",
    "occupation": "Occupation",
    "percent": "Records (%)",
    "preferred_mode": "Preferred payment mode",
    "security_concern_score": "Security-concern score (1–5)",
    "trust_score": "Trust score (1–5)",
    "upi_adoption_score": "UPI Adoption Score (0–100)",
    "upi_apps_used": "UPI apps used",
    "upi_share_weekly": "Weekly UPI share (0–1)",
    "upi_usage_frequency": "UPI usage frequency",
    "weekly_cash_txns": "Weekly cash transactions",
    "weekly_total_txns": "Total weekly transactions",
    "weekly_upi_txns": "Weekly UPI transactions",
}


def field_label(field: str) -> str:
    """Return a presentation-friendly label for a dataset field."""
    return FIELD_LABELS.get(field, field.replace("_", " ").capitalize())


def appearance_toggle() -> bool:
    """Global Light/Dark mode shared across all pages."""

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    with st.sidebar:
        st.markdown("### 🎨 Appearance")

        st.session_state.dark_mode = st.toggle(
            "🌙 Dark Mode",
            value=st.session_state.dark_mode,
        )

    return st.session_state.dark_mode


def page_setup(page_title: str) -> None:
    st.set_page_config(
        page_title=f"{page_title} · {APP_TITLE}",
        page_icon="◇",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    dark_mode = appearance_toggle()

    st.markdown(_CSS, unsafe_allow_html=True)
    if dark_mode:
        st.markdown(_DARK_MODE_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### {APP_TITLE}")
        st.caption(APP_SUBTITLE)
        st.caption(COURSE_LINE)
        st.markdown("---")
        st.warning("Synthetic / demonstration data only. Not a real field sample.")


def banner(title: str, intro: str) -> None:
    st.markdown(f'<div class="hero"><p class="kicker">{TOPIC_LINE}</p><h1>{title}</h1><p>{intro}</p></div>', unsafe_allow_html=True)
    st.info(DATA_DISCLAIMER)


def apply_plotly(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        title=dict(x=0, xanchor="left", font=dict(size=18)),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="left",
            x=0,
        ),
        autosize=True,
    )
    fig.update_xaxes(
        title_text=field_label(fig.layout.xaxis.title.text or ""),
        showgrid=True,
        gridcolor="#e4e9ef",
        automargin=True,
    )
    fig.update_yaxes(
        title_text=field_label(fig.layout.yaxis.title.text or ""),
        showgrid=True,
        gridcolor="#e4e9ef",
        automargin=True,
    )
    if fig.layout.coloraxis and fig.layout.coloraxis.colorbar:
        colorbar_title = fig.layout.coloraxis.colorbar.title.text or ""
        fig.update_coloraxes(colorbar_title_text=field_label(colorbar_title))
    if st.session_state.get("dark_mode", False):
        fig.update_layout(
            plot_bgcolor="rgba(30,41,59,0.9)",
            font=dict(color="#f8fafc"),
        )
        fig.update_xaxes(gridcolor="#475569")
        fig.update_yaxes(gridcolor="#475569")
    else:
        fig.update_layout(plot_bgcolor="rgba(255,255,255,0.85)")
    return fig


def style_matplotlib(ax) -> None:
    """Match Matplotlib axes to the shared light/dark appearance."""
    dark_mode = st.session_state.get("dark_mode", False)
    foreground = "#f8fafc" if dark_mode else "#1c2b36"
    background = "#111827" if dark_mode else "#ffffff"
    ax.figure.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.tick_params(colors=foreground)
    ax.xaxis.label.set_color(foreground)
    ax.yaxis.label.set_color(foreground)
    ax.title.set_color(foreground)
    for spine in ax.spines.values():
        spine.set_color("#475569" if dark_mode else "#d9e3ec")


@st.cache_data(show_spinner=False)
def get_prepared_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = load_raw_dataset()
    clean, log = get_cleaned_dataset(raw)
    scored = adoption_components(clean)
    return raw, log, scored


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.markdown("#### Filters")
        areas = sorted(df["area_type"].dropna().unique().tolist())
        genders = sorted(df["gender"].dropna().unique().tolist())
        ages = [a for a in ["18–24", "25–34", "35–44", "45–54", "55+"] if a in set(df["age_group"])]
        occs = sorted(df["occupation"].dropna().unique().tolist())

        sel_area = st.multiselect("Area type", areas, default=areas)
        sel_gender = st.multiselect("Gender", genders, default=genders)
        sel_age = st.multiselect("Age group", ages, default=ages)
        sel_occ = st.multiselect("Occupation", occs, default=occs)

        filtered = df[
            df["area_type"].isin(sel_area)
            & df["gender"].isin(sel_gender)
            & df["age_group"].isin(sel_age)
            & df["occupation"].isin(sel_occ)
        ]
        st.caption(f"Showing {len(filtered)} of {len(df)} synthetic records.")
        if len(filtered) == 0:
            st.error("No rows match these filters. Restore at least one option in each list.")
        return filtered


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Fraunces:opsz,wght@9..144,560;9..144,650&display=swap');

:root {
    --bc-navy: #0f3d5e;
    --bc-teal: #1a7a6d;
    --bc-ink: #1c2b36;
    --bc-muted: #5b6b78;
    --bc-line: #d9e3ec;
    --bc-surface: #ffffff;
    --bc-canvas: #eef3f7;
}
html, body, [class*="css"] {
    font-family: "Source Sans 3", "Segoe UI", sans-serif;
}
.stApp { background: var(--bc-canvas); color: var(--bc-ink); }
.block-container {
    width: 100%;
    max-width: 1480px;
    padding: 2rem clamp(1rem, 3vw, 2.5rem) 3rem;
}
h1, h2, h3, h4 { color: var(--bc-navy); letter-spacing: -0.02em; }
h2 { margin-top: 1.8rem; padding-bottom: 0.2rem; }
h3 { margin-top: 1.25rem; }
p, li { line-height: 1.58; }
section[data-testid="stSidebar"] {
    background: #0f3d5e;
}
section[data-testid="stSidebar"] * { color: #f4f8fb !important; }
section[data-testid="stSidebar"] .stAlert { background: #1a7a6d; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label,
section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
    font-weight: 600;
}
.hero {
    background: linear-gradient(120deg, #0f3d5e 0%, #1a5f6e 58%, #1a7a6d 100%);
    color: #f7fbfc;
    padding: clamp(1.25rem, 3vw, 2.1rem);
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: 0 12px 30px rgba(15, 61, 94, 0.12);
}
.hero h1 {
    font-family: Fraunces, Georgia, serif;
    font-size: clamp(1.8rem, 3vw, 2.5rem);
    margin: 0.2rem 0 0.5rem 0;
    color: #fff;
}
.hero .kicker {
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 0.75rem;
    margin: 0;
    opacity: 0.85;
}
.hero p { margin: 0; max-width: 64rem; }
div[data-testid="stAlert"] { border-radius: 10px; }
div[data-testid="stMetric"] {
    background: var(--bc-surface);
    border: 1px solid var(--bc-line);
    padding: 0.85rem 1rem;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(15, 61, 94, 0.045);
    min-height: 100%;
}
div[data-testid="stMetricLabel"] { color: var(--bc-muted); font-weight: 600; }
div[data-testid="stMetricValue"] { color: var(--bc-navy); font-variant-numeric: tabular-nums; }
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid var(--bc-line);
    border-radius: 10px;
    overflow: hidden;
}
[data-testid="stPlotlyChart"] {
    background: var(--bc-surface);
    border: 1px solid var(--bc-line);
    border-radius: 12px;
    padding: 0.4rem;
    margin: 0.25rem 0 1rem;
    overflow: hidden;
}
.formula-box {
    background: var(--bc-surface);
    border-left: 4px solid #1a7a6d;
    padding: 1rem 1.1rem;
    border-radius: 0 10px 10px 0;
    margin: 0.6rem 0 1rem 0;
    box-shadow: 0 3px 12px rgba(15, 61, 94, 0.04);
}
.evidence-card {
    height: 100%;
    background: var(--bc-surface);
    border: 1px solid var(--bc-line);
    border-top: 3px solid var(--bc-teal);
    border-radius: 12px;
    padding: 1rem 1.1rem;
}
.evidence-card h3, .evidence-card h4 { margin-top: 0; }
.eyebrow {
    color: var(--bc-teal);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.footer-note {
    margin-top: 2rem;
    color: var(--bc-muted);
    font-size: 0.85rem;
    border-top: 1px solid var(--bc-line);
    padding-top: 1rem;
}
@media (max-width: 900px) {
    .block-container { padding-top: 1.25rem; }
    [data-testid="stPlotlyChart"] { padding: 0.15rem; }
}
@media (max-width: 600px) {
    .block-container { padding: 1rem 0.75rem 2rem; }
    .hero { border-radius: 12px; }
    div[data-testid="stMetric"] { padding: 0.7rem; }
    h2 { margin-top: 1.4rem; }
}
</style>
"""

_DARK_MODE_CSS = """
<style>
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    color: #f8fafc;
}
section[data-testid="stSidebar"] {
    background-color: #111827;
}
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}
.stMarkdown,
.stText,
p,
h1, h2, h3, h4, h5, h6 {
    color: #f8fafc;
}
div[data-testid="stMetric"] {
    background-color: #1e293b;
    border-color: #334155;
}
[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #111827;
    border-color: #334155;
}
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    color: #f8fafc;
    border-color: #334155;
}
[data-testid="stPlotlyChart"] {
    background: #111827;
    border-color: #334155;
}
[data-testid="stAlert"] {
    background-color: #1e293b;
    color: #f8fafc;
}
[data-testid="stMarkdownContainer"] a {
    color: #5eead4;
}
.formula-box {
    background-color: #1e293b;
    color: #f8fafc;
    border-color: #1a7a6d;
}
.evidence-card {
    background: #111827;
    border-color: #334155;
    border-top-color: #2dd4bf;
}
.footer-note {
    color: #cbd5e1;
    border-color: #334155;
}
</style>
"""
