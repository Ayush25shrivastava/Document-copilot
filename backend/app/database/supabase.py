from supabase import Client, create_client
from app.config import settings


def get_supabase_client() -> Client:
    """Returns a Supabase client using the anon key (for public operations / unauthenticated user scope)."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_supabase_admin_client() -> Client:
    """Returns a Supabase client using the service role key (bypasses RLS, for admin/ingestion operations)."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def get_user_supabase_client(access_token: str) -> Client:
    """Returns a user-scoped Supabase client authorized with the user's JWT access token."""
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    client.postgrest.auth(access_token)
    return client
