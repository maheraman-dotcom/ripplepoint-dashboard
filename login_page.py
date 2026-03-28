# ═══════════════════════════════════════════════════════════════════════════
# login_page.py — RIPPLEPOINT login + registration UI
# Called from app.py when user is not authenticated
# ═══════════════════════════════════════════════════════════════════════════

import streamlit as st
from auth import supabase_sign_in, supabase_sign_up

def render_login_page():
    """Renders the full login/register wall. Sets session state on success."""

    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;500;600&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&display=swap" rel="stylesheet">
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
      background: #080c14 !important;
    }
    #MainMenu, footer, header, [data-testid="stDecoration"],
    [data-testid="stToolbar"] { display:none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    .rp-auth-wrap {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #080c14;
      background-image:
        linear-gradient(rgba(59,130,246,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59,130,246,0.025) 1px, transparent 1px);
      background-size: 48px 48px;
    }
    .rp-auth-box {
      width: 100%;
      max-width: 420px;
      background: #0d1420;
      border: 1px solid #1e2d42;
      border-radius: 12px;
      padding: 40px 36px;
      margin: 40px auto;
    }
    .rp-auth-logo {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 32px;
      letter-spacing: 0.08em;
      color: #ffffff;
      text-align: center;
      margin-bottom: 2px;
    }
    .rp-auth-logo span { color: #22d3ee; }
    .rp-auth-tagline {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: #64748b;
      text-align: center;
      margin-bottom: 28px;
    }
    .rp-tab-row {
      display: flex;
      border-bottom: 1px solid #1e2d42;
      margin-bottom: 24px;
    }
    .rp-tab {
      flex: 1;
      text-align: center;
      padding: 10px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #64748b;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -1px;
    }
    .rp-tab-active {
      color: #60a5fa;
      border-bottom-color: #3b82f6;
    }
    .rp-field-label {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #64748b;
      margin-bottom: 6px;
      margin-top: 14px;
    }
    .rp-disclaimer {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px;
      color: #475569;
      line-height: 1.7;
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid #1e2d42;
      text-align: center;
    }
    .rp-pending-box {
      background: rgba(245,158,11,0.08);
      border: 1px solid rgba(245,158,11,0.2);
      border-radius: 8px;
      padding: 14px 16px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10px;
      color: #fbbf24;
      line-height: 1.7;
      margin-top: 16px;
    }
    .rp-rejected-box {
      background: rgba(239,68,68,0.08);
      border: 1px solid rgba(239,68,68,0.2);
      border-radius: 8px;
      padding: 14px 16px;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 10px;
      color: #f87171;
      line-height: 1.7;
      margin-top: 16px;
    }
    div[data-testid="stTextInput"] input {
      background: #0a1020 !important;
      border: 1px solid #1e2d42 !important;
      border-radius: 6px !important;
      color: #e2e8f0 !important;
      font-family: 'IBM Plex Mono', monospace !important;
      font-size: 13px !important;
    }
    div[data-testid="stTextInput"] input:focus {
      border-color: #3b82f6 !important;
      box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
    }
    div[data-testid="stButton"] button {
      width: 100%;
      background: #1d4ed8 !important;
      color: #ffffff !important;
      border: none !important;
      border-radius: 6px !important;
      font-family: 'IBM Plex Mono', monospace !important;
      font-size: 12px !important;
      letter-spacing: 0.08em !important;
      text-transform: uppercase !important;
      padding: 12px !important;
      margin-top: 8px !important;
      transition: background 0.15s !important;
    }
    div[data-testid="stButton"] button:hover {
      background: #1e40af !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Tab state
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "login"

    st.markdown('<div class="rp-auth-box">', unsafe_allow_html=True)
    st.markdown("""
      <div class="rp-auth-logo">RIPPLE<span>POINT</span></div>
      <div class="rp-auth-tagline">Global Macro Intelligence · Ripple Axis Systems</div>
    """, unsafe_allow_html=True)

    # Tabs
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", key="tab_login", use_container_width=True):
            st.session_state.auth_tab = "login"
    with col2:
        if st.button("Request Access", key="tab_register", use_container_width=True):
            st.session_state.auth_tab = "register"

    st.markdown("---")

    # ── LOGIN TAB ─────────────────────────────────────────────────────────
    if st.session_state.auth_tab == "login":
        st.markdown('<div class="rp-field-label">Email Address</div>', unsafe_allow_html=True)
        email = st.text_input("Email", key="login_email", label_visibility="collapsed",
                              placeholder="your@email.com")
        st.markdown('<div class="rp-field-label">Password</div>', unsafe_allow_html=True)
        password = st.text_input("Password", key="login_password",
                                 label_visibility="collapsed",
                                 type="password", placeholder="••••••••")

        if st.button("ACCESS RIPPLEPOINT →", key="login_btn"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Authenticating..."):
                    ok, result = supabase_sign_in(email, password)

                if not ok:
                    st.error(f"Login failed: {result}")
                else:
                    # Store in session
                    st.session_state.rp_logged_in = True
                    st.session_state.rp_user      = result
                    st.session_state.rp_token     = result.get("access_token")

                    status = result.get("status", "pending")

                    if status == "pending":
                        st.markdown("""
                        <div class="rp-pending-box">
                          ACCESS PENDING APPROVAL<br><br>
                          Your registration has been received. Ripple Axis Systems
                          reviews all access requests manually. You will be notified
                          once your account is activated.<br><br>
                          Contact: rippleaxis.in@gmail.com
                        </div>""", unsafe_allow_html=True)
                        st.session_state.rp_logged_in = False
                        st.session_state.rp_user = {}

                    elif status == "rejected":
                        st.markdown("""
                        <div class="rp-rejected-box">
                          ACCESS NOT GRANTED<br><br>
                          Your access request was not approved at this time.
                          Contact rippleaxis.in@gmail.com for more information.
                        </div>""", unsafe_allow_html=True)
                        st.session_state.rp_logged_in = False

                    elif status == "approved":
                        st.success(f"Welcome back, {result.get('full_name', email).split()[0]}.")
                        st.rerun()

    # ── REGISTER TAB ──────────────────────────────────────────────────────
    else:
        st.markdown('<div class="rp-field-label">Full Name</div>', unsafe_allow_html=True)
        full_name = st.text_input("Full Name", key="reg_name",
                                  label_visibility="collapsed",
                                  placeholder="Mahesh Rajaram")
        st.markdown('<div class="rp-field-label">Email Address</div>', unsafe_allow_html=True)
        reg_email = st.text_input("Email", key="reg_email",
                                  label_visibility="collapsed",
                                  placeholder="your@email.com")
        st.markdown('<div class="rp-field-label">Password (min 8 characters)</div>', unsafe_allow_html=True)
        reg_pw = st.text_input("Password", key="reg_password",
                               label_visibility="collapsed",
                               type="password", placeholder="••••••••")
        st.markdown('<div class="rp-field-label">Confirm Password</div>', unsafe_allow_html=True)
        reg_pw2 = st.text_input("Confirm", key="reg_confirm",
                                label_visibility="collapsed",
                                type="password", placeholder="••••••••")

        if st.button("SUBMIT ACCESS REQUEST →", key="register_btn"):
            if not all([full_name, reg_email, reg_pw, reg_pw2]):
                st.error("All fields are required.")
            elif len(reg_pw) < 8:
                st.error("Password must be at least 8 characters.")
            elif reg_pw != reg_pw2:
                st.error("Passwords do not match.")
            else:
                with st.spinner("Submitting request..."):
                    ok, msg = supabase_sign_up(reg_email, reg_pw, full_name)
                if ok:
                    st.success(msg)
                    st.info("Switch to Sign In once your access is approved.")
                else:
                    st.error(msg)

    st.markdown("""
      <div class="rp-disclaimer">
        For research purposes only. Not investment advice.<br>
        Not SEBI registered. © Ripple Axis Systems 2026
      </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
