# File: supabase_client.py
# Purpose: Create a cached Supabase client that works on Streamlit Cloud (st.secrets)
# and on other hosts (Render/Railway) via environment variables.
# Minimal comments: explain the why only.

from supabase import create_client
import streamlit as st
import os

@st.cache_resource
def get_supabase():
    """
    Return a Supabase client.
    Priority:
      1) Streamlit secrets: st.secrets['supabase']['project_url'|'service_role_key']
      2) Environment variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

    Why: Streamlit Cloud exposes secrets via st.secrets; Render/Railway expose environment
    variables. Supporting both makes the repo portable.
    """
    # 1) Try Streamlit secrets (preferred on Streamlit Cloud)
    try:
        sec = st.secrets.get("supabase")
        if sec:
            project_url = sec.get("project_url") or sec.get("url") or sec.get("SUPABASE_URL")
            service_key = sec.get("service_role_key") or sec.get("service_role") or sec.get("SUPABASE_SERVICE_ROLE_KEY")
            if project_url and service_key:
                return create_client(project_url, service_key)
    except Exception:
        # Fall through to environment var fallback
        pass

    # 2) Fallback to environment variables (Render / Railway / local env)
    project_url = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_PROJECT_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE")

    if project_url and service_key:
        return create_client(project_url, service_key)

    # 3) Nothing available — helpful runtime error (no secrets exposed)
    raise RuntimeError(
        "Supabase credentials not found. Provide either:\n"
        "  - Streamlit secrets: st.secrets['supabase']['project_url'] and st.secrets['supabase']['service_role_key']\n"
        "  - OR environment variables: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
    )
