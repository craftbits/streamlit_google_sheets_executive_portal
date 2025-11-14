import io
import streamlit as st

import layout


def main():
    left, center, right = layout.centered_columns()

    with center:
        layout.page_header(":material/receipt_long:", "Tax return extractor")

        uploaded_files = st.file_uploader(
            "Drag and drop files here",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.write(f"{len(uploaded_files)} file(s) selected.")

        if st.button("Extract", icon=":material/play_arrow:"):
            if not uploaded_files:
                st.warning("Please upload at least one PDF first.")
            else:
                with st.status("Extracting tax information...", expanded=True) as status:
                    for f in uploaded_files:
                        st.write(f"- Processed `{f.name}`")
                    status.update(label="Extraction complete", state="complete")

                # Dummy CSV as example output
                csv_bytes = io.BytesIO(b"entity,year,net_income\nExample LP,2024,123456\n")
                st.download_button(
                    "Download",
                    data=csv_bytes.getvalue(),
                    file_name="tax_extraction.csv",
                    mime="text/csv",
                )

        with st.expander("Extraction information"):
            st.write(
                "This prototype UI mirrors the original Beitel app. "
                "Replace the dummy extraction code with your actual parsing logic."
            )


if __name__ == "__main__":
    main()