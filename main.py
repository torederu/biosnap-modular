import streamlit as st
from components.timepoint_layout import render_timepoint_layout
from auth import get_authenticator

# Set page config FIRST - before any other Streamlit commands
st.set_page_config(page_title="Biosnap", layout="centered")

# Initialize authenticator once at the module level
authenticator = get_authenticator()

# Handle authentication
authenticator.login(location='main')
auth_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# If not authenticated, show only login form (no sidebar)
if auth_status is False:
    st.error("Username or password is incorrect.")
    st.stop()
elif auth_status is None:
    # User is not logged in - show login form only
    st.stop()
elif not auth_status:
    st.stop()

# Only continue if authenticated
# Add logout button to sidebar
with st.sidebar:
    authenticator.logout("Logout", location='main')

# Clear session state if username changed (logout→login transition)
if "last_username" in st.session_state and st.session_state["last_username"] != username:
    st.session_state.clear()
    st.rerun()
st.session_state["last_username"] = username

# Define the Welcome page content
def welcome_page():
    # Welcome message with username
    st.title(f"Welcome to Biosnap, {username.upper()}!")
    
    # Content from the screenshot
    st.markdown("Biosnap is the personalized data portal for pilot participants in the **Good Life Camp** experiment to view snapshots of their biometric data.")
    st.write("Here, you can:")
    st.markdown("""
    *   **View** your health and performance data already collected and analyzed.
    *   **Upload** data we haven't yet received (e.g. reports like Prenuvo).
    *   **Connect** your accounts (e.g. Function Health) so we can retrieve your data.
    """)
    st.markdown("The Good Life Camp experiment relies on **repeated testing**, so your data is organized by **Time Points** (e.g. T01, T02).")
    st.write("To complete your data intake:")
    st.markdown("""
    1.  Click into each **Time Point** in the sidebar.
    2.  Visit each **tab** (e.g. Labs, Prenuvo, Emotion & Cognition).
    3.  Ensure that your data is either visible or uploaded.
    """)

# Create individual page functions for timepoints
def timepoint_01():
    with st.spinner("Please wait while we update and display your Time Point #01 data..."):
        render_timepoint_layout("T_01", "Time Point #01", authenticator)

def timepoint_02():
    with st.spinner("Please wait while we update and display your Time Point #02 data......"):
        render_timepoint_layout("T_02", "Time Point #02", authenticator)

# Create pages with custom labels - Updated sidebar format
welcome_st_page = st.Page(welcome_page, title=f"Welcome, {username.upper()}!")
timepoint_01_st_page = st.Page(timepoint_01, title="T01 - Time Point 01")
timepoint_02_st_page = st.Page(timepoint_02, title="T02 - Time Point 02")

# Set up navigation
nav = st.navigation([welcome_st_page, timepoint_01_st_page, timepoint_02_st_page])

# Run the navigation
nav.run()
