import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase

def surveys_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Surveys</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    behavior_scores_file = f"{username}/{timepoint_id}/surveys.csv"
    try:
        behavior_scores_bytes = user_supabase.storage.from_("data").download(behavior_scores_file)
        behavior_scores_df = pd.read_csv(io.BytesIO(behavior_scores_bytes))
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(behavior_scores_df)
    except Exception as e:
        st.info("There was an error retrieving your survey data. Please contact admin.") 