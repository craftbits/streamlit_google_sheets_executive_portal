# pages/cfo_financial_overview.py

import streamlit as st
import pandas as pd

import config
import layout
from data_access import load_dataset


def _prepare_pnl(period_end: pd.Timestamp, include_budget: bool = True):
    coa = load_dataset("chart_of_accounts")
    gl = load_dataset("gl_transactions")
    gl["period"] = pd.to_datetime(gl["period"])

    # Filter to all months up to selected (YTD)
    mask = gl["period"] <= period_end
    gl_ytd = gl[mask]

    # Aggregate by account
    pnl = (
        gl_ytd.groupby("account_number")["amount"]
        .sum()
        .reset_index()
        .merge(
            coa[["account_number", "account_type", "ratio_group"]],
            on="account_number",
            how="left",
        )
    )

    # Revenue & COGS & Opex & below-the-line
    revenue = pnl[pnl["account_type"] == "Revenue"]["amount"].sum()
    cogs = pnl[pnl["account_type"] == "COGS"]["amount"].sum()
    opex = pnl[(pnl["account_type"] == "Expense") & (pnl["ratio_group"] == "Operating Expenses")]["amount"].sum()
    below = pnl[(pnl["account_type"] == "Expense") & (pnl["ratio_group"].isin(["Below-the-line"]))]["amount"].sum()

    gross_profit = revenue - cogs
    operating_profit = gross_profit - opex  # rough EBITDA before non-cash / below-the-line
    net_profit = operating_profit - below

    # Budget for YTD (optional)
    budget_df = load_dataset("budget_monthly")
    budget_df["period"] = pd.to_datetime(budget_df["period"])
    budget_mask = budget_df["period"] <= period_end
    budget_ytd = budget_df[budget_mask]

    budget_pnl = (
        budget_ytd.groupby("account_number")["budget_amount"]
        .sum()
        .reset_index()
        .merge(
            coa[["account_number", "account_type", "ratio_group"]],
            on="account_number",
            how="left",
        )
    )
    b_revenue = budget_pnl[budget_pnl["account_type"] == "Revenue"]["budget_amount"].sum()
    b_cogs = budget_pnl[budget_pnl["account_type"] == "COGS"]["budget_amount"].sum()
    b_opex = budget_pnl[
        (budget_pnl["account_type"] == "Expense") & (budget_pnl["ratio_group"] == "Operating Expenses")
    ]["budget_amount"].sum()
    b_below = budget_pnl[
        (budget_pnl["account_type"] == "Expense") & (budget_pnl["ratio_group"].isin(["Below-the-line"]))
    ]["budget_amount"].sum()

    b_gross = b_revenue - b_cogs
    b_operating = b_gross - b_opex
    b_net = b_operating - b_below

    return {
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "opex": opex,
        "operating_profit": operating_profit,
        "net_profit": net_profit,
        "budget_revenue": b_revenue,
        "budget_gross": b_gross,
        "budget_operating": b_operating,
        "budget_net": b_net,
    }


def _prepare_cash(period_end: pd.Timestamp):
    cf = load_dataset("cashflow_items")
    cf["period"] = pd.to_datetime(cf["period"])

    mask = cf["period"] <= period_end
    cf_ytd = cf[mask]

    # Opening cash: take last "Opening Cash" up to the period
    openings = cf_ytd[cf_ytd["item_type"] == "Opening Cash"].sort_values("date")
    opening_cash = openings["amount"].iloc[-1] if not openings.empty else 0.0

    # Other cash items
    other = cf_ytd[cf_ytd["item_type"] != "Opening Cash"]["amount"].sum()

    ending_cash = opening_cash + other
    return opening_cash, ending_cash


