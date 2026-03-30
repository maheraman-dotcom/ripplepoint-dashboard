import streamlit as st
import os
import requests
from datetime import datetime, timezone

SUPABASE_URL     = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON    = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE = os.environ.get("SUPABASE_SERVICE_KEY", "")

def _anon_headers():
    return {
        "apikey":        SUPABASE_ANON,
        "Authorization": f"Bearer {SUPABASE_ANON}",
        "Content-Type":  "application/json",
    }

def _service_headers():
    return {
        "apikey":        SUPABASE_SERVICE,
        "Authorization": f"Bearer {SUPABASE_SERVICE}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }

def supabase_sign_in(email, password):
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers=_anon_headers(),
            json={"email": email, "password": password},
            timeout=15
        )
        if r.status_code != 200:
            body = r.json()
            msg  = body.get("error_description") or body.get("msg") or "Invalid credentials"
            return False, msg

        auth_data    = r.json()
        access_token = auth_data.get("access_token", "")
        user_id      = auth_data.get("user", {}).get("id", "")

        if not user_id:
            return False, "Could not retrieve user ID"

        r2 = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=*",
            headers=_service_headers(),
            timeout=10
        )

        if r2.status_code != 200:
            return False, f"Profile fetch failed: {r2.status_code}"

        profiles = r2.json()
        if not profiles:
            return False, "Profile not found. Contact maheraman@gmail.com"

        profile = profiles[0]
        return True, {
            "access_token": access_token,
            "user_id":      user_id,
            "email":        email,
            "full_name":    profile.get("full_name", email),
            "status":       profile.get("status", "pending"),
            "tier":         profile.get("tier", "none"),
        }

    except requests.exceptions.Timeout:
        return False, "Connection timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to server. Check internet connection."
    except Exception as e:
        return False, f"Login error: {str(e)[:100]}"

def supabase_sign_up(email, password, full_name):
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers=_anon_headers(),
            json={"email": email, "password": password, "data": {"full_name": full_name}},
            timeout=15
        )
        body = r.json()
        if r.status_code not in (200, 201):
            return False, body.get("msg") or body.get("error_description") or "Sign-up failed"

        user_id = (body.get("user") or body).get("id")
        if not user_id:
            return False, "Could not retrieve user ID"

        r2 = requests.post(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers=_service_headers(),
            json={"id": user_id, "email": email, "full_name": full_name,
                  "status": "pending", "tier": "none",
                  "created_at": datetime.now(timezone.utc).isoformat()},
            timeout=10
        )
        if r2.status_code not in (200, 201):
            return False, f"Profile creation failed: {r2.text[:80]}"

        return True, "Registration submitted. Access granted once approved."
    except Exception as e:
        return False, f"Sign-up error: {str(e)[:100]}"

def supabase_sign_out():
    for key in ["rp_logged_in", "rp_user", "rp_token", "_rp_token_persist", "_rp_user_persist"]:
        if key in st.session_state:
            del st.session_state[key]

def get_all_users():
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?select=*&order=created_at.desc",
            headers=_service_headers(), timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def update_user_status(user_id, status, tier):
    try:
        payload = {"status": status, "tier": tier}
        if status == "approved":
            payload["approved_at"] = datetime.now(timezone.utc).isoformat()
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}",
            headers=_service_headers(), json=payload, timeout=10)
        return r.status_code in (200, 204)
    except:
        return False

def is_logged_in():
    return st.session_state.get("rp_logged_in", False)

def current_user():
    return st.session_state.get("rp_user", {})

def is_approved():
    return current_user().get("status") == "approved"

def is_admin(email):
    admin_emails = os.environ.get("ADMIN_EMAILS", "").split(",")
    return email.strip() in [e.strip() for e in admin_emails if e.strip()]
