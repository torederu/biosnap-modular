import streamlit as st
import pandas as pd
import io
from supabase_utils import get_user_supabase, build_supabase_path

def clinical_intake_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Clinical Intake</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    clinical_file = build_supabase_path(username, timepoint_id, "clinical.csv")
    try:
        clinical_bytes = user_supabase.storage.from_("data").download(clinical_file)
        clinical_df = pd.read_csv(io.BytesIO(clinical_bytes))
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(clinical_df)
    except Exception as e:
        st.info("Your clinical intake data has not yet been received and/or analyzed. If you believe this is an error, please contact admin.")
