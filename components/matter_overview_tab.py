import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path

def matter_overview_tab(username: str, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Matter Overview</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    matter_file = build_supabase_path(username, timepoint_id, "matter.csv")
    try:
        matter_bytes = user_supabase.storage.from_("data").download(matter_file)
        matter_df = pd.read_csv(io.BytesIO(matter_bytes))
        st.markdown("Overview of Matter data from Jan 2025 - May 2025. Double-click any cell to reveal its full contents.")
        st.dataframe(matter_df)
    except Exception as e:
        st.info("Your Matter data has not yet been received and/or analyzed. If you believe this is an error, please contact admin.") 
