import streamlit as st
import pandas as pd

import layout
from data_access import load_dataset


def _get_financials() -> pd.DataFrame:
    df = load_dataset("financials")
    df["Period"] = pd.to_datetime(df["Period"])
    return df


def _get_properties() -> pd.DataFrame:
    df = load_dataset("properties")
    df["Acquisition Date"] = pd.to_datetime(df["Acquisition Date"])
    return df



def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/sell:", "Exit value")

        df_fin = _get_financials()
        df_prop = _get_properties()

        cap_rate_pct = st.number_input(
            "Cap rate (%)",
            min_value=3.0,
            max_value=10.0,
            value=6.0,
            step=0.25,
        )
        cap_rate = cap_rate_pct / 100.0

        # Simplified: treat available months as T-12 equivalent
        t12 = (
            df_fin.groupby("Property")
            .agg({"NOI": "sum"})
            .reset_index()
            .rename(columns={"NOI": "T-12 NOI"})
        )

        merged = df_prop.merge(t12, on="Property", how="left")
        merged["T-12 NOI"] = merged["T-12 NOI"].fillna(0)
        merged[f"Exit value at {cap_rate_pct:.2f}% cap rate"] = (
            merged["T-12 NOI"] / cap_rate
        )

        st.dataframe(
            merged[
                [
                    "Property",
                    "Acquisition Date",
                    "T-12 NOI",
                    f"Exit value at {cap_rate_pct:.2f}% cap rate",
                ]
            ],
            use_container_width=True,
            column_config={
                "Acquisition Date": st.column_config.DateColumn(
                    "Purchase date", format="MMM D, YYYY"
                ),
                "T-12 NOI": st.column_config.NumberColumn(format="$%,.0f"),
                f"Exit value at {cap_rate_pct:.2f}% cap rate": st.column_config.NumberColumn(
                    format="$%,.0f"
                ),
            },
        )

        layout.data_sources_expander(
            [
                "Financials – Google Sheets (or built-in sample data)",
                "Properties – Google Sheets (or built-in sample data)",
            ]
        )
