import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path

def thorne2_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Thorne Community Report</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    filename = build_supabase_path(username, timepoint_id, "thorne2.csv")
    bucket = user_supabase.storage.from_("data")
    file_list = bucket.list(path=f"{username}/{timepoint_modifier}/")
    file_exists = any(f["name"] == "thorne2.csv" for f in file_list)
    
    if file_exists:
        try:
            csv_bytes = bucket.download(filename)
            if isinstance(csv_bytes, bytes):
                df = pd.read_csv(io.BytesIO(csv_bytes))
                st.markdown("Double-click any cell to reveal its full contents.")
                st.dataframe(df)
                st.success("Upload successful!")
            else:
                st.error("Failed to retrieve the file. Please try again.")
        except Exception as e:
            st.error(f"Error retrieving file: {e}")
    else:
        # Convert T01 -> 01, T02 -> 02, etc.
        timepoint_number = timepoint_modifier.replace("T", "")
        
        st.markdown("<div style='font-size:17.5px; line-height:1.6'>Please upload your Thorne Full Microbe Community Report:</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='font-size:15px; line-height:1.6; margin-bottom:0.5rem; padding-left:1.5rem'>
          <ol style="margin-top: 0; margin-bottom: 0;">
            <li>Log in to <a href='https://www.thorne.com/login' target='_blank'>Thorne</a>.</li>
            <li>Navigate to your <strong>Gut Health Results</strong> for <strong>Time Point {timepoint_number}.</strong></li>
            <li>Click <strong>"Download"</strong> in the top right of the report area.</li>
            <li>Select <strong>"Full Microbe Community."</strong></li>
            <li>Upload the downloaded CSV file below.</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded = st.file_uploader("", type="csv", key="thorne2_upload")
        if uploaded:
            with st.spinner("Processing your file..."):
                try:
                    df = pd.read_csv(uploaded)
                    csv_bytes = df.to_csv(index=False).encode()
                    bucket.upload(filename, csv_bytes, {"content-type": "text/csv"})
                    st.session_state.thorne2_df = df
                    st.success("Upload successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to process file: {e}")
