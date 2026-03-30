import streamlit as st
from auth import supabase_sign_in, supabase_sign_up

def render_login_page():

    st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        background-color: #080c14 !important;
    }
    #MainMenu, footer, header,
    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    .block-container { padding: 2rem 1rem !important; max-width: 480px !important; margin: 0 auto !important; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    div[data-testid="stTextInput"] input {
        background: #0a1020 !important;
        border: 1px solid #1e2d42 !important;
        border-radius: 6px !important;
        color: #e2e8f0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 13px !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stTextInput"] label {
        color: #64748b !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stButton"] button {
        width: 100% !important;
        background: #1d4ed8 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        padding: 12px !important;
        margin-top: 4px !important;
    }
    div[data-testid="stButton"] button:hover {
        background: #1e40af !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #0d1420 !important;
        border-bottom: 1px solid #1e2d42 !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #64748b !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom: 2px solid #3b82f6 !important;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Logo
    st.markdown("""
    <div style="text-align:center;padding:40px 0 24px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:36px;letter-spacing:0.08em;color:#ffffff;line-height:1;">
        RIPPLE<span style="color:#22d3ee;">POINT</span>
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:#64748b;margin-top:4px;">
        Global Macro Intelligence &nbsp;·&nbsp; Ripple Axis Systems
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["SIGN IN", "REQUEST ACCESS"])

    # ── SIGN IN TAB ──────────────────────────────────────────────────────────
    with tab1:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        email    = st.text_input("Email Address", key="login_email",
                                 placeholder="your@email.com")
        password = st.text_input("Password", key="login_password",
                                 type="password", placeholder="••••••••")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("ACCESS RIPPLEPOINT →", key="login_btn"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Authenticating..."):
                    ok, result = supabase_sign_in(email, password)

                if not ok:
                    st.error(f"Login failed: {result}")
                else:
                    status = result.get("status", "pending")

                    if status == "pending":
                        st.warning(
                            "**Access Pending Approval**\n\n"
                            "Your registration has been received. "
                            "Ripple Axis Systems reviews all access requests manually. "
                            "Contact: maheraman@gmail.com"
                        )
                    elif status == "rejected":
                        st.error(
                            "**Access Not Granted**\n\n"
                            "Your request was not approved. "
                            "Contact maheraman@gmail.com for more information."
                        )
                    elif status == "approved":
                        st.session_state.rp_logged_in      = True
                        st.session_state.rp_user           = result
                        st.session_state.rp_token          = result.get("access_token")
                        st.session_state._rp_token_persist = result.get("access_token")
                        st.session_state._rp_user_persist  = result
                        st.rerun()

    # ── REGISTER TAB ─────────────────────────────────────────────────────────
    with tab2:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        full_name = st.text_input("Full Name", key="reg_name",
                                  placeholder="Mahesh Rajaram")
        reg_email = st.text_input("Email Address", key="reg_email",
                                  placeholder="your@email.com")
        reg_pw    = st.text_input("Password (min 8 characters)", key="reg_pw",
                                  type="password", placeholder="••••••••")
        reg_pw2   = st.text_input("Confirm Password", key="reg_pw2",
                                  type="password", placeholder="••••••••")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

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
                else:
                    st.error(msg)

    # Disclaimer
    st.markdown("""
    <div style="text-align:center;margin-top:32px;font-family:'IBM Plex Mono',monospace;
                font-size:9px;color:#475569;line-height:1.7;padding:0 20px;">
      For research purposes only. Not investment advice.<br>
      Not SEBI registered. © Ripple Axis Systems 2026
    </div>
    """, unsafe_allow_html=True)
