import streamlit as st

import config
import layout

# Import page modules
from pages import (
    executive_overview,          # Home
    collections_and_occupancy,   # Reports
    financial_summary,           # Reports (high-level / T-12 combined for now)
    properties,                  # Reference
    scenarios,                   # We'll keep as a tool for now
    file_downloader_page,
    tax_extractor_page,
    exit_value_page,
)

# -------------------------------------------------------------------
# Global page config + CSS
# -------------------------------------------------------------------
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=":material/dashboard:",
    layout="wide",
)
layout.inject_base_css()

# Logo in sidebar (you can change paths in config.py if you like)
try:
    if config.LOGO_IMAGE:
        st.logo(config.LOGO_IMAGE, icon_image=config.LOGO_ICON)
except Exception:
    # Fallback: just show app name if logo file doesn't exist yet
    st.sidebar.title(config.COMPANY_NAME)

# -------------------------------------------------------------------
# Page definitions (Streamlit 1.38+ navigation API)
# -------------------------------------------------------------------
home_page = st.Page(
    executive_overview.main,
    title="Home",
    icon=":material/home:",
    url_path="home",
)

collections_page = st.Page(
    collections_and_occupancy.main,
    title="Collections and occupancy",
    icon=":material/payments:",
    url_path="collections",
)

financials_page = st.Page(
    financial_summary.main,
    title="T-12 / high-level financial summary",
    icon=":material/planner_review:",
    url_path="financials",
)

exit_value_page_def = st.Page(
    exit_value_page.main,
    title="Exit value",
    icon=":material/sell:",
    url_path="exit-value",
)

properties_page_def = st.Page(
    properties.main,
    title="Properties",
    icon=":material/list:",
    url_path="properties",
)

file_downloader_page_def = st.Page(
    file_downloader_page.main,
    title="Yardi file downloader",
    icon=":material/cloud_download:",
    url_path="yardi-downloader",
)

tax_extractor_page_def = st.Page(
    tax_extractor_page.main,
    title="Tax return extractor",
    icon=":material/receipt_long:",
    url_path="tax-extractor",
)

scenarios_page_def = st.Page(
    scenarios.main,
    title="Scenarios & what-if",
    icon=":material/trending_up:",
    url_path="scenarios",
)

# -------------------------------------------------------------------
# Navigation sections (matching the original app’s sidebar layout)
# -------------------------------------------------------------------
nav = st.navigation(
    {
        "": [home_page],
        "Reports": [collections_page, financials_page],
        "Value-add": [exit_value_page_def],
        "Tools": [file_downloader_page_def, tax_extractor_page_def, scenarios_page_def],
        "Reference": [properties_page_def],
    }
)

# Optional: show "logged in as" in sidebar if running in an authenticated env
if hasattr(st, "user"):
    try:
        with st.sidebar.popover(
            label=f"Logged in as **{st.user.email.split('@')[0]}**",
            icon=":material/account_circle:",
        ):
            if st.button("Log out", key="sidebar-logout", icon=":material/logout:"):
                st.logout()
    except Exception:
        # If st.user is not available (e.g. local/dev), just ignore gracefully
        pass

nav.run()
