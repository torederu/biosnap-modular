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

# New placeholder tabs
from components.toxicology_tab import toxicology_tab
from components.matter_overview_tab import matter_overview_tab
from components.matter_memory_ratings_tab import matter_memory_ratings_tab
from components.hri_tab import hri_tab
from components.oprl_tab import oprl_tab

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

    # Five main tabs
    main_tab_names = [
        "Screening",
        "Labs",
        "Emotion & Cognition",
        "Habits & Performance",
        "Interventions"
    ]
    main_tabs = st.tabs(main_tab_names)

    # Screening
    with main_tabs[0]:
        screening_tabs = st.tabs(["Clinical Intake", "Toxicology", "Prenuvo"])
        with screening_tabs[0]:
            clinical_intake_tab(username)
        with screening_tabs[1]:
            toxicology_tab(username)
        with screening_tabs[2]:
            prenuvo_tab(username)

    # Labs
    with main_tabs[1]:
        labs_tabs = st.tabs([
            "Function Health",
            "Biostarks",
            "Trudiagnostic",
            "Thorne Overview",
            "Thorne Community Report"
        ])
        with labs_tabs[0]:
            function_health_tab(username)
        with labs_tabs[1]:
            biostarks_tab(username)
        with labs_tabs[2]:
            trudiagnostic_tab(username)
        with labs_tabs[3]:
            thorne_tab(username)
        with labs_tabs[4]:
            thorne2_tab(username)

    # Emotion & Cognition
    with main_tabs[2]:
        ec_tabs = st.tabs([
            "Matter Overview",
            "Matter Memory Ratings",
            "HRI",
            "Surveys"
        ])
        with ec_tabs[0]:
            matter_overview_tab(username)
        with ec_tabs[1]:
            matter_memory_ratings_tab(username)
        with ec_tabs[2]:
            hri_tab(username)
        with ec_tabs[3]:
            surveys_tab(username)

    # Habits & Performance
    with main_tabs[3]:
        hp_tabs = st.tabs(["Lifestyle", "OPRL"])
        with hp_tabs[0]:
            lifestyle_tab(username)
        with hp_tabs[1]:
            oprl_tab(username)

    # Interventions
    with main_tabs[4]:
        interventions_tab(username)

if __name__ == "__main__":
    main()