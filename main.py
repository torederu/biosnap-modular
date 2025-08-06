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
from components.lifestyle_tab import lifestyle_tab
from components.thorne2_tab import thorne2_tab

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
        "Lifestyle",
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
        lifestyle_tab(username)
    with tabs[2]:
        function_health_tab(username)
    with tabs[3]:
        thorne_subtabs = st.tabs(["Thorne Overview", "Thorne Community Report"])
        with thorne_subtabs[0]:
            thorne_tab(username)
        with thorne_subtabs[1]:
            thorne2_tab(username)
    with tabs[4]:
        prenuvo_tab(username)
    with tabs[5]:
        trudiagnostic_tab(username)
    with tabs[6]:
        biostarks_tab(username)
    with tabs[7]:
        surveys_tab(username)
    with tabs[8]:
        interventions_tab(username)

if __name__ == "__main__":
    main()