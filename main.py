import streamlit as st
from auth import get_authenticator
from components.function_health_tab import function_health_tab
from components.thorne_tab import thorne_tab
from components.prenuvo_tab import prenuvo_tab
from components.trudiagnostic_tab import trudiagnostic_tab
from components.biostarks_tab import biostarks_tab
from components.surveys_tab import surveys_tab
from components.interventions_tab import interventions_tab
from components.clinical_intake_tab import clinical_intake_tab
# Import other tab components as you modularize them

def main():
    st.set_page_config(page_title="Biometric Snapshot", layout="centered")
    authenticator = get_authenticator()
    authenticator.login(location='main')
    auth_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")
    if auth_status is False:
        st.error("Username or password is incorrect.")
        st.stop()
    elif auth_status is None:
        st.stop()
    elif auth_status:
        col1, col2 = st.columns([4, 1])
        with col2:
            authenticator.logout("Logout", location='main')
    if not auth_status:
        st.stop()
    tab_names = [
        "Clinical Intake",
        "Function Health",
        "Thorne",
        "Prenuvo",
        "Trudiagnostic",
        "Biostarks",
        "Surveys",
        "Interventions"
    ]
    tabs = st.tabs(tab_names)
    with tabs[0]:
        clinical_intake_tab(username)
    with tabs[1]:
        function_health_tab(username)
    with tabs[2]:
        thorne_tab(username)
    with tabs[3]:
        prenuvo_tab(username)
    with tabs[4]:
        trudiagnostic_tab(username)
    with tabs[5]:
        biostarks_tab(username)
    with tabs[6]:
        surveys_tab(username)
    with tabs[7]:
        interventions_tab(username)
    # Add other tab calls as you modularize them

if __name__ == "__main__":
    main()
