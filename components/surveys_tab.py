import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path
from datetime import datetime

def surveys_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Surveys</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    bucket = user_supabase.storage.from_("data")
    
    # Check if surveys data exists
    surveys_file = build_supabase_path(username, timepoint_id, "surveys.csv")
    surveys_data_exists = False
    
    try:
        surveys_bytes = user_supabase.storage.from_("data").download(surveys_file)
        surveys_df = pd.read_csv(io.BytesIO(surveys_bytes))
        surveys_data_exists = True
    except Exception as e:
        surveys_data_exists = False
    
    # Check if form submission confirmation exists
    submission_file = build_supabase_path(username, timepoint_id, "surveys_submitted.txt")
    form_submitted = False
    
    try:
        bucket.download(submission_file)
        form_submitted = True
    except Exception as e:
        form_submitted = False
    
    if surveys_data_exists:
        # Show the surveys data if available
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(surveys_df)
    elif form_submitted:
        # Show success message if form was submitted but data not yet processed
        st.success("Thank you! We will retrieve and process your survey responses shortly.")
    else:
        # Show instructions for completing surveys
        st.markdown(f"""
        <div style='font-size:17.5px; line-height:1.6; margin-bottom:1.5rem;'>
        Please complete your survey dataset:
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='font-size:15px; line-height:1.6; margin-top:-1.5rem; margin-bottom:0.5rem; padding-left:1.5rem'>
          <ol style="margin-top: 0; margin-bottom: 0; padding-top: 0;">
            <li><a href='https://docs.google.com/forms/d/e/1FAIpQLSdvcndisQSc97xPNEr5FtnOrsbmRjWhjqvehcWOQi4VsEXE5w/viewform?usp=sharing' target='_blank' style='text-decoration: none; color: #1f77b4;'>Click here to complete the GLC Sleep Survey.</a></li>
            <li><a href='https://docs.google.com/forms/d/e/1FAIpQLScyUvEqND71X_gs3bTtljXDLBLqCBNhzTvUYiHmV1v0gUFdIA/viewform?usp=sharing' target='_blank' style='text-decoration: none; color: #1f77b4;'>Click here to complete the GLC Behavioral Survey.</a></li>
            <li><a href='https://docs.google.com/forms/d/e/1FAIpQLScpjCrhNoSrM_2drqNtnhhXQF4K8BHl9a4Y0AAQBMHRgP7CRQ/viewform?usp=sharing' target='_blank' style='text-decoration: none; color: #1f77b4;'>Click here to complete the GLC Affective Survey.</a></li>
            <li><a href='https://docs.google.com/forms/d/e/1FAIpQLSf_tp6InhfQLA3fcWla5z2ZbP8HaNqYpNYZBYFFq-CmlMyAqg/viewform' target='_blank' style='text-decoration: none; color: #1f77b4;'>Click here to complete the GLC Cognitive Survey.</a></li>
            <li>Confirm that you completed all surveys below.</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Form submission checkbox
        with st.form("surveys_confirmation"):
            st.markdown("**I have completed all surveys.**")
            submitted = st.form_submit_button("Submit Confirmation")
            
            if submitted:
                # Create a confirmation file in the database
                timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
                confirmation_content = f"All surveys completed for {timepoint_modifier} at {timestamp}"
                
                try:
                    bucket.upload(
                        submission_file,
                        confirmation_content.encode("utf-8"),
                        {"content-type": "text/plain"}
                    )
                    st.success("Thank you! We will retrieve and process your survey responses shortly.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to submit confirmation: {e}")
