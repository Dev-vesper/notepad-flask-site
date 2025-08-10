import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from a .env file if present (development convenience)
load_dotenv()

SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase connection environment variables are missing. Please set SUPABASE_URL and SUPABASE_KEY.")

# Create a singleton Supabase client so we reuse underlying HTTP session across imports
_supabase: Client | None = None


def get_supabase() -> Client:
    """Return a singleton Supabase client instance

    The function lazily instantiates the client on first call and reuses it afterwards.
    This avoids repeatedly opening new network sessions.
    """
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase