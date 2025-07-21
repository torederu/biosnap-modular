import os
from supabase import create_client
from dotenv import load_dotenv

def get_user_supabase():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    return create_client(url, key)
