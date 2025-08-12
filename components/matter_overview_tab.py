import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase

def matter_overview_tab(username: str):
    st.markdown("<h1>Matter Overview</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    matter_file = f"{username}/matter.csv"
    try:
        matter_bytes = user_supabase.storage.from_("data").download(matter_file)
        matter_df = pd.read_csv(io.BytesIO(matter_bytes))
        st.markdown("Overview of Matter data from Jan 2025 - May 2025. Double-click any cell to reveal its full contents.")
        st.dataframe(matter_df)
    except Exception as e:
        st.info("There was an error retrieving your Matter data. Please contact admin.") 