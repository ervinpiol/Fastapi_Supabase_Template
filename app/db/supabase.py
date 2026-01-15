from supabase import Client, create_client

from app.core.config import settings


def get_supabase_client() -> Client:
    """Return Supabase client for auth operations."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
