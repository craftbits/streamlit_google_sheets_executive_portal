# pages/executive_overview.py

import streamlit as st
import pandas as pd

import config
import layout
from data_access import load_dataset, dataset_mtime


# ---------- Data helpers ----------

def _get_collections_df() -> pd.DataFrame:
    df = load_dataset("collections", dataset_mtime("collections"))
    # already parsed in data_access, but harmless to ensure:
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def _get_financials_df() -> pd.DataFrame:
    df = load_dataset("financials", dataset_mtime("financials"))
    df["Period"] = pd.to_datetime(df["Period"])
    return df


def _get_properties_df() -> pd.DataFrame:
    df = load_dataset("properties", dataset_mtime("properties"))
    df["Acquisition Date"] = pd.to_datetime(df["Acquisition Date"])
    return df


# ---------- Page entrypoint ----------

def main() -> None:
    """Minimal placeholder so st.Page(executive_overview.main) works."""
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(
            ":material/insights:",
            "Executive overview",
            subtitle=f"{config.COMPANY_NAME} • {config.DEFAULT_PORTFOLIO_NAME}",
        )
        st.write(
            "This is a temporary placeholder for the Executive overview page.\n\n"
            "If you're seeing this, the navigation wiring is working. "
            "We can then drop in the full KPI + tabs UI."
        )

        # ----- Load data -----
        df_coll = _get_collections_df()
        df_fin = _get_financials_df()
        df_prop = _get_properties_df()

        # ----- Portfolio KPIs -----
        latest_coll_date = df_coll["Date"].max()
        curr_coll = df_coll[df_coll["Date"] == latest_coll_date]

        portfolio_occupancy = curr_coll["Occupancy %"].mean()
        collection_rate = curr_coll["Collection %"].mean()

        latest_fin_period = df_fin["Period"].max()
        fin_latest = df_fin[df_fin["Period"] == latest_fin_period]
        portfolio_noi = fin_latest["NOI"].sum()
        noi_margin = fin_latest["NOI Margin"].mean()

        total_units = int(df_prop["Units"].sum())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Portfolio occupancy", f"{portfolio_occupancy:.1%}")
        k2.metric("Collection rate", f"{collection_rate:.1%}")
        k3.metric("T-12 NOI", f"${portfolio_noi:,.0f}")
        k4.metric("Total units", f"{total_units:,}")

        layout.latest_data_badge(
            f"Collections through {latest_coll_date:%b %Y} • "
            f"Financials through {latest_fin_period:%b %Y}"
        )

        st.divider()

        # ----- Tabs: snapshot / trends / risk / questions -----
        tab_snap, tab_trends, tab_risk, tab_q = st.tabs(
            ["Portfolio snapshot", "Trends", "Risk & exceptions", "Executive questions"]
        )

        # Snapshot
        with tab_snap:
            st.subheader("Snapshot by region")

            snap = (
                curr_coll.groupby("Region")
                .agg(
                    Units=("Total Units", "sum"),
                    Occupancy=("Occupancy %", "mean"),
                    Collection=("Collection %", "mean"),
                    Billed_Rent=("Billed Rent", "sum"),
                    Collected_Rent=("Collected Rent", "sum"),
                )
                .reset_index()
            )
            snap["Occupancy %"] = snap["Occupancy"]
            snap["Collection %"] = snap["Collection"]

            st.dataframe(
                snap[
                    [
                        "Region",
                        "Units",
                        "Occupancy %",
                        "Collection %",
                        "Billed_Rent",
                        "Collected_Rent",
                    ]
                ],
                use_container_width=True,
                column_config={
                    "Units": st.column_config.NumberColumn(format="%d"),
                    "Occupancy %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Collection %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Billed_Rent": st.column_config.NumberColumn(
                        "Billed rent", format="$%,.0f"
                    ),
                    "Collected_Rent": st.column_config.NumberColumn(
                        "Collected rent", format="$%,.0f"
                    ),
                },
            )

        # Trends
        with tab_trends:
            st.subheader("Occupancy & collections trend")

            coll_trend = (
                df_coll.groupby("Date")
                .agg(
                    Occupancy=("Occupancy %", "mean"),
                    Collection=("Collection %", "mean"),
                )
                .reset_index()
                .sort_values("Date")
            )
            st.line_chart(
                coll_trend.set_index("Date")[["Occupancy", "Collection"]]
            )

            st.subheader("NOI trend")

            fin_trend = (
                df_fin.groupby("Period")
                .agg(NOI=("NOI", "sum"))
                .reset_index()
                .sort_values("Period")
            )
            st.line_chart(fin_trend.set_index("Period")[["NOI"]])

        # Risk & exceptions
        with tab_risk:
            st.subheader("Assets below threshold")

            threshold_occ = st.slider(
                "Minimum occupancy threshold", 0.85, 0.99, 0.92, 0.01
            )
            threshold_coll = st.slider(
                "Minimum collection threshold", 0.85, 0.99, 0.94, 0.01
            )

            curr_coll["Occ Flag"] = curr_coll["Occupancy %"].apply(
                lambda v: layout.rate_flag(v, good=threshold_occ + 0.02, warn=threshold_occ)
            )
            curr_coll["Coll Flag"] = curr_coll["Collection %"].apply(
                lambda v: layout.rate_flag(v, good=threshold_coll + 0.02, warn=threshold_coll)
            )

            risk_df = curr_coll[
                (curr_coll["Occupancy %"] < threshold_occ)
                | (curr_coll["Collection %"] < threshold_coll)
            ]

            if risk_df.empty:
                st.success("No assets currently breaching the selected thresholds.")
            else:
                st.dataframe(
                    risk_df[
                        [
                            "Property",
                            "Region",
                            "Total Units",
                            "Occupancy %",
                            "Collection %",
                            "Occ Flag",
                            "Coll Flag",
                            "Billed Rent",
                            "Collected Rent",
                        ]
                    ],
                    use_container_width=True,
                    column_config={
                        "Total Units": st.column_config.NumberColumn(format="%d"),
                        "Occupancy %": st.column_config.NumberColumn(format="%.1f%%"),
                        "Collection %": st.column_config.NumberColumn(format="%.1f%%"),
                        "Billed Rent": st.column_config.NumberColumn(
                            "Billed rent", format="$%,.0f"
                        ),
                        "Collected Rent": st.column_config.NumberColumn(
                            "Collected rent", format="$%,.0f"
                        ),
                    },
                )

        # Exec questions tab
        with tab_q:
            st.subheader("Quick questions to explore")
            st.write("Use the navigation on the left to drill into details:")
            for q in config.EXEC_QUESTIONS:
                st.markdown(f"- {q}")

        layout.data_sources_expander(
            [
                "Collections – Google Sheets dataset 'collections' (or sample data)",
                "Financials – Google Sheets dataset 'financials' (or sample data)",
                "Properties – Google Sheets dataset 'properties' (or sample data)",
            ]
        )


# Optional: if this file is ever used directly as a page via st.Page('pages/executive_overview.py')
if __name__ == "__page__":
    main()
