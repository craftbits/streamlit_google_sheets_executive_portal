# pages/pnl_statement.py

import streamlit as st
import pandas as pd

import layout
from data_access import load_dataset


def _build_pnl_matrix(periods, scenario: str = "Actual"):
    coa = load_dataset("chart_of_accounts")
    gl = load_dataset("gl_transactions")
    gl["period"] = pd.to_datetime(gl["period"])

    gl_sel = gl[gl["period"].isin(periods)]
    if scenario != "Actual":
        gl_sel = gl_sel[gl_sel["scenario"] == scenario]

    # Actual P&L pivot (account rows x period columns)
    actual = (
        gl_sel.groupby(["account_number", "period"])["amount"]
        .sum()
        .unstack(fill_value=0.0)
        .reset_index()
        .merge(coa[["account_number", "account_name", "report_class", "ratio_group"]], on="account_number", how="left")
    )

    # Budget P&L pivot
    budget_df = load_dataset("budget_monthly")
    budget_df["period"] = pd.to_datetime(budget_df["period"])
    budget_sel = budget_df[budget_df["period"].isin(periods)]

    budget = (
        budget_sel.groupby(["account_number", "period"])["budget_amount"]
        .sum()
        .unstack(fill_value=0.0)
        .reset_index()
    )

    pnl = actual.merge(budget, on="account_number", how="left", suffixes=("", "_budget"))
    return pnl, coa, periods


def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/description:", "Profit & Loss statement")

        gl = load_dataset("gl_transactions")
        gl["period"] = pd.to_datetime(gl["period"])
        all_periods = sorted(gl["period"].unique())
        if not all_periods:
            st.warning("No GL data found.")
            return

        col1, col2 = st.columns(2)
        with col1:
            start = st.selectbox(
                "Start period",
                options=all_periods,
                index=max(0, len(all_periods) - 3),
                format_func=lambda d: d.strftime("%b %Y"),
            )
        with col2:
            end = st.selectbox(
                "End period",
                options=[p for p in all_periods if p >= start],
                index=len([p for p in all_periods if p >= start]) - 1,
                format_func=lambda d: d.strftime("%b %Y"),
            )

        scenario = st.selectbox("Scenario", options=["Actual"], index=0)

        periods = [p for p in all_periods if start <= p <= end]
        pnl, coa, periods = _build_pnl_matrix(periods, scenario=scenario)

        # Build a display frame grouped by ratio_group, then account_name
        display_cols = []
        for p in periods:
            label = p.strftime("%b %Y")
            display_cols.append(label)
            pnl[label] = pnl[p].fillna(0.0)
            pnl[label + " (Budget)"] = pnl.get(str(p) + "_budget", 0.0)

        show_budget = st.checkbox("Show budget columns", value=True)

        # Sort accounts by report_class, ratio_group, account_number
        pnl = pnl.sort_values(["report_class", "ratio_group", "account_number"])

        # Prepare view
        base_cols = ["report_class", "ratio_group", "account_number", "account_name"]
        value_cols = []
        for p in periods:
            lbl = p.strftime("%b %Y")
            value_cols.append(lbl)
            if show_budget:
                value_cols.append(f"{lbl} (Budget)")

        display_df = pnl[base_cols + value_cols]

        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                c: st.column_config.NumberColumn(format="$%,.0f")
                for c in value_cols
            },
        )

        st.caption(
            "This P&L view is driven by GL transactions and chart of accounts. "
            "You can export this table via the built-in Streamlit download menu."
        )
