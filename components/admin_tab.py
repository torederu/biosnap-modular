import streamlit as st
from supabase_utils import get_user_supabase
import yaml

def admin_tab(admin_username: str):
    st.markdown("<h1>Admin Controls</h1>", unsafe_allow_html=True)
    
    # Get the current viewing user (either admin or switched user)
    current_viewing_user = st.session_state.get("admin_viewing_user", admin_username)
    
    # Show info about who they're currently viewing - capitalize the username
    st.info(f"You are currently viewing BioSnap as {current_viewing_user.upper()}.")
    
    # Get list of all users from config.yaml instead of Supabase
    try:
        with open('config.yaml') as file:
            config = yaml.load(file, yaml.SafeLoader)
        
        # Get usernames from config
        if 'credentials' in config and 'usernames' in config['credentials']:
            users = list(config['credentials']['usernames'].keys())
            users = sorted(users)
        else:
            users = []
        

        
        # Also try to get users from Supabase for comparison
        user_supabase = get_user_supabase()
        bucket = user_supabase.storage.from_("data")
        
        try:
            all_items = bucket.list(path="")
            supabase_users = []
            for item in all_items:
                # Check different possible structures
                if isinstance(item, dict):
                    if item.get("type") == "folder" and item.get("name"):
                        supabase_users.append(item["name"])
                    elif item.get("name") and "/" not in item.get("name", ""):
                        # This might be a top-level user folder
                        supabase_users.append(item["name"])
            
            supabase_users = sorted(list(set(supabase_users)))
            
            # Use Supabase users if available, otherwise fall back to config users
            if supabase_users:
                users = supabase_users
                
        except Exception as e:
            pass  # Silently handle Supabase errors, fall back to config users
        
        # If still no users, fall back to hardcoded list based on what we saw in debug
        if not users:
            users = ['GLCXXX', 'GLC001', 'GLC002', 'GLC003', 'GLC004', 'GLC005']
        
        # Create form for user switching
        if users:
            with st.form("admin_user_switch"):
                st.markdown("**Switch to view another user's data:**")
                
                # Handle case where current_viewing_user might not be in the list
                default_index = 0
                if current_viewing_user in users:
                    default_index = users.index(current_viewing_user)
                elif current_viewing_user.upper() in users:
                    default_index = users.index(current_viewing_user.upper())
                elif current_viewing_user.lower() in [u.lower() for u in users]:
                    # Find case-insensitive match
                    for i, user in enumerate(users):
                        if user.lower() == current_viewing_user.lower():
                            default_index = i
                            break
                
                selected_user = st.selectbox(
                    "Select user to view:",
                    options=users,
                    index=default_index,
                    key="admin_user_selector",
                    format_func=lambda x: x.upper()
                )
                
                if st.form_submit_button("Switch User"):
                    if selected_user != current_viewing_user:
                        # Clear all session state to prevent data contamination
                        for key in list(st.session_state.keys()):
                            if key not in ["authentication_status", "username", "name"]:
                                st.session_state.pop(key, None)
                        
                        # Set the new viewing user
                        st.session_state["admin_viewing_user"] = selected_user
                        st.rerun()
        else:
            st.error("No users found. Please check your configuration.")
            
    except Exception as e:
        st.error(f"Error accessing user list: {e}") 