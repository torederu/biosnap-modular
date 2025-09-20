import streamlit as st
import pandas as pd
import io
import time
from utils.scraping_utils import update_progress, scrape_function_health
from supabase_utils import get_supabase_bucket, build_supabase_path

def function_health_tab(username, timepoint_id="T_01", timepoint_modifier="T01"):
    bucket = get_supabase_bucket()
    
    # Create timepoint-scoped session state keys
    csv_ready_key = f"function_csv_ready_{timepoint_modifier}"
    csv_key = f"function_csv_{timepoint_modifier}"
    df_key = f"function_df_{timepoint_modifier}"
    uploaded_key = f"function_supabase_uploaded_{timepoint_modifier}"
    init_key = f"to_initialize_function_csv_{timepoint_modifier}"
    
    # === Try to restore saved CSV (stateless ghost-block logic)
    if not st.session_state.get(csv_ready_key):
        try:
            function_filename = build_supabase_path(username, timepoint_id, "functionhealth.csv")
            res = bucket.download(function_filename)
            files = bucket.list(path=f"{username}/{timepoint_modifier}/")
            in_list = any(f["name"] == "functionhealth.csv" for f in files)
            if res and len(res) > 0 and not in_list:
                st.session_state[csv_ready_key] = False
            elif res and len(res) > 0:
                function_df = pd.read_csv(io.BytesIO(res))
                st.session_state[csv_key] = res
                st.session_state[df_key] = function_df
                st.session_state[csv_ready_key] = True
            else:
                st.session_state[csv_ready_key] = False
        except Exception:
            st.session_state[csv_ready_key] = False
    st.markdown(f"<h1>{timepoint_modifier} Function Health</h1>", unsafe_allow_html=True)
    if st.session_state.get(csv_ready_key) and df_key in st.session_state:
        st.markdown("Double-click any cell to reveal its full contents.")
        st.dataframe(st.session_state[df_key])
        st.success("Import successful!")
    else:
        st.markdown(f"<div style='font-size:17.5px; line-height:1.6'>Please import your Function Health data:</div>", unsafe_allow_html=True)
        # Convert T01 -> 01, T02 -> 02, etc.
        timepoint_number = timepoint_modifier.replace("T", "")
        st.markdown(f"""
        <div style='font-size:15px; line-height:1.6; margin-bottom:0.5rem; padding-left:1.5rem'>
          <ol style="margin-top: 0; margin-bottom: 0;">
            <li>Confirm that your <a href='https://www.functionhealth.com/' target='_blank'>Function Health account</a> is up to date with data from <strong>Time Point {timepoint_number}</strong>.</li>
            <li>When your Function Health account is completely up to date, enter your credentials below to connect and import your data.</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
    <div style='font-size:17.5px; line-height:1.6; margin-top:-0.3rem; margin-bottom:1.5rem;'>
    <strong>Your Information Stays Private:</strong> We do not store your credentials. They are used to connect to Function Health to download your data, and then are erased from memory.
    </div>""", unsafe_allow_html=True)
        
        with st.form("function_login_form"):
            user_email = st.text_input("Function Health Email", key="function_email")
            user_pass = st.text_input("Function Health Password", type="password", key="function_password")
            submitted = st.form_submit_button("Connect & Import Data")
        
        if submitted:
            if not user_email or not user_pass:
                st.error("Please enter email and password.")
                st.stop()
            st.session_state.pop("skip_restore", None)
            with st.spinner("Importing Function Health Data"):
                status = st.empty()
                try:
                    function_df = scrape_function_health(user_email, user_pass, status)
                    status.markdown(
                        '<div style="margin-left:2.3em; font-size:1rem; font-weight:400; line-height:1.2; margin-top:-0.6em; margin-bottom:0.1em;">⤷ Deleting Function Health credentials from memory</div>',
                        unsafe_allow_html=True
                    )
                    del user_email
                    del user_pass
                    st.session_state.pop("function_email", None)
                    st.session_state.pop("function_password", None)
                    function_csv_bytes = function_df.to_csv(index=False).encode()
                    st.session_state[csv_key] = function_csv_bytes
                    st.session_state[df_key] = function_df
                    st.session_state[f"{username}_functionhealth.csv"] = function_csv_bytes
                    st.session_state[f"{username}_functionhealth.csv"] = function_csv_bytes
                    function_filename = build_supabase_path(username, timepoint_id, "functionhealth.csv")
                    try:
                        bucket.remove([function_filename])
                    except Exception:
                        pass
                    response = bucket.upload(
                        path=function_filename,
                        file=function_csv_bytes,
                        file_options={"content-type": "text/csv"}
                    )
                    res_data = response.__dict__
                    if "error" in res_data and res_data["error"]:
                        st.error("Upload failed.")
                    else:
                        st.session_state[uploaded_key] = True
                    
                    status.markdown(
                        '<div style="margin-left:2.3em; font-size:1rem; font-weight:400; line-height:1.2; margin-top:-0.6em; margin-bottom:0.1em;">⤷ Import successful!</div>',
                        unsafe_allow_html=True
                    )
                    st.session_state[init_key] = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Import failed: {type(e).__name__} — {e}")
                finally:
                    status.empty()
