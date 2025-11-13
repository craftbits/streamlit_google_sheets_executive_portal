# app.py

import streamlit as st
import config
import layout

# --- Global config & CSS ----------------------------------------------------
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=":material/dashboard:",
    layout="wide",
)
layout.inject_base_css()

# Logo / brand in sidebar
if getattr(config, "LOGO_IMAGE", None):
    try:
        st.logo(config.LOGO_IMAGE, icon_image=getattr(config, "LOGO_ICON", None))
    except Exception:
        st.sidebar.title(config.COMPANY_NAME)
else:
    st.sidebar.title(config.COMPANY_NAME)

# --- Define pages using FILE PATHS (native navigation) ----------------------
# Paths are relative to app.py. These must match your actual filenames
# under the pages/ directory.

home_page = st.Page(
    "pages/executive_overview.py",
    title="Home",
    icon=":material/home:",
    url_path="home",
)

collections_page = st.Page(
    "pages/collections_and_occupancy.py",
    title="Collections and occupancy",
    icon=":material/payments:",
    url_path="collections",
)

financials_page = st.Page(
    "pages/financial_summary.py",
    title="Financial summary",
    icon=":material/paid:",
    url_path="financials",
)

exit_value_page_def = st.Page(
    "pages/exit_value_page.py",
    title="Exit value",
    icon=":material/sell:",
    url_path="exit-value",
)

properties_page_def = st.Page(
    "pages/properties.py",
    title="Properties",
    icon=":material/list:",
    url_path="properties",
)

file_downloader_page_def = st.Page(
    "pages/file_downloader_page.py",
    title="Yardi file downloader",
    icon=":material/cloud_download:",
    url_path="yardi-downloader",
)

tax_extractor_page_def = st.Page(
    "pages/tax_extractor_page.py",
    title="Tax return extractor",
    icon=":material/receipt_long:",
    url_path="tax-extractor",
)

scenarios_page_def = st.Page(
    "pages/scenarios.py",
    title="Scenarios & what-if",
    icon=":material/trending_up:",
    url_path="scenarios",
)

# --- Navigation menu (native) ----------------------------------------------
pg = st.navigation(
    {
        "": [home_page],
        "Reports": [collections_page, financials_page],
        "Value-add": [exit_value_page_def],
        "Tools": [file_downloader_page_def, tax_extractor_page_def, scenarios_page_def],
        "Reference": [properties_page_def],
    },
    position="sidebar",
    expanded=True,
)

pg.run()
