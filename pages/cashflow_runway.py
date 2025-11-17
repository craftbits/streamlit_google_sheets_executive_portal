# pages/cashflow_runway.py

import streamlit as st
import pandas as pd

import layout
from data_access import load_dataset


def _calc_cashflow(periods):
    cf = load_dataset("cashflow_items")
    cf["period"] = pd.to_datetime(cf["period"])
    cf_sel = cf[cf["period"].isin(periods)].copy()

    # Aggregate by period and item_type
    agg = (
        cf_sel.groupby(["period", "item_type"])["amount"]
        .sum()
        .unstack(fill_value=0.0)
        .reset_index()
    )

    agg["Net cash (excl opening)"] = agg.drop(columns=["period", "Opening Cash"], errors="ignore").sum(axis=1)

    # Compute ending cash sequentially
    agg = agg.sort_values("period")
    ending = []
    current_cash = 0.0
    for _, row in agg.iterrows():
        opening = row.get("Opening Cash", 0.0)
        if opening != 0:
            current_cash = opening
        current_cash += row["Net cash (excl opening)"]
        ending.append(current_cash)
    agg["Ending cash"] = ending

    return agg


def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/account_balance:", "Cashflow & runway")

        cf = load_dataset("cashflow_items")
        cf["period"] = pd.to_datetime(cf["period"])
        all_periods = sorted(cf["period"].unique())
        if not all_periods:
            st.warning("No cashflow data found.")
            return

        start = st.selectbox(
            "Start period",
            options=all_periods,
            index=max(0, len(all_periods) - 3),
            format_func=lambda d: d.strftime("%b %Y"),
        )
        end = st.selectbox(
            "End period",
            options=[p for p in all_periods if p >= start],
            index=len([p for p in all_periods if p >= start]) - 1,
            format_func=lambda d: d.strftime("%b %Y"),
        )

        periods = [p for p in all_periods if start <= p <= end]
        agg = _calc_cashflow(periods)

        # Show chart of Ending cash
        chart_df = agg.set_index("period")[["Ending cash"]]
        st.line_chart(chart_df)

        # Burn & runway calculators
        lookback = st.slider(
            "Look-back months for burn calculation",
            min_value=1,
            max_value=len(periods),
            value=min(3, len(periods)),
        )

        recent = agg.tail(lookback)
        monthly_net = recent["Net cash (excl opening)"].mean()
        ending_cash = agg["Ending cash"].iloc[-1]

        # User can overlay an adjustment to future burn
        burn_adjust_pct = st.slider(
            "Adjustment to monthly burn going forward",
            min_value=-0.5,
            max_value=0.5,
            value=0.0,
            step=0.05,
            format="%.0f%%",
        )

        adjusted_monthly_net = monthly_net * (1 + burn_adjust_pct)
        runway_months = ending_cash / abs(adjusted_monthly_net) if adjusted_monthly_net < 0 else float("inf")

        c1, c2, c3 = st.columns(3)
        with c1:
            layout.metric_card("Avg monthly net cash", f"${monthly_net:,.0f}")
        with c2:
            layout.metric_card("Adjusted monthly net", f"${adjusted_monthly_net:,.0f}")
        with c3:
            layout.metric_card(
                "Runway (months)",
                "∞" if runway_months == float("inf") else f"{runway_months:,.1f}",
            )

        st.caption(
            "Adjust the burn percentage to test new hiring plans, cost cuts, or revenue growth impact on runway."
        )


if __name__ == "__main__":
    main()