def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(
            ":material/leaderboard:",
            "CFO dashboard",
            subtitle=f"{config.COMPANY_NAME} • Financial overview",
        )

        # Period selection (assume months from GL)
        gl = load_dataset("gl_transactions")
        gl["period"] = pd.to_datetime(gl["period"])
        periods = sorted(gl["period"].unique())
        if not periods:
            st.warning("No GL data found.")
            return

        period_end = st.selectbox(
            "Reporting period (YTD through)",
            options=periods,
            index=len(periods) - 1,
            format_func=lambda d: d.strftime("%b %Y"),
        )

        pnl = _prepare_pnl(period_end)
        opening_cash, ending_cash = _prepare_cash(period_end)

        revenue = pnl["revenue"]
        gross = pnl["gross_profit"]
        net = pnl["net_profit"]

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            layout.metric_card("Revenue (YTD)", f"${revenue:,.0f}")
        with k2:
            layout.metric_card("Gross profit (YTD)", f"${gross:,.0f}")
        with k3:
            layout.metric_card("Operating profit (YTD)", f"${pnl['operating_profit']:,.0f}")
        with k4:
            layout.metric_card("Net profit (YTD)", f"${net:,.0f}")
        with k5:
            layout.metric_card("Ending cash", f"${ending_cash:,.0f}")

        layout.latest_data_badge(f"Data through {period_end:%b %Y}")
        st.divider()

        tab_pnl, tab_cash, tab_ops = st.tabs(
            ["P&L trend", "Cash & runway", "Operational KPIs"]
        )

        # --- P&L trend ---
        with tab_pnl:
            st.subheader("Revenue & profit trend")

            trend = (
                gl.groupby("period")["amount"]
                .sum()
                .reset_index()  # total not meaningful alone, so rebuild per type
            )
            # Better: build trend off P&L-style aggregation per period
            periods_df = (
                gl.groupby(["period", "account_number"])["amount"]
                .sum()
                .reset_index()
                .merge(
                    load_dataset("chart_of_accounts")[["account_number", "account_type"]],
                    on="account_number",
                    how="left",
                )
            )
            revenue_trend = (
                periods_df[periods_df["account_type"] == "Revenue"]
                .groupby("period")["amount"]
                .sum()
                .rename("Revenue")
            )
            cogs_trend = (
                periods_df[periods_df["account_type"] == "COGS"]
                .groupby("period")["amount"]
                .sum()
                .rename("COGS")
            )
            gross_trend = (revenue_trend - cogs_trend).rename("Gross profit")

            trend_df = pd.concat([revenue_trend, gross_trend], axis=1).fillna(0)
            st.line_chart(trend_df)

        # --- Cash & runway ---
        with tab_cash:
            st.subheader("Cashflow & runway")

            cf = load_dataset("cashflow_items")
            cf["period"] = pd.to_datetime(cf["period"])

            burn_window_months = st.slider(
                "Look-back window for average monthly burn",
                min_value=1,
                max_value=12,
                value=3,
            )

            # Simple burn: sum negative cash items over last N months / N
            recent_periods = sorted(cf["period"].unique())
            if recent_periods:
                cutoff = recent_periods[-burn_window_months] if len(recent_periods) >= burn_window_months else recent_periods[0]
                mask_recent = cf["period"] >= cutoff
                recent_cf = cf[mask_recent & (cf["item_type"] != "Opening Cash")]
                monthly_burn = (
                    recent_cf.groupby("period")["amount"]
                    .sum()
                    .mean()
                )
            else:
                monthly_burn = 0.0

            runway_months = ending_cash / abs(monthly_burn) if monthly_burn < 0 else float("inf")

            c1, c2 = st.columns(2)
            with c1:
                layout.metric_card("Avg monthly net cash (burn)", f"${monthly_burn:,.0f}")
            with c2:
                layout.metric_card("Runway (months)", "∞" if runway_months == float("inf") else f"{runway_months:,.1f}")

            st.caption(
                "Burn is estimated from non-opening cash movements over the selected look-back window."
            )

        # --- Operational KPIs ---
        with tab_ops:
            st.subheader("Operational KPIs")

            ops = load_dataset("operational_kpis")
            ops["period"] = pd.to_datetime(ops["period"])

            metric = st.selectbox(
                "Metric",
                options=sorted(ops["metric_name"].unique()),
            )

            metric_df = ops[ops["metric_name"] == metric].set_index("period")["metric_value"]
            st.line_chart(metric_df)

            st.caption("Operational metrics are maintained in `data/operational_kpis.csv`.")
