from supabase import create_client
import streamlit as st

@st.cache_resource
def get_supabase():
    url = st.secrets["supabase"]["project_url"]
    key = st.secrets["supabase"]["service_role_key"]
    return create_client(url, key)
