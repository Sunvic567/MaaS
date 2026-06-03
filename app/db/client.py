from supabase import create_client, Client
from functools import lru_cache
from app.core.config import get_settings

settings = get_settings()


@lru_cache()
def get_master_client() -> Client:
    """Your hosted Supabase instance — stores tenants, API keys, usage."""
    return settings.supabase


def get_tenant_client(tenant: dict) -> Client:
    """
    Returns the correct Supabase client for this tenant.

    - Hosted mode: returns master client (tenant isolated by user_id/agent_id)
    - BYOD mode: returns client pointed at tenant's own Supabase instance
    """
    if tenant.get("mode") == "byod":
        return create_client(
            tenant["byod_supabase_url"],
            tenant["byod_supabase_key"],
        )
    return get_master_client()
