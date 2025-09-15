import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path

def hri_tab(username: str, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Happiness Research Institute</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    hri_file = build_supabase_path(username, timepoint_id, "hri.csv")
    try:
        hri_bytes = user_supabase.storage.from_("data").download(hri_file)
        hri_df = pd.read_csv(io.BytesIO(hri_bytes))
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(hri_df)
    except Exception as e:
        st.info("There was an error retrieving your HRI data. Please contact admin.") 
