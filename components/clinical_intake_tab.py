import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase

def clinical_intake_tab(username):
    st.markdown("<h1>Clinical Intake</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    clinical_file = f"{username}/clinical.csv"
    try:
        clinical_bytes = user_supabase.storage.from_("data").download(clinical_file)
        clinical_df = pd.read_csv(io.BytesIO(clinical_bytes))
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(clinical_df)
    except Exception as e:
        st.info("There was an error retrieving your clinical intake data. Please contact admin.") 