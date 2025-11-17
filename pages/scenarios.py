# pages/scenarios.py

import streamlit as st
import pandas as pd

import config
import layout
from data_access import load_dataset


def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/trending_up:", "Financial scenarios")

        assumptions = load_dataset("model_assumptions")
        gl = load_dataset("gl_transactions")
        gl["period"] = pd.to_datetime(gl["period"])

        base_periods = sorted(gl["period"].unique())
        if not base_periods:
            st.warning("No GL data found.")
            return

        base_end = base_periods[-1]
        st.caption(f"Base actuals through {base_end:%b %Y}")

        # Base P&L (YTD)
        base_ytd = gl[gl["period"] <= base_end]
        pnl_base = (
            base_ytd.groupby("account_number")["amount"]
            .sum()
            .reset_index()
            .merge(
                load_dataset("chart_of_accounts")[["account_number", "account_type"]],
                on="account_number",
                how="left",
            )
        )
        base_revenue = pnl_base[pnl_base["account_type"] == "Revenue"]["amount"].sum()
        base_cogs = pnl_base[pnl_base["account_type"] == "COGS"]["amount"].sum()
        base_gross = base_revenue - base_cogs

        # Pull some assumptions
        def get_assump(key, default):
            row = assumptions[assumptions["assumption_key"] == key]
            if row.empty:
                return default
            try:
                return float(row["base_value"].iloc[0])
            except Exception:
                return default

        default_growth = get_assump("revenue_growth_rate_yoy", 0.20)
        default_gm = get_assump("gross_margin_target", 0.60)
        default_opex_pct = get_assump("opex_as_percent_revenue", 0.40)

        st.markdown("### Scenario inputs")

        c1, c2, c3 = st.columns(3)
        with c1:
            growth = st.slider(
                "Revenue growth vs base (12-month)",
                min_value=-0.5,
                max_value=0.8,
                value=float(default_growth),
                step=0.05,
                format="%.0f%%",
            )
        with c2:
            gross_margin = st.slider(
                "Target gross margin",
                min_value=0.3,
                max_value=0.85,
                value=float(default_gm),
                step=0.01,
                format="%.0f%%",
            )
        with c3:
            opex_pct = st.slider(
                "Operating expenses as % of revenue",
                min_value=0.2,
                max_value=0.8,
                value=float(default_opex_pct),
                step=0.02,
                format="%.0f%%",
            )

        target_revenue = base_revenue * (1 + growth)
        target_gross = target_revenue * gross_margin
        projected_cogs = target_revenue - target_gross
        projected_opex = target_revenue * opex_pct
        projected_ebitda = target_gross - projected_opex

        st.markdown("### Scenario results (next 12 months)")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            layout.metric_card("Revenue (12m)", f"${target_revenue:,.0f}")
        with c2:
            layout.metric_card("Gross profit", f"${target_gross:,.0f}")
        with c3:
            layout.metric_card("Operating expenses", f"${projected_opex:,.0f}")
        with c4:
            layout.metric_card("EBITDA (approx.)", f"${projected_ebitda:,.0f}")

        st.caption(
            "Tweak growth, margins, and opex to test scenarios. "
            "You can save these combinations externally as named scenarios if desired."
        )
