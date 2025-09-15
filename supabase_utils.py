import os
from supabase import create_client
from dotenv import load_dotenv

def get_user_supabase():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    return create_client(url, key)

def convert_timepoint_id_to_format(timepoint_id):
    """
    Convert timepoint_id (e.g., "T_01") to timepoint format (e.g., "T01")
    
    Args:
        timepoint_id: The timepoint identifier from the app (e.g., "T_01", "T_02")
    
    Returns:
        str: The timepoint format for file paths (e.g., "T01", "T02")
    """
    return timepoint_id.replace("_", "")

def build_supabase_path(username, timepoint_id, filename):
    """
    Build the Supabase storage path in the format: username/timepoint/filename
    
    Args:
        username: The username
        timepoint_id: The timepoint identifier (e.g., "T_01", "T_02")
        filename: The filename
    
    Returns:
        str: The full path for Supabase storage
    """
    timepoint = convert_timepoint_id_to_format(timepoint_id)
    return f"{username}/{timepoint}/{filename}"

def get_supabase_bucket():
    """
    Get the Supabase storage bucket for data files
    
    Returns:
        The Supabase storage bucket
    """
    user_supabase = get_user_supabase()
    return user_supabase.storage.from_("data")
