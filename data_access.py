# data_access.py

from pathlib import Path
from typing import Literal, List

import pandas as pd
import streamlit as st

import config
import sample_data  # still used as a fallback


DatasetName = Literal["collections", "financials", "properties"]


def dataset_mtime(name: DatasetName) -> float:
    """
    Return the last-modified timestamp for the mapped CSV file.
    Used as a cache-buster so cached data refreshes when files change.
    """
    base_dir = Path(config.CSV_DATA_DIR)
    filename = config.CSV_DATASETS.get(name)
    if not filename:
        return 0.0
    path = base_dir / filename
    if path.exists():
        try:
            return path.stat().st_mtime
        except Exception:
            return 0.0
    return 0.0


@st.cache_data(show_spinner=False, ttl=config.CACHE_TTL_SECONDS)
def load_dataset(name: DatasetName, _cache_buster: float | None = None) -> pd.DataFrame:
    """
    Load a dataset from CSV. Falls back to sample_data.* if the CSV is missing
    or if required columns are not present.

    name: "collections" | "financials" | "properties"
    _cache_buster: pass dataset_mtime(name) so cache refreshes when CSV updates
    """
    base_dir = Path(config.CSV_DATA_DIR)
    filename = config.CSV_DATASETS.get(name)

    if filename:
        path = base_dir / filename
        if path.exists():
            df = pd.read_csv(path)

            # Parse dates & ensure dtypes
            if name == "collections":
                # Required columns (light schema guard)
                required: List[str] = [
                    "Date",
                    "Property",
                    "Billed Rent",
                    "Collected Rent",
                    "Occupancy %",
                    "Collection %",
                ]
                missing = [c for c in required if c not in df.columns]
                if missing:
                    st.warning(
                        f"Collections CSV missing columns: {missing}. Falling back to sample data."
                    )
                    return sample_data.sample_collections_data()

                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                for col in ["Occupancy %", "Collection %", "Billed Rent", "Collected Rent", "Total Units", "Occupied Units"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            elif name == "financials":
                required = [
                    "Period",
                    "Property",
                    "Revenue",
                    "Operating Expenses",
                    "NOI",
                    "Budget NOI",
                    "NOI Variance",
                    "NOI Margin",
                ]
                missing = [c for c in required if c not in df.columns]
                if missing:
                    st.warning(
                        f"Financials CSV missing columns: {missing}. Falling back to sample data."
                    )
                    return sample_data.sample_financials_data()

                df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
                for col in [
                    "Revenue",
                    "Operating Expenses",
                    "NOI",
                    "Budget NOI",
                    "NOI Variance",
                    "NOI Margin",
                ]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            elif name == "properties":
                required = ["Property", "Acquisition Date", "Units"]
                missing = [c for c in required if c not in df.columns]
                if missing:
                    st.warning(
                        f"Properties CSV missing columns: {missing}. Falling back to sample data."
                    )
                    return sample_data.sample_properties_data()

                df["Acquisition Date"] = pd.to_datetime(df["Acquisition Date"], errors="coerce")
                for col in ["Units", "Latest Value"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")

            return df

    # Fallback: use in-memory sample data if CSV not present
    if name == "collections":
        return sample_data.sample_collections_data()
    if name == "financials":
        return sample_data.sample_financials_data()
    if name == "properties":
        return sample_data.sample_properties_data()

    raise ValueError(f"Unknown dataset name: {name}")
