import streamlit as st
from auth import is_admin_user
from components.function_health_tab import function_health_tab
from components.thorne_tab import thorne_tab
from components.prenuvo_tab import prenuvo_tab
from components.trudiagnostic_tab import trudiagnostic_tab
from components.biostarks_tab import biostarks_tab
from components.surveys_tab import surveys_tab
from components.clinical_intake_tab import clinical_intake_tab
from components.lifestyle_tab import lifestyle_tab
from components.thorne2_tab import thorne2_tab
from components.toxicology_tab import toxicology_tab
from components.matter_overview_tab import matter_overview_tab
from components.matter_memory_ratings_tab import matter_memory_ratings_tab
from components.hri_tab import hri_tab
from components.oprl_tab import oprl_tab
from components.admin_tab import admin_tab

def render_timepoint_layout(timepoint_id, timepoint_name, authenticator=None):
    """
    Render the common layout for all timepoint pages
    
    Args:
        timepoint_id: The timepoint identifier (e.g., "T_01", "T_02")
        timepoint_name: The display name (e.g., "Time Point #01", "Time Point #02")
        authenticator: Optional authenticator instance (not used, kept for compatibility)
    """
    # Get username from session state (auth already handled in main)
    username = st.session_state.get("username", "USER")

    # Check if current user is admin
    is_admin = is_admin_user(username)
    
    # Determine which user's data to display
    if is_admin and "admin_viewing_user" in st.session_state:
        # Admin is viewing another user's data
        display_username = st.session_state["admin_viewing_user"]
    else:
        # Normal user or admin viewing their own data
        display_username = username

    # Extract timepoint number for modifier (e.g., "T_01" -> "T01")
    timepoint_modifier = timepoint_id.replace("_", "")
    
    # Create tab names list (original names without modifiers)
    main_tab_names = [
        "Screening",
        "Labs", 
        "Emotion & Cognition",
        "Habits & Performance",
    ]
    
    main_tabs = st.tabs(main_tab_names)

    # Screening
    with main_tabs[0]:
        screening_tabs = st.tabs(["Clinical Intake", "Toxicology", "Prenuvo"])
        with screening_tabs[0]:
            clinical_intake_tab(display_username, timepoint_id, timepoint_modifier)
        with screening_tabs[1]:
            toxicology_tab(display_username, timepoint_id, timepoint_modifier)
        with screening_tabs[2]:
            prenuvo_tab(display_username, timepoint_id, timepoint_modifier)

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
            function_health_tab(display_username, timepoint_id, timepoint_modifier)
        with labs_tabs[1]:
            biostarks_tab(display_username, timepoint_id, timepoint_modifier)
        with labs_tabs[2]:
            trudiagnostic_tab(display_username, timepoint_id, timepoint_modifier)
        with labs_tabs[3]:
            thorne_tab(display_username, timepoint_id, timepoint_modifier)
        with labs_tabs[4]:
            thorne2_tab(display_username, timepoint_id, timepoint_modifier)

    # Emotion & Cognition
    with main_tabs[2]:
        ec_tabs = st.tabs([
            "Matter Overview",
            "Matter Memory Ratings",
            "HRI",
            "Surveys"
        ])
        with ec_tabs[0]:
            matter_overview_tab(display_username, timepoint_id, timepoint_modifier)
        with ec_tabs[1]:
            matter_memory_ratings_tab(display_username, timepoint_id, timepoint_modifier)
        with ec_tabs[2]:
            hri_tab(display_username, timepoint_id, timepoint_modifier)
        with ec_tabs[3]:
            surveys_tab(display_username, timepoint_id, timepoint_modifier)

    # Habits & Performance
    with main_tabs[3]:
        hp_tabs = st.tabs(["Lifestyle", "OPRL"])
        with hp_tabs[0]:
            lifestyle_tab(display_username, timepoint_id, timepoint_modifier)
        with hp_tabs[1]:
            oprl_tab(display_username, timepoint_id, timepoint_modifier)

