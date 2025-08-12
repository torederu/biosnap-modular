import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase

def oprl_tab(username: str):
    st.markdown("<h1>Oregon Performance Research Lab</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    oprl_file = f"{username}/oprl.csv"
    try:
        oprl_bytes = user_supabase.storage.from_("data").download(oprl_file)
        oprl_df = pd.read_csv(io.BytesIO(oprl_bytes))
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(oprl_df)
    except Exception as e:
        st.info("There was an error retrieving your OPRL data. Please contact admin.") 