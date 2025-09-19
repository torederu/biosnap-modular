import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path
from utils.toxicology_utils import extract_results_to_dataframe, humanize_result_text


def toxicology_tab(username: str, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Toxicology</h1>", unsafe_allow_html=True)
    
    # Check if this is T02 - no data collected
    if timepoint_id == "T_02":
        st.info("No toxicology data were collected for Time Point 02.")
        return
    
    user_supabase = get_user_supabase()
    bucket = user_supabase.storage.from_("data")
    csv_key = build_supabase_path(username, timepoint_id, "toxicology.csv")

    # Check if CSV already exists
    file_list = bucket.list(path=f"{username}/{timepoint_modifier}/")
    csv_exists = any(f["name"] == "toxicology.csv" for f in file_list)

    if csv_exists:
        try:
            csv_bytes = bucket.download(csv_key)
            if isinstance(csv_bytes, bytes):
                df = pd.read_csv(io.BytesIO(csv_bytes))
                if "Result" in df.columns:
                    df["Result"] = df["Result"].astype(str).apply(humanize_result_text)
                st.markdown("Double-click any cell to reveal its full contents.")
                st.dataframe(df)
                st.success("Upload successful!")
            else:
                st.error("Failed to retrieve the file. Please try again.")
        except Exception as e:
            st.error(f"Error retrieving file: {e}")
    else:
        st.markdown("<div style='font-size:17.5px; line-height:1.6'>Please upload your toxicology report:</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='font-size:15px; line-height:1.6; margin-bottom:0.5rem; padding-left:1.5rem'>
              <ol style="margin-top: 0; margin-bottom: 0;">
                <li>Find the email containing your toxicology report - titled <strong>"View your Quest test results."</strong></li>
                <li>Submit your test registration confirmation code and personal details to log in.</li>
                <li>Click <strong>"View Online Results"</strong> on the right hand side.</li>
                <li>Click <strong>"Print Report"</strong> in the top right of the report area.</li>
                <li>Select <strong>"Simple Report"</strong> from the dropdown menu.</li>
                <li>Download the PDF file and upload it below.</li>
              </ol>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader("", type="pdf", key="toxicology_upload")
        if uploaded:
            with st.spinner("Processing your report..."):
                try:
                    pdf_bytes = uploaded.read()
                    df = extract_results_to_dataframe(pdf_bytes)
                    # Save CSV to Supabase
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_content = csv_buffer.getvalue().encode("utf-8")
                    bucket.upload(csv_key, csv_content, {"content-type": "text/csv"})
                    st.success("Upload successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to process file: {e}") 
