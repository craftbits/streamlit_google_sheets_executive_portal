import streamlit as st

import config
import layout


def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/trending_up:", "Scenarios & what-if")

        st.caption(
            "Adjust occupancy, rent growth, and exit cap rate to explore implied "
            "portfolio value and NOI outcomes."
        )

        base_noi = config.SCENARIO_DEFAULTS["base_noi"]
        base_gpr = config.SCENARIO_DEFAULTS["base_gpr"]
        base_occ = config.SCENARIO_DEFAULTS["base_occupancy"]
        base_cap = config.SCENARIO_DEFAULTS["base_cap_rate"]

        st.markdown("### Scenario inputs")

        c1, c2 = st.columns(2)
        with c1:
            target_occ = st.slider(
                "Portfolio occupancy",
                min_value=0.85,
                max_value=0.99,
                value=float(base_occ),
                step=0.005,
                format="%.1f%%",
            )
            rent_growth = st.slider(
                "Rent growth vs current (YoY)",
                min_value=-0.05,
                max_value=0.15,
                value=0.03,
                step=0.005,
                format="%.1f%%",
            )
        with c2:
            cap_rate = st.slider(
                "Exit cap rate",
                min_value=0.035,
                max_value=0.08,
                value=float(base_cap),
                step=0.0025,
                format="%.2f%%",
            )
            expense_delta = st.slider(
                "Operating expense change",
                min_value=-0.05,
                max_value=0.10,
                value=0.0,
                step=0.005,
                format="%.1f%%",
            )

        # Convert slider display units (percent) to ratios
        target_occ_ratio = target_occ
        rent_growth_ratio = rent_growth
        cap_rate_ratio = cap_rate
        expense_delta_ratio = expense_delta

        # Scenario engine (simple, transparent)
        current_value = base_noi / base_cap if base_cap else 0

        occupancy_factor = target_occ_ratio / base_occ if base_occ else 1
        revenue_factor = 1 + rent_growth_ratio
        expense_factor = 1 + expense_delta_ratio

        projected_noi = base_noi * occupancy_factor * revenue_factor / expense_factor
        scenario_value = projected_noi / cap_rate_ratio if cap_rate_ratio else 0

        value_delta = scenario_value - current_value
        noi_delta = projected_noi - base_noi

        st.markdown("### Scenario results")

        r1, r2, r3 = st.columns(3)
        r1.metric(
            "Projected NOI",
            f"${projected_noi:,.0f}",
            f"{noi_delta / base_noi:.1%} vs base" if base_noi else None,
        )
        r2.metric(
            "Implied portfolio value",
            f"${scenario_value:,.0f}",
            f"${value_delta:,.0f} vs base",
        )
        r3.metric(
            "Current implied value (base)",
            f"${current_value:,.0f}",
            f"Cap rate {base_cap:.2%}",
        )

        st.markdown("### Notes")
        st.write(
            "- This page is meant for directional scenario analysis, not detailed asset-level "
            "underwriting.\n"
            "- You can align `config.SCENARIO_DEFAULTS` with your actual T-12 NOI, GPR, "
            "occupancy, and cap rate to make these outputs more precise."
        )
