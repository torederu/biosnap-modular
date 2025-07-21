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
