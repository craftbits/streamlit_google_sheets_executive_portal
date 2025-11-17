# data_access.py

from pathlib import Path
from typing import Literal, List, Optional, Dict

import pandas as pd
import streamlit as st

import config
import sample_data  # still used as a fallback


DatasetName = Literal[
    "collections",
    "financials",
    "properties",
    "chart_of_accounts",
    "gl_transactions",
    "budget_monthly",
    "cashflow_items",
    "operational_kpis",
    "model_assumptions",
]


def _get_csv_dir() -> Path:
    """
    Resolve the CSV data directory with a safe default of 'data' if
    the attribute is missing from config on the server.
    """
    csv_dir = getattr(config, "CSV_DATA_DIR", "data")
    return Path(csv_dir)


def _get_csv_datasets() -> Dict[str, str]:
    """
    Resolve the dataset name -> filename mapping with a safe default mapping
    if the attribute is missing from config on the server.
    """
    default_map: Dict[str, str] = {
        "collections": "collections.csv",
        "financials": "financials.csv",
        "properties": "properties.csv",
    }
    return getattr(config, "CSV_DATASETS", default_map)


def dataset_mtime(name: DatasetName) -> float:
    """
    Return the last-modified timestamp for the mapped CSV file.
    Used as a cache-buster so cached data refreshes when files change.
    """
    base_dir = _get_csv_dir()
    filename = _get_csv_datasets().get(name)
    if not filename:
        return 0.0
    path = base_dir / filename
    if path.exists():
        try:
            return path.stat().st_mtime
        except Exception:
            return 0.0
    return 0.0


@st.cache_data(show_spinner=False)
def load_dataset(name: DatasetName) -> pd.DataFrame:
    base_dir = _get_csv_dir()
    filename = _get_csv_datasets().get(name) or f"{name}.csv"

    if filename:
        path = base_dir / filename
        if path.exists():
            df = pd.read_csv(path)

            # Normalize types
            if name in ("collections",):
                df["Date"] = pd.to_datetime(df["Date"])
                df["Occupancy %"] = df["Occupancy %"].astype(float)
                df["Collection %"] = df["Collection %"].astype(float)

            elif name in ("financials",):
                df["Period"] = pd.to_datetime(df["Period"])

            elif name in ("properties",):
                df["Acquisition Date"] = pd.to_datetime(df["Acquisition Date"])

            elif name in ("gl_transactions",):
                df["txn_date"] = pd.to_datetime(df["txn_date"])
                if "period" in df.columns:
                    df["period"] = pd.to_datetime(df["period"])

            elif name in ("budget_monthly",):
                df["period"] = pd.to_datetime(df["period"])

            elif name in ("cashflow_items",):
                df["date"] = pd.to_datetime(df["date"])
                df["period"] = pd.to_datetime(df["period"])

            elif name in ("operational_kpis",):
                df["period"] = pd.to_datetime(df["period"])

            elif name in ("model_assumptions",):
                # base_value may be numeric or text; leave as-is
                pass

            elif name in ("chart_of_accounts",):
                # dates not needed here
                pass

            return df

    # Fallback to sample data for the legacy three datasets only
    if name == "collections":
        return sample_data.sample_collections_data()
    if name == "financials":
        return sample_data.sample_financials_data()
    if name == "properties":
        return sample_data.sample_properties_data()

    raise ValueError(f"Dataset '{name}' not found and no fallback is defined.")