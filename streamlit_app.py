# streamlit_app.py
import streamlit as st
import os
from supabase_client import get_supabase
import requests

st.set_page_config(page_title="Sportaura CMS (Debug)", layout="wide")
st.title("Sportaura CMS — Connectivity & Auth Debug")

# Safe env info (do not print keys)
def env_info():
    url = os.getenv("SUPABASE_URL") or "<not set>"
    key_len = len(os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "")
    return {"project_url": url, "key_length": key_len}

info = env_info()
st.subheader("Secrets / env health (safe)")
st.write("Project URL:", info["project_url"])
st.write("Key length (chars):", info["key_length"])
st.caption("Key not printed. Only length shown to confirm value present.")

# Initialize supabase client (uses supabase_client.get_supabase)
try:
    supabase = get_supabase()
except Exception as e:
    st.error("Supabase initialization failed. Check environment variables.")
    st.exception(e)
    st.stop()

# connectivity quick checks
def safe_get(url, timeout=6):
    try:
        r = requests.get(url, timeout=timeout)
        return {"ok": True, "status_code": r.status_code}
    except Exception as e:
        return {"ok": False, "error_type": type(e).__name__, "error_str": str(e)}

st.subheader("Outbound checks (safe)")
st.write("example.com ->", safe_get("https://example.com"))
if info["project_url"] != "<not set>":
    st.write(f"{info['project_url']} ->", safe_get(info["project_url"]))
    st.write(f"{info['project_url']}/rest/v1 ->", safe_get(info["project_url"] + "/rest/v1"))

# UI: insert + fetch (unchanged)
st.markdown("---")
st.header("Add trivia")
q = st.text_area("Question")
correct = st.text_input("Correct")
opt2 = st.text_input("Option 2")
opt3 = st.text_input("Option 3")
is_disp = st.checkbox("Is dispatched?")

if st.button("Add to Supabase"):
    if not q or not correct:
        st.error("Question and Correct Answer required.")
    else:
        payload = {
            "question_text": q,
            "correct_answer": correct,
            "option_2": opt2 or "",
            "option_3": opt3 or "",
            "is_dispatched": bool(is_disp),
        }
        try:
            resp = supabase.table("trivia").insert(payload).execute()
            if getattr(resp, "error", None):
                st.error(f"Supabase API error: {resp.error}")
            else:
                st.success("Inserted.")
        except Exception as e:
            st.error("Insert failed — see details.")
            st.exception(e)

st.markdown("---")
st.header("Existing Questions")
try:
    resp = supabase.table("trivia").select("*").order("id", desc=True).limit(100).execute()
    if getattr(resp, "error", None):
        st.error("Select API error.")
        st.json({"error": str(resp.error)})
    else:
        st.write(resp.data or [])
except Exception as e:
    st.error("Fetch failed — see details.")
    st.exception(e)
