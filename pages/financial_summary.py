import streamlit as st
import pandas as pd
import altair as alt

import layout
from data_access import load_dataset


def _get_df() -> pd.DataFrame:
    df = load_dataset("financials")
    df["Period"] = pd.to_datetime(df["Period"])
    df["Month"] = df["Period"].dt.to_period("M").dt.to_timestamp("M")
    return df



def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/paid:", "Financial summary")

        df = _get_df()

        months = sorted(df["Month"].unique())
        regions = sorted(df["Region"].unique())
        properties = sorted(df["Property"].unique())

        f1, f2, f3 = st.columns(3)
        selected_month = f1.selectbox(
            "Period (month)",
            options=months,
            index=len(months) - 1,
            format_func=lambda d: d.strftime("%b %Y"),
        )
        selected_regions = f2.multiselect(
            "Regions",
            options=regions,
            default=regions,
        )
        selected_properties = f3.multiselect(
            "Properties",
            options=properties,
            default=properties,
        )

        mask = df["Month"] == selected_month
        if selected_regions:
            mask &= df["Region"].isin(selected_regions)
        if selected_properties:
            mask &= df["Property"].isin(selected_properties)

        view_df = df[mask].copy()
        if view_df.empty:
            st.warning("No data for the selected filters.")
            return

        # Portfolio metrics
        total_rev = view_df["Revenue"].sum()
        total_opex = view_df["Operating Expenses"].sum()
        total_noi = view_df["NOI"].sum()
        total_budget_noi = view_df["Budget NOI"].sum()
        noi_var = total_noi - total_budget_noi
        noi_margin = total_noi / total_rev if total_rev else 0

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Revenue", f"${total_rev:,.0f}")
        k2.metric("Operating expenses", f"${total_opex:,.0f}")
        k3.metric("NOI", f"${total_noi:,.0f}")
        k4.metric("NOI margin", f"{noi_margin:.1%}")
        k5.metric("NOI vs budget", f"${noi_var:,.0f}")

        st.markdown("### NOI vs budget by property")
        agg = (
            view_df.groupby(["Property", "Region"])
            .agg(
                Revenue=("Revenue", "sum"),
                NOI=("NOI", "sum"),
                Budget_NOI=("Budget NOI", "sum"),
                NOI_Variance=("NOI Variance", "sum"),
                NOI_Margin=("NOI Margin", "mean"),
            )
            .reset_index()
        )
        agg["NOI Margin %"] = agg["NOI_Margin"]

        st.dataframe(
            agg[
                [
                    "Property",
                    "Region",
                    "Revenue",
                    "NOI",
                    "Budget_NOI",
                    "NOI_Variance",
                    "NOI Margin %",  # percent
                ]
            ],
            use_container_width=True,
            column_config={
                "Revenue": st.column_config.NumberColumn(format="$%,.0f"),
                "NOI": st.column_config.NumberColumn(format="$%,.0f"),
                "Budget_NOI": st.column_config.NumberColumn("Budget NOI", format="$%,.0f"),
                "NOI_Variance": st.column_config.NumberColumn("NOI variance", format="$%,.0f"),
                "NOI Margin %": st.column_config.NumberColumn("NOI margin", format="%.1f%%"),
            },
        )

        st.markdown("### NOI trend")
        trend = (
            df.groupby("Month")
            .agg(NOI=("NOI", "sum"), Budget_NOI=("Budget NOI", "sum"))
            .reset_index()
            .sort_values("Month")
        )
        trend_long = trend.melt(id_vars=["Month"], value_vars=["NOI", "Budget_NOI"], var_name="Series", value_name="Value")
        chart = (
            alt.Chart(trend_long)
            .mark_line(point=True)
            .encode(
                x=alt.X("Month:T", title="Month"),
                y=alt.Y("Value:Q", title="Amount"),
                color=alt.Color("Series:N", title=None),
                tooltip=[alt.Tooltip("Month:T", title="Month"), alt.Tooltip("Series:N"), alt.Tooltip("Value:Q", title="Amount", format=",.0f")],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)

        layout.latest_data_badge(f"Financials through {selected_month:%b %Y}")
        layout.data_sources_expander(
            ["Financials – Google Sheets dataset 'financials' (or built-in sample data)"]
        )


if __name__ == "__main__":
    main()
