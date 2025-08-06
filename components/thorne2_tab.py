import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase

def thorne2_tab(username):
    st.markdown("<h1>Thorne Community Report</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    filename = f"{username}/thorne2_data.csv"
    bucket = user_supabase.storage.from_("data")
    file_list = bucket.list(path=username)
    file_exists = any(f["name"] == "thorne2_data.csv" for f in file_list)
    
    if file_exists:
        st.success("Your Thorne Community Report data has been uploaded successfully!")
        try:
            csv_bytes = bucket.download(filename)
            if isinstance(csv_bytes, bytes):
                df = pd.read_csv(io.BytesIO(csv_bytes))
                st.markdown("Double-click any cell to reveal its full contents.")
                st.dataframe(df)
                st.download_button("Download CSV", csv_bytes, file_name="thorne2_data.csv")
            else:
                st.error("Failed to retrieve the file. Please try again.")
        except Exception as e:
            st.error(f"Error retrieving file: {e}")
    else:
        st.markdown("<div style='font-size:17.5px; line-height:1.6'>Please upload your Thorne Full Microbe Community Report:</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:15px; line-height:1.6; margin-bottom:0.5rem; padding-left:1.5rem'>
          <ol style="margin-top: 0; margin-bottom: 0;">
            <li>Log in to <a href='https://www.thorne.com/login' target='_blank'>Thorne</a></li>
            <li>Navigate to your Gut Health results</li>
            <li>Click "Download" in the top right of the report area</li>
            <li>Select Full Microbe Community</li>
            <li>Upload the downloaded CSV file below</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded = st.file_uploader("", type="csv")
        if uploaded:
            with st.spinner("Uploading your Thorne Community Report data..."):
                try:
                    csv_content = uploaded.read()
                    bucket.upload(filename, csv_content, {"content-type": "text/csv"})
                    st.success("File uploaded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to upload file: {e}") 