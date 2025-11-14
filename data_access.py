# data_access.py

from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

import config
import sample_data  # still used as a fallback


DatasetName = Literal["collections", "financials", "properties"]


@st.cache_data(show_spinner=False)
def load_dataset(name: DatasetName) -> pd.DataFrame:
    """
    Load a dataset from CSV. Falls back to sample_data.* if the CSV is missing.

    name: "collections" | "financials" | "properties"
    """
    base_dir = Path(config.CSV_DATA_DIR)
    filename = config.CSV_DATASETS.get(name)

    if filename:
        path = base_dir / filename
        if path.exists():
            df = pd.read_csv(path)

            # Parse dates & ensure dtypes
            if name == "collections":
                df["Date"] = pd.to_datetime(df["Date"])
                df["Occupancy %"] = df["Occupancy %"].astype(float)
                df["Collection %"] = df["Collection %"].astype(float)

            elif name == "financials":
                df["Period"] = pd.to_datetime(df["Period"])
                # numeric columns should already be floats, but we can be explicit if needed

            elif name == "properties":
                df["Acquisition Date"] = pd.to_datetime(df["Acquisition Date"])

            return df

    # Fallback: use in-memory sample data if CSV not present
    if name == "collections":
        return sample_data.sample_collections_data()
    if name == "financials":
        return sample_data.sample_financials_data()
    if name == "properties":
        return sample_data.sample_properties_data()

    raise ValueError(f"Unknown dataset name: {name}")
