import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path
from datetime import datetime

def clinical_intake_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Clinical Intake</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    bucket = user_supabase.storage.from_("data")
    
    # Check if clinical data exists
    clinical_file = build_supabase_path(username, timepoint_id, "clinical.csv")
    clinical_data_exists = False
    
    try:
        clinical_bytes = user_supabase.storage.from_("data").download(clinical_file)
        clinical_df = pd.read_csv(io.BytesIO(clinical_bytes))
        clinical_data_exists = True
    except Exception as e:
        clinical_data_exists = False
    
    # Check if form submission confirmation exists
    submission_file = build_supabase_path(username, timepoint_id, "clinical_intake_submitted.txt")
    form_submitted = False
    
    try:
        bucket.download(submission_file)
        form_submitted = True
    except Exception as e:
        form_submitted = False
    
    if clinical_data_exists:
        # Show the clinical data if available
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(clinical_df)
    elif form_submitted:
        # Show success message if form was submitted but data not yet processed
        timepoint_number = timepoint_modifier.replace("T", "")
        st.success("We will retrieve and process your form responses shortly!")
    else:
        # Show instructions for completing the form
        timepoint_number = timepoint_modifier.replace("T", "")
        
        st.markdown(f"""
        <div style='font-size:17.5px; line-height:1.6; margin-bottom:1.5rem;'>
        Please complete your clinical intake form for Time Point {timepoint_number}:
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='font-size:15px; line-height:1.6; margin-top:-1.5rem; margin-bottom:0.5rem; padding-left:1.5rem'>
          <ol style="margin-top: 0; margin-bottom: 0; padding-top: 0;">
            <li>Click <a href='https://docs.google.com/forms/d/e/1FAIpQLSdCxQubmvjkjxbeNaf7O0XFyVeq0JRLT-BDIlXDqu3XwBc4xw/viewform?usp=sharing' target='_blank'>here</a> to access and complete the form.</li>
            <li>Confirm that you completed the form below.</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Form submission checkbox
        with st.form("clinical_intake_confirmation"):
            st.markdown("**I have completed the clinical intake form.**")
            submitted = st.form_submit_button("Submit Confirmation")
            
            if submitted:
                # Create a confirmation file in the database
                timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
                confirmation_content = f"Clinical intake form completed for {timepoint_modifier} at {timestamp}"
                
                try:
                    bucket.upload(
                        submission_file,
                        confirmation_content.encode("utf-8"),
                        {"content-type": "text/plain"}
                    )
                    st.success("Thank you! We will retrieve and process your form responses shortly.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit confirmation: {e}")
