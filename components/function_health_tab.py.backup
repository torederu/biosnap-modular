import streamlit as st
import pandas as pd
import io
import time
from utils.scraping_utils import update_progress, scrape_function_health
from supabase_utils import get_user_supabase

def function_health_tab(username):
    user_supabase = get_user_supabase()
    # === Try to restore saved CSV (stateless ghost-block logic)
    if not st.session_state.get("function_csv_ready"):
        try:
            bucket = user_supabase.storage.from_("data")
            function_filename = f"{username}/functionhealth.csv"
            res = bucket.download(function_filename)
            files = bucket.list(path=f"{username}/")
            in_list = any(f["name"] == "functionhealth.csv" for f in files)
            if res and len(res) > 0 and not in_list:
                st.session_state.function_csv_ready = False
            elif res and len(res) > 0:
                function_df = pd.read_csv(io.BytesIO(res))
                st.session_state.function_csv = res
                st.session_state.function_df = function_df
                st.session_state.function_csv_ready = True
            else:
                st.session_state.function_csv_ready = False
        except Exception:
            st.session_state.function_csv_ready = False
    st.markdown("<h1>Function Health</h1>", unsafe_allow_html=True)
    if st.session_state.get("deleting_in_progress", False):
        with st.spinner("Deleting file from database..."):
            st.session_state.pop("function_csv_ready", None)
            st.session_state.pop("function_csv", None)
            st.session_state.pop("function_df", None)
            st.session_state.pop("function_csv_filename", None)
            st.session_state.pop("function_supabase_uploaded", None)
            st.session_state.pop("function_email", None)
            st.session_state.pop("function_password", None)
            try:
                bucket = user_supabase.storage.from_("data")
                bucket.remove([f"{username}/functionhealth.csv"])
                max_attempts = 20
                file_still_exists = True
                for attempt in range(max_attempts):
                    time.sleep(3)
                    files = bucket.list(path=f"{username}/")
                    file_still_exists = any(f["name"] == "functionhealth.csv" for f in files)
                    if not file_still_exists:
                        break
                if not file_still_exists:
                    st.success("Resetting...")
                    time.sleep(1.5)
                    st.session_state.skip_restore = True
                    st.session_state.deletion_successful = True
                    st.session_state.just_deleted = True
                    st.session_state.pop("deleting_in_progress", None)
                    st.rerun()
                else:
                    st.error("File deletion timed out after 60 seconds. Please try again or check your connection.")
            except Exception as e:
                st.error(f"Something went wrong while deleting your file: {e}")
    elif st.session_state.get("function_csv_ready") and "function_df" in st.session_state:
        st.dataframe(st.session_state.function_df)
        st.success("Import successful!")
    else:
        st.markdown("""
    <div style='font-size:17.5px; line-height:1.6'>
    Please enter your Function Health credentials to connect and download your data.
    </div>""", unsafe_allow_html=True)
        st.markdown("""
    <div style='font-size:17.5px; line-height:1.6; margin-top:0.5rem; margin-bottom:1.5rem;'>
    <strong>Your Information Stays Private:</strong> We do not store your credentials. They are used once to connect to Function Health to download your data, and then are immediately erased from memory.
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
                    st.session_state.function_csv = function_csv_bytes
                    st.session_state.function_df = function_df
                    st.session_state.function_csv_filename = f"{username}_functionhealth.csv"
                    st.session_state.function_csv_file = function_csv_bytes
                    function_filename = f"{username}/functionhealth.csv"
                    bucket = user_supabase.storage.from_("data")
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
                        st.session_state.function_supabase_uploaded = True
                    status.markdown(
                        '<div style="margin-left:2.3em; font-size:1rem; font-weight:400; line-height:1.2; margin-top:-0.6em; margin-bottom:0.1em;">⤷ Import successful!</div>',
                        unsafe_allow_html=True
                    )
                    st.session_state.to_initialize_function_csv = True
                    st.rerun()
                except ValueError as ve:
                    st.error(str(ve))
                except Exception as e:
                    st.error(f"Import failed: {type(e).__name__} — {e}")
            status.empty() 