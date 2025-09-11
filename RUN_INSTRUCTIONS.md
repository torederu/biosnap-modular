# How to Run the App

## Start the Application
```bash
streamlit run main.py
```

## Navigation
- **Time Point 01** - Root page (default) - shows in sidebar as "Time Point 01"
- **Time Point 02** - Available via sidebar navigation

## File Structure
- `main.py` - Main entry point using programmatic pages API
- `components/` - All tab components with timepoint support

## Database Structure
Data is stored in Supabase with the structure:
- `{username}/T_01/{data_type}.csv` - Time Point 01 data
- `{username}/T_02/{data_type}.csv` - Time Point 02 data

## Adding More Timepoints
To add Time Point 03, simply:
1. Add a new function: `def timepoint_03_page():`
2. Add the page to navigation: `timepoint_03 = st.Page(timepoint_03_page, title="Time Point 03", icon="📉")`
3. Add to nav list: `nav = st.navigation([timepoint_01, timepoint_02, timepoint_03])`
