# app.py

import streamlit as st
import config
import layout

# Import page modules as callables
from pages import (
    executive_overview,
    collections_and_occupancy,
    financial_summary,
    properties,
    scenarios,
    file_downloader_page,
    tax_extractor_page,
    exit_value_page,
)

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

# --- Define pages using st.Page (native navigation) -------------------------
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
    title="Financial summary",
    icon=":material/paid:",
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
