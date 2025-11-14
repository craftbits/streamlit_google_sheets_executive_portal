import streamlit as st
import pandas as pd

import layout
from data_access import load_dataset, dataset_mtime


def _get_df() -> pd.DataFrame:
    df = load_dataset("properties", dataset_mtime("properties"))
    df["Acquisition Date"] = pd.to_datetime(df["Acquisition Date"])
    return df



def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/list:", "Properties")

        df = _get_df()

        active_props = df.shape[0]
        total_units = int(df["Units"].sum())

        m1, m2 = st.columns(2)
        with m1:
            layout.metric_card("Active properties", f"{active_props:,}")
        with m2:
            layout.metric_card("Units", f"{total_units:,}")

        st.markdown("")  # small spacing

        st.dataframe(
            df[
                [
                    "Property",
                    "Acquisition Date",
                    "City",
                    "State",
                    "Units",
                    "Management" if "Management" in df.columns else df.columns[-1],
                ]
            ],
            use_container_width=True,
            column_config={
                "Property": st.column_config.TextColumn("Asset"),
                "Acquisition Date": st.column_config.DateColumn(
                    "Purchase date", format="MMM D, YYYY"
                ),
                "Units": st.column_config.NumberColumn(format="%d"),
            },
        )

        layout.data_sources_expander(
            ["Properties – Google Sheets (or built-in sample data)"]
        )
