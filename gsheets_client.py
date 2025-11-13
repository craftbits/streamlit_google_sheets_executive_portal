import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe
from typing import Optional

import config


@st.cache_resource(show_spinner=False)
def get_gspread_client() -> Optional[gspread.Client]:
    """
    Returns an authenticated gspread client using the service account
    JSON stored in .streamlit/secrets.toml under [gcp_service_account].

    If not configured, returns None and the app will use sample data instead.
    """
    try:
        sa_info = st.secrets["gcp_service_account"]
    except Exception:
        return None

    try:
        client = gspread.service_account_from_dict(sa_info)
        return client
    except Exception as e:
        st.warning(f"Error creating Google Sheets client: {e}")
        return None


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def load_dataset_from_sheets(dataset_key: str) -> Optional[pd.DataFrame]:
    """
    Load a dataset from Google Sheets based on the mapping in config.GOOGLE_SHEETS_CONFIG.
    Returns a pandas DataFrame or None on error.
    """
    ds_cfg = config.GOOGLE_SHEETS_CONFIG.get(dataset_key)
    if not ds_cfg:
        return None

    client = get_gspread_client()
    if client is None:
        return None

    try:
        sheet_id = ds_cfg["sheet_id"]
        worksheet_name = ds_cfg["worksheet"]
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(worksheet_name)
        df = get_as_dataframe(ws, evaluate_formulas=True, dtype=None)
        # Drop completely empty rows
        df = df.dropna(how="all")
        return df
    except Exception as e:
        st.warning(f"Could not load '{dataset_key}' from Google Sheets: {e}")
        return None
