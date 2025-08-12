import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

def get_authenticator(config_path='config.yaml'):
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

def is_admin_user(username, config_path='config.yaml'):
    """Check if the given username has admin privileges."""
    try:
        with open(config_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
        
        # Check if user exists and has admin role
        if 'credentials' in config and 'usernames' in config['credentials']:
            # Handle case-insensitive username matching
            usernames = config['credentials']['usernames']
            # Find the username regardless of case
            matched_username = None
            for config_username in usernames.keys():
                if config_username.lower() == username.lower():
                    matched_username = config_username
                    break
            
            if matched_username:
                user_config = usernames[matched_username]
                role = user_config.get('role')
                return role == 'admin'
        
        return False
    except Exception as e:
        # Log the error for debugging
        print(f"Error checking admin status for {username}: {e}")
        return False
