# ═══════════════════════════════════════════════════════════════════════════
# auth.py — Supabase authentication utility for RIPPLEPOINT
# Place this file alongside app.py in your GitHub repo
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import os
import json
import requests
from datetime import datetime, timezone

SUPABASE_URL     = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON    = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE = os.environ.get("SUPABASE_SERVICE_KEY", "")  # admin only

# ── SUPABASE REST HELPERS ─────────────────────────────────────────────────────

def _headers(service=False):
    key = SUPABASE_SERVICE if service else SUPABASE_ANON
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def supabase_sign_up(email, password, full_name):
    """Register a new user. Returns (success, message)."""
    try:
        # 1. Create auth user
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers=_headers(),
            json={"email": email, "password": password,
                  "data": {"full_name": full_name}}
        )
        data = r.json()
        if r.status_code not in (200, 201):
            return False, data.get("msg", data.get("error_description", "Sign-up failed"))

        user_id = data.get("user", {}).get("id") or data.get("id")
        if not user_id:
            return False, "Could not retrieve user ID"

        # 2. Insert into profiles table (pending approval)
        r2 = requests.post(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers=_headers(service=True),
            json={
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "status": "pending",       # pending | approved | rejected
                "tier": "none",            # none | free | pro | institutional
                "created_at": datetime.now(timezone.utc).isoformat(),
                "approved_at": None
            }
        )
        if r2.status_code not in (200, 201):
            return False, f"Profile creation failed: {r2.text[:100]}"

        return True, "Registration submitted. You will receive access once approved."

    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def supabase_sign_in(email, password):
    """Sign in. Returns (success, user_data_or_error_msg)."""
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers=_headers(),
            json={"email": email, "password": password}
        )
        data = r.json()
        if r.status_code != 200:
            return False, data.get("error_description", "Invalid credentials")

        access_token = data.get("access_token")
        user_id      = data.get("user", {}).get("id")

        # Fetch profile
        r2 = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=*",
            headers=_headers(service=True)
        )
        profiles = r2.json()
        if not profiles:
            return False, "Profile not found. Contact support."

        profile = profiles[0]
        return True, {
            "access_token": access_token,
            "user_id":      user_id,
            "email":        email,
            "full_name":    profile.get("full_name", email),
            "status":       profile.get("status", "pending"),
            "tier":         profile.get("tier", "none"),
        }

    except Exception as e:
        return False, f"Login error: {str(e)[:100]}"


def supabase_sign_out():
    """Clear session."""
    for key in ["rp_user", "rp_token", "rp_logged_in"]:
        if key in st.session_state:
            del st.session_state[key]


def get_all_users():
    """Admin only — get all profiles."""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?select=*&order=created_at.desc",
            headers=_headers(service=True)
        )
        return r.json() if r.status_code == 200 else []
    except:
        return []


def update_user_status(user_id, status, tier):
    """Admin only — approve/reject user and set tier."""
    try:
        payload = {"status": status, "tier": tier}
        if status == "approved":
            payload["approved_at"] = datetime.now(timezone.utc).isoformat()
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}",
            headers=_headers(service=True),
            json=payload
        )
        return r.status_code in (200, 204)
    except:
        return False


# ── SESSION HELPERS ───────────────────────────────────────────────────────────

def is_logged_in():
    return st.session_state.get("rp_logged_in", False)

def current_user():
    return st.session_state.get("rp_user", {})

def is_approved():
    return current_user().get("status") == "approved"

def is_admin(email):
    admin_emails = os.environ.get("ADMIN_EMAILS", "").split(",")
    return email.strip() in [e.strip() for e in admin_emails]

def require_auth():
    """
    Call at the top of every page. Redirects to login if not authenticated.
    Returns True if user is logged in AND approved.
    """
    if not is_logged_in():
        st.stop()
    user = current_user()
    if user.get("status") == "pending":
        st.stop()
    if user.get("status") == "rejected":
        st.stop()
    return True
