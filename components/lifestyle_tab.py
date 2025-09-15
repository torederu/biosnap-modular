import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path

def lifestyle_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Lifestyle</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    lifestyle_file = build_supabase_path(username, timepoint_id, "lifestyle.csv")
    try:
        lifestyle_bytes = user_supabase.storage.from_("data").download(lifestyle_file)
        lifestyle_df = pd.read_csv(io.BytesIO(lifestyle_bytes))
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(lifestyle_df)
    except Exception as e:
        st.info("There was an error retrieving your lifestyle data. Please contact admin.") 
