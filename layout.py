"""
layout.py

Shared layout + CSS helpers so pages visually match the original Beitel-style UI:
- centered content
- metric "cards"
- consistent badges/expander
"""

from typing import Optional

import streamlit as st
import config

# -------------------------------------------------------------------
# Global CSS to tighten layout and style metric cards
# -------------------------------------------------------------------

_BASE_CSS = """
<style>
/* Reduce excessive padding and keep content nicely centered */
main .block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Simple metric card style (used on multiple pages) */
.metric-card {
    border-radius: 16px;
    padding: 1.2rem 1.6rem;
    background-color: #F9FAFB;
    border: 1px solid rgba(15, 23, 42, 0.04);
}

.metric-card-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6B7280;
    margin-bottom: 0.35rem;
}

.metric-card-value {
    font-size: 1.9rem;
    font-weight: 600;
    color: #111827;
}

/* Smaller caption under header */
.page-caption {
    color: #6B7280;
    font-size: 0.9rem;
}
</style>
"""


def inject_base_css() -> None:
    """
    Inject shared CSS once per run.

    This is what app.py is calling at startup; if this function is missing
    you will get AttributeError: 'layout' has no attribute 'inject_base_css'.
    """
    st.markdown(_BASE_CSS, unsafe_allow_html=True)


# -------------------------------------------------------------------
# Layout helpers
# -------------------------------------------------------------------

def centered_columns():
    """Return three columns with a wide center, for 'centered' page layouts."""
    return st.columns([1, 5, 1])


def page_header(icon: str, title: str, subtitle: Optional[str] = None) -> None:
    """Standard page header with optional subtitle."""
    st.header(f"{icon} {title}")
    if subtitle:
        st.markdown(
            f'<p class="page-caption">{subtitle}</p>',
            unsafe_allow_html=True,
        )


def metric_card(label: str, value: str) -> None:
    """Render a metric card using the shared CSS."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-label">{label}</div>
            <div class="metric-card-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def latest_data_badge(text: str) -> None:
    st.caption(f"Latest data: {text}")


def data_sources_expander(sources) -> None:
    with st.expander("Data sources", expanded=False):
        for src in sources:
            st.markdown(f"- {src}")


def rate_flag(value: float, good: float = 0.97, warn: float = 0.94) -> str:
    """
    Simple flag used to annotate rates (e.g. occupancy / collection).
    Returns ✅, ⚠️, or ❌.
    """
    if value is None:
        return ""
    if value >= good:
        return "✅"
    if value >= warn:
        return "⚠️"
    return "❌"
