import streamlit as st
from components.timepoint_layout import render_timepoint_layout

# Set page config FIRST - before any other Streamlit commands
st.set_page_config(page_title="Biometric Snapshot", layout="centered")

# Create individual page functions
def timepoint_01():
    render_timepoint_layout("T_01", "Time Point #01")

def timepoint_02():
    render_timepoint_layout("T_02", "Time Point #02")

# Create pages with custom labels
timepoint_01_page = st.Page(timepoint_01, title="Time Point 01")
timepoint_02_page = st.Page(timepoint_02, title="Time Point 02")

# Set up navigation
nav = st.navigation([timepoint_01_page, timepoint_02_page])

# Run the navigation
nav.run()
