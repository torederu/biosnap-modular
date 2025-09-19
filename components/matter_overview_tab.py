import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path
from datetime import datetime

def matter_overview_tab(username: str, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Matter Overview</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    bucket = user_supabase.storage.from_("data")
    
    # Check if matter data exists
    matter_file = build_supabase_path(username, timepoint_id, "matter.csv")
    matter_data_exists = False
    
    try:
        matter_bytes = user_supabase.storage.from_("data").download(matter_file)
        matter_df = pd.read_csv(io.BytesIO(matter_bytes))
        matter_data_exists = True
    except Exception as e:
        matter_data_exists = False
    
    # Check if form submission confirmation exists
    submission_file = build_supabase_path(username, timepoint_id, "matter_memory_submitted.txt")
    form_submitted = False
    
    try:
        bucket.download(submission_file)
        form_submitted = True
    except Exception as e:
        form_submitted = False
    
    if matter_data_exists:
        # Show the matter data if available
        st.markdown("Overview of Matter data from Jan 2025 - May 2025. Double-click any cell to reveal its full contents.")
        st.dataframe(matter_df)
    elif form_submitted:
        # Show success message if form was submitted but data not yet processed
        st.success("Thank you! We will retrieve and process your memory data shortly.")
    else:
        # Show instructions for submitting memory data
        st.markdown(f"""
        <div style='font-size:17.5px; line-height:1.6; margin-bottom:1.5rem;'>
        Please submit your latest memory data:
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='font-size:15px; line-height:1.6; margin-top:-1.5rem; margin-bottom:0.5rem; padding-left:1.5rem'>
          <ol style="margin-top: 0; margin-bottom: 0; padding-top: 0;">
            <li>Ensure you have version 1.1 (v1.1) of the Memory Transfer app downloaded on your iPhone.</li>
            <li>If needed, update the Memory Transfer app using <a href='https://apps.apple.com/us/app/matter-hri-study-transfer/id6554001771' target='_blank'>this link</a>.</li>
            <li>Open the Memory Transfer app and click <strong>"Upload Memory Scores."</strong></li>
            <li>Confirm that you completed the form below.</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Form submission checkbox
        with st.form("matter_memory_confirmation"):
            st.markdown("**I have completed the memory data upload.**")
            submitted = st.form_submit_button("Submit Confirmation")
            
            if submitted:
                # Create a confirmation file in the database
                timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
                confirmation_content = f"Matter memory data uploaded for {timepoint_modifier} at {timestamp}"
                
                try:
                    bucket.upload(
                        submission_file,
                        confirmation_content.encode("utf-8"),
                        {"content-type": "text/plain"}
                    )
                    st.success("Thank you! We will retrieve and process your memory data shortly.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit confirmation: {e}") 
