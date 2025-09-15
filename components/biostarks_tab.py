import streamlit as st
import pandas as pd
import io
import time
from supabase_utils import get_user_supabase, build_supabase_path

def biostarks_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    st.markdown(f"<h1>{timepoint_modifier} Biostarks</h1>", unsafe_allow_html=True)
    user_supabase = get_user_supabase()
    biostarks_filename = build_supabase_path(username, timepoint_id, "biostarks.csv")
    bucket = user_supabase.storage.from_("data")
    if "biostarks_df" not in st.session_state:
        try:
            biostarks_bytes = bucket.download(biostarks_filename)
            files = bucket.list(path=f"{username}/{timepoint_modifier}/")
            in_list = any(f["name"] == "biostarks.csv" for f in files)
            if biostarks_bytes and len(biostarks_bytes) > 0 and in_list:
                st.session_state.biostarks_df = pd.read_csv(io.BytesIO(biostarks_bytes))
            else:
                st.session_state.biostarks_df = pd.DataFrame(columns=["Metric", "Value"])
        except Exception:
            st.session_state.biostarks_df = pd.DataFrame(columns=["Metric", "Value"])
    if st.session_state.get("reset_biostarks", False):
        with st.spinner("Deleting file from database..."):
            try:
                bucket.remove([biostarks_filename])
                st.session_state.biostarks_deleted = True
            except Exception as e:
                st.warning(f"Failed to delete file: {e}")
                st.session_state.biostarks_deleted = False
        for key in ["reset_biostarks", "biostarks_submitted"]:
            st.session_state.pop(key, None)
        st.session_state.biostarks_df = pd.DataFrame(columns=["Metric", "Value"])
        st.rerun()
    if st.session_state.biostarks_df.empty:
        st.markdown("""
        <div style='font-size:17.5px; line-height:1.6'>
        Please log in to <a href='https://results.biostarks.com/' target='_blank'>Biostarks</a> and fill in the fields below with the relevant values.<br><br>
        </div>
        """, unsafe_allow_html=True)
        with st.form("biostarks_form", border=True):
            def input_metric(label, expander_text):
                with st.container():
                    col1, col3 = st.columns([5, 4])
                    with col1:
                        st.markdown(
                            f"<div style='font-weight:600; font-size:1.2rem; margin-bottom:0.3rem'>{label}</div>",
                            unsafe_allow_html=True
                        )
                    with col3:
                        with st.expander("Where do I find this?"):
                            st.markdown(expander_text)
                st.text_input(label, key=label, label_visibility="collapsed")
            input_metric("Longevity NAD+ Score", """• Log in to [results.biostarks.com](https://results.biostarks.com)  
            • Look for your **Longevity Score** (0–100)""")
            st.divider()
            input_metric("NAD+ Levels", """• Log in to [results.biostarks.com](https://results.biostarks.com)  
            • Click your **Longevity Score**  
            • Hover over the **NAD+** hexagon  
            • Value will be shown in **ug/gHb**""")
            st.divider()
            input_metric("Magnesium Levels", """• Log in to [results.biostarks.com](https://results.biostarks.com)  
            • Click your **Longevity Score**  
            • Hover over the **Mg** hexagon  
            • Value will be shown in **ug/gHb**""")
            st.divider()
            input_metric("Selenium Levels", """• Log in to [results.biostarks.com](https://results.biostarks.com)  
            • Click your **Longevity Score**  
            • Hover over the **Se** hexagon  
            • Value will be shown in **ug/gHb**""")
            st.divider()
            input_metric("Zinc Levels", """• Log in to [results.biostarks.com](https://results.biostarks.com)  
            • Click your **Longevity Score**  
            • Hover over the **Zn** hexagon  
            • Value will be shown in **ug/gHb**""")
            submitted = st.form_submit_button("Submit")
        required_keys = [
            "Longevity NAD+ Score",
            "NAD+ Levels",
            "Magnesium Levels",
            "Selenium Levels",
            "Zinc Levels",
        ]
        if submitted:
            missing = [k for k in required_keys if not st.session_state.get(k, "").strip()]
            if missing:
                st.error("Please complete all required fields before submitting.")
            else:
                biostarks_df = pd.DataFrame([
                    ["Longevity NAD+ Score", st.session_state["Longevity NAD+ Score"]],
                    ["NAD+ Levels", st.session_state["NAD+ Levels"]],
                    ["Magnesium Levels", st.session_state["Magnesium Levels"]],
                    ["Selenium Levels", st.session_state["Selenium Levels"]],
                    ["Zinc Levels", st.session_state["Zinc Levels"]],
                ], columns=["Metric", "Value"])
                with st.spinner("Saving to database..."):
                    st.session_state.biostarks_df = biostarks_df
                    biostarks_csv_bytes = biostarks_df.to_csv(index=False).encode()
                    try:
                        bucket.remove([biostarks_filename])
                    except:
                        pass
                    bucket.upload(
                        path=biostarks_filename,
                        file=biostarks_csv_bytes,
                        file_options={"content-type": "text/csv"}
                    )
                    time.sleep(1)
                    st.session_state["biostarks_submitted"] = True
                    st.rerun()
    else:
        st.dataframe(st.session_state.biostarks_df)
        st.success("Upload successful!")
        # Removed Start Over button 
