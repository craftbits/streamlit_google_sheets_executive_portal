"""
config.py

Central configuration for the Executive Finance Portal.

Edit this file to change:
- Company name
- Portfolio name
- Theme colors
- Google Sheets dataset IDs / worksheet names
- Executive questions
- Scenario defaults
"""

from datetime import date

# -----------------------------------------------------------------------------
# App & branding
# -----------------------------------------------------------------------------
APP_NAME = "Executive Finance Portal"
COMPANY_NAME = "ContourCFO"
DEFAULT_PORTFOLIO_NAME = "Multifamily Portfolio"
DEFAULT_CURRENCY = "USD"
LOGO_IMAGE = "assets/contour_logo.png"   # set to None if you don't have a logo yet
LOGO_ICON = "assets/contour_icon.png"    # optional small icon


# Primary teal theme (matches .streamlit/config.toml)
PRIMARY_COLOR = "#00897B"   # teal green
SECONDARY_COLOR = "#004D40"  # dark teal
LIGHT_BACKGROUND = "#E0F2F1"

# -----------------------------------------------------------------------------
# Google Sheets configuration
# -----------------------------------------------------------------------------
# Replace "YOUR_..._SHEET_ID" with actual Sheet IDs and worksheet names.
# If you leave these as-is OR if Sheets cannot be loaded, the app will
# automatically fall back to built-in sample data.
GOOGLE_SHEETS_CONFIG = {
    "collections": {
        "sheet_id": "YOUR_COLLECTIONS_SHEET_ID",
        "worksheet": "Collections",
    },
    "financials": {
        "sheet_id": "YOUR_FINANCIALS_SHEET_ID",
        "worksheet": "Financials",
    },
    "properties": {
        "sheet_id": "YOUR_PROPERTIES_SHEET_ID",
        "worksheet": "Properties",
    },
}

# -----------------------------------------------------------------------------
# Executive guidance & questions
# -----------------------------------------------------------------------------
EXEC_QUESTIONS = [
    "How is occupancy trending across the portfolio?",
    "Are collections on track versus budget?",
    "Which assets are underperforming on NOI?",
    "What is our implied portfolio value at different cap rates?",
    "Which markets are driving growth vs. underperformance?",
]

# -----------------------------------------------------------------------------
# Scenario defaults
# -----------------------------------------------------------------------------
# These give reasonable starting points for the Scenarios / What-if page.
# You can tune them to match your actual portfolio profile.
SCENARIO_DEFAULTS = {
    # Approximate current trailing NOI (USD)
    "base_noi": 18_500_000,
    # Portfolio-wide GPR (gross potential rent) per year (USD)
    "base_gpr": 30_000_000,
    # Current occupancy ratio (0-1)
    "base_occupancy": 0.96,
    # Current implied portfolio cap rate (0-1)
    "base_cap_rate": 0.055,
}

# -----------------------------------------------------------------------------
# Caching TTL (seconds) for Google Sheets reads
# -----------------------------------------------------------------------------
CACHE_TTL_SECONDS = 60 * 60  # 1 hour
