import streamlit as st

import layout


def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/cloud_download:", "Yardi file downloader")

        with st.container(border=True):
            report = st.selectbox(
                "Report",
                ["Trial Balance", "Budget", "Aged Receivables", "Custom"],
            )
            asset = st.selectbox("Asset", ["All assets", "Sunset Villas", "Lakeside", "Oakwood"])
            date = st.selectbox("Date", ["Most recent", "Prior month", "Two months ago"])

            if st.button("Find", icon=":material/search:"):
                st.success(
                    f"Pretending to locate {report} for {asset} ({date}). "
                    "Wire this button to your real file store when ready."
                )
                st.download_button(
                    "Download sample file",
                    data=b"sample file contents",
                    file_name=f"{report.replace(' ', '_').lower()}_sample.csv",
                    mime="text/csv",
                )


if __name__ == "__main__":
    main()