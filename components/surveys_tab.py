import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path

def surveys_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Surveys</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    surveys_file = build_supabase_path(username, timepoint_id, "surveys.csv")
    try:
        surveys_bytes = user_supabase.storage.from_("data").download(surveys_file)
        surveys_df = pd.read_csv(io.BytesIO(surveys_bytes))
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(surveys_df)
    except Exception as e:
        st.info("Your survey data has not yet been received and/or analyzed. If you believe this is an error, please contact admin.")
