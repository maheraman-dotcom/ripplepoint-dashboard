# ═══════════════════════════════════════════════════════════════════════════
# pages/admin.py — RIPPLEPOINT Admin Panel
# Accessible at: ripplepoint.rippleaxispoint.com (login as admin email)
# Only admin emails (set in ADMIN_EMAILS env var) can see this page
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
import os
from auth import (is_logged_in, current_user, is_admin,
                  get_all_users, update_user_status)

st.set_page_config(
    page_title="RIPPLEPOINT Admin",
    page_icon="⚙️",
    layout="wide"
)

# ── AUTH GUARD ────────────────────────────────────────────────────────────────
if not is_logged_in():
    st.error("Not authenticated. Please log in first.")
    st.stop()

user = current_user()
if not is_admin(user.get("email", "")):
    st.error("Access denied. Admin only.")
    st.stop()

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
html, body, [data-testid="stAppViewContainer"] { background: #080c14 !important; color: #e2e8f0 !important; }
#MainMenu, footer, header, [data-testid="stDecoration"] { display:none !important; }
.block-container { padding: 24px 32px !important; max-width: 100% !important; }
.adm-hdr { font-family:'Bebas Neue',sans-serif; font-size:28px; letter-spacing:0.06em; color:#fff; margin-bottom:4px; }
.adm-hdr span { color:#22d3ee; }
.adm-sub { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#64748b; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:28px; }
.stat-row { display:flex; gap:12px; margin-bottom:24px; }
.stat { background:#0d1420; border:1px solid #1e2d42; border-radius:8px; padding:14px 18px; min-width:120px; }
.stat-num { font-family:'Bebas Neue',sans-serif; font-size:28px; color:#60a5fa; line-height:1; }
.stat-lbl { font-family:'IBM Plex Mono',monospace; font-size:9px; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-top:3px; }
.user-row { display:grid; grid-template-columns:200px 180px 100px 100px 120px 1fr; gap:10px; padding:11px 14px; border-bottom:1px solid #1a2540; align-items:center; font-family:'IBM Plex Mono',monospace; font-size:10px; }
.user-hdr { color:#64748b; font-size:9px; text-transform:uppercase; letter-spacing:0.1em; border-bottom:2px solid #243450 !important; }
.s-pending  { color:#fbbf24; background:rgba(245,158,11,0.12); padding:2px 8px; border-radius:3px; border:1px solid rgba(245,158,11,0.25); }
.s-approved { color:#34d399; background:rgba(16,185,129,0.12); padding:2px 8px; border-radius:3px; border:1px solid rgba(16,185,129,0.25); }
.s-rejected { color:#f87171; background:rgba(239,68,68,0.12); padding:2px 8px; border-radius:3px; border:1px solid rgba(239,68,68,0.25); }
.t-pro   { color:#60a5fa; }
.t-inst  { color:#c084fc; }
.t-free  { color:#94a3b8; }
.t-none  { color:#475569; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="adm-hdr">RIPPLE<span>POINT</span> Admin</div>', unsafe_allow_html=True)
st.markdown(f'<div class="adm-sub">Access Control Panel · Logged in as {user.get("email","")}</div>', unsafe_allow_html=True)

# ── LOAD USERS ────────────────────────────────────────────────────────────────
users = get_all_users()

if not users:
    st.warning("No users found, or Supabase connection issue.")
    st.stop()

# ── STATS ─────────────────────────────────────────────────────────────────────
total    = len(users)
pending  = sum(1 for u in users if u.get("status") == "pending")
approved = sum(1 for u in users if u.get("status") == "approved")
rejected = sum(1 for u in users if u.get("status") == "rejected")

st.markdown(f"""
<div class="stat-row">
  <div class="stat"><div class="stat-num">{total}</div><div class="stat-lbl">Total Users</div></div>
  <div class="stat"><div class="stat-num" style="color:#fbbf24">{pending}</div><div class="stat-lbl">Pending</div></div>
  <div class="stat"><div class="stat-num" style="color:#34d399">{approved}</div><div class="stat-lbl">Approved</div></div>
  <div class="stat"><div class="stat-num" style="color:#f87171">{rejected}</div><div class="stat-lbl">Rejected</div></div>
</div>
""", unsafe_allow_html=True)

# ── FILTER ────────────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns([2, 4])
with col_f1:
    filter_status = st.selectbox("Filter by status",
        ["All", "Pending", "Approved", "Rejected"], index=0)

filtered = users if filter_status == "All" else [
    u for u in users if u.get("status","").lower() == filter_status.lower()
]

# ── TABLE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="user-row user-hdr">
  <div>Name</div><div>Email</div><div>Status</div>
  <div>Tier</div><div>Registered</div><div>Actions</div>
</div>
""", unsafe_allow_html=True)

# ── USER ROWS ─────────────────────────────────────────────────────────────────
for u in filtered:
    uid      = u.get("id","")
    name     = u.get("full_name", "—")[:28]
    email    = u.get("email","—")
    status   = u.get("status","pending")
    tier     = u.get("tier","none")
    created  = u.get("created_at","")[:10]

    status_class = {"pending":"s-pending","approved":"s-approved","rejected":"s-rejected"}.get(status,"s-pending")
    tier_class   = {"pro":"t-pro","institutional":"t-inst","free":"t-free","none":"t-none"}.get(tier,"t-none")

    col1, col2, col3, col4, col5, col6 = st.columns([2, 2.5, 1.2, 1.2, 1.2, 2.5])

    with col1:
        st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#e2e8f0;">{name}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#94a3b8;">{email}</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="{status_class}" style="font-family:IBM Plex Mono,monospace;font-size:9px;">{status.upper()}</span>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<span class="{tier_class}" style="font-family:IBM Plex Mono,monospace;font-size:10px;">{tier.upper()}</span>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<span style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#64748b;">{created}</span>', unsafe_allow_html=True)

    with col6:
        action_cols = st.columns([1, 1, 1, 1.8])
        with action_cols[0]:
            if st.button("✓ Free", key=f"free_{uid}", help="Approve — Free tier"):
                if update_user_status(uid, "approved", "free"):
                    st.success(f"Approved {name} → Free")
                    st.rerun()
        with action_cols[1]:
            if st.button("✓ Pro", key=f"pro_{uid}", help="Approve — Pro tier"):
                if update_user_status(uid, "approved", "pro"):
                    st.success(f"Approved {name} → Pro")
                    st.rerun()
        with action_cols[2]:
            if st.button("✓ Inst", key=f"inst_{uid}", help="Approve — Institutional"):
                if update_user_status(uid, "approved", "institutional"):
                    st.success(f"Approved {name} → Institutional")
                    st.rerun()
        with action_cols[3]:
            if st.button("✗ Reject", key=f"rej_{uid}", help="Reject access"):
                if update_user_status(uid, "rejected", "none"):
                    st.warning(f"Rejected {name}")
                    st.rerun()

    st.markdown('<div style="border-bottom:1px solid #141e30;"></div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:32px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:#334155;">
  RIPPLEPOINT Admin · {total} users · Last refreshed: now · rippleaxis.in@gmail.com
</div>
""", unsafe_allow_html=True)

