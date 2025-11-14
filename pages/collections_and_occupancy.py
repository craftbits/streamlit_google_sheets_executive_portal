import streamlit as st
import pandas as pd

import layout
from data_access import load_dataset, dataset_mtime


def _get_df() -> pd.DataFrame:
    df = load_dataset("collections", dataset_mtime("collections"))
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").dt.to_timestamp("M")
    return df



def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(
            ":material/payments:",
            "Collections and occupancy",
        )

        df = _get_df()

        month_options = sorted(df["Month"].unique())
        month = st.selectbox(
            "Period",
            options=month_options,
            index=len(month_options) - 1,
            format_func=lambda d: d.strftime("%B %Y"),
        )

        current = df[df["Month"] == month].copy()
        if current.empty:
            st.warning("No data for the selected period.")
            return

        collections_rate = current["Collection %"].mean()
        occupancy_rate = current["Occupancy %"].mean()

        c1, c2 = st.columns(2)
        with c1:
            layout.metric_card("Collections %", f"{collections_rate:.2%}")
        with c2:
            layout.metric_card("Occupancy %", f"{occupancy_rate:.2%}")

        # Table by property
        current = current.sort_values("Property")
        current["Collections %"] = current["Collection %"]
        current["Occupancy %"] = current["Occupancy %"]

        st.markdown("")
        st.dataframe(
            current[
                [
                    "Property",
                    "Date",
                    "Billed Rent",
                    "Collected Rent",
                    "Collections %",
                    "Occupancy %",
                ]
            ],
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn("Month", format="MMM YYYY"),
                "Billed Rent": st.column_config.NumberColumn(
                    "Amount billed", format="$%,.0f"
                ),
                "Collected Rent": st.column_config.NumberColumn(
                    "Amount collected", format="$%,.0f"
                ),
                "Collections %": st.column_config.NumberColumn(format="%.2f%%"),
                "Occupancy %": st.column_config.NumberColumn(format="%.2f%%"),
            },
        )

        layout.latest_data_badge(f"Collections through {month:%B %Y}")
        layout.data_sources_expander(
            ["Collections – Google Sheets (or built-in sample data)"]
        )
