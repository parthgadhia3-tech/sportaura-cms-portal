# streamlit_app.py -- Paste (or merge) this debug-enabled version into your repo.
# Minimal comments. This shows secret health, runs safe network checks,
# and wraps supabase insert/select in try/except to expose the underlying error.

import streamlit as st
from supabase_client import get_supabase
import requests

st.set_page_config(page_title="Sportaura CMS — Debug", layout="wide")
st.title("Sportaura CMS — Connectivity & Auth Debug")

# 1) Secret health (do NOT print the key)
def check_secrets():
    try:
        s = st.secrets["supabase"]
    except Exception:
        return {"ok": False, "reason": "st.secrets['supabase'] missing"}
    url = s.get("project_url")
    key = s.get("service_role_key")
    return {"ok": True, "project_url": url, "key_length": len(key) if key else 0}

health = check_secrets()
if not health["ok"]:
    st.error("Supabase secrets missing in Streamlit Cloud. Add them and redeploy.")
    st.stop()

st.subheader("Secrets health")
st.write("Project URL:", health["project_url"])
st.write("Service role key length (chars):", health["key_length"])
st.caption("Key is not shown. Length printed only to confirm you pasted a full key (> ~300 chars).")

# 2) Simple safe HTTP test helper
def safe_get(url, headers=None, timeout=6):
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        return {"ok": True, "status_code": r.status_code, "text_preview": r.text[:250]}
    except Exception as e:
        return {"ok": False, "error_type": type(e).__name__, "error_str": str(e)}

st.subheader("Outbound connectivity checks (safe)")
# a) basic internet
res_example = safe_get("https://example.com")
st.write("https://example.com ->", res_example)

# b) supabase project root
proj = health["project_url"].rstrip("/")
res_root = safe_get(proj)
st.write(f"{proj} ->", res_root)

# c) supabase rest endpoint with headers (we use the real key but do not print it)
try:
    key = st.secrets["supabase"]["service_role_key"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    res_rest = safe_get(f"{proj}/rest/v1", headers=headers)
    st.write(f"{proj}/rest/v1 ->", res_rest)
except Exception as e:
    st.write("Could not run REST check:", type(e).__name__, str(e))

# 3) Initialize supabase client (existing helper)
supabase = get_supabase()

st.markdown("---")
st.header("Insert trivia (debug-wrapped)")

question = st.text_area("Question", height=80)
correct = st.text_input("Correct Answer")
opt2 = st.text_input("Option 2")
opt3 = st.text_input("Option 3")
is_disp = st.checkbox("Is dispatched?", value=False)

if st.button("Add to Supabase (debug)"):
    if not question.strip() or not correct.strip():
        st.error("Question and Correct Answer required.")
    else:
        payload = {
            "question_text": question,
            "correct_answer": correct,
            "option_2": opt2 or "",
            "option_3": opt3 or "",
            "is_dispatched": is_disp,
        }
        try:
            resp = supabase.table("trivia").insert(payload).execute()
            if getattr(resp, "error", None):
                st.error("Supabase API rejected request (APIError).")
                st.json({"status": getattr(resp, "status_code", None), "error": str(resp.error)})
            else:
                st.success("Insert succeeded.")
        except Exception as e:
            # Show the connection/auth exception info (safe: no secrets)
            st.error("Exception while inserting (see details).")
            st.write("Exception type:", type(e).__name__)
            st.write("Exception message:", str(e))
            st.exception(e)

st.markdown("---")
st.header("Fetch trivia (debug-wrapped)")

try:
    resp = supabase.table("trivia").select("*").order("id", desc=True).limit(50).execute()
    if getattr(resp, "error", None):
        st.error("Supabase API rejected SELECT.")
        st.json({"status": getattr(resp, "status_code", None), "error": str(resp.error)})
    else:
        st.write(resp.data or [])
except Exception as e:
    st.error("Exception while fetching (see details).")
    st.write("Exception type:", type(e).__name__)
    st.write("Exception message:", str(e))
    st.exception(e)
