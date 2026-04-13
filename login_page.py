import streamlit as st
from auth import supabase_sign_in, supabase_sign_up
import os
import requests

def send_password_reset(email):
    """Trigger Supabase password reset email."""
    supabase_url  = os.environ.get("SUPABASE_URL", "")
    supabase_anon = os.environ.get("SUPABASE_ANON_KEY", "")
    try:
        r = requests.post(
            f"{supabase_url}/auth/v1/recover",
            headers={
                "apikey": supabase_anon,
                "Content-Type": "application/json"
            },
            json={"email": email},
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def render_login_page():

    st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
    .main, .block-container, [data-testid="stSidebar"] {
        background-color: #080c14 !important;
    }
    #MainMenu, footer, header,
    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
    .login-wrap {
        min-height: 100vh;
        background: #080c14;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
    }
    .login-box {
        width: 100%;
        max-width: 460px;
        background: #0d1420;
        border: 1px solid #1e2d42;
        border-radius: 12px;
        padding: 40px 36px;
    }
    div[data-testid="stTextInput"] input {
        background: #080c14 !important;
        border: 1px solid #1e2d42 !important;
        border-radius: 6px !important;
        color: #e2e8f0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 13px !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #3b82f6 !important;
        outline: none !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
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
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        padding: 14px !important;
        margin-top: 4px !important;
        cursor: pointer !important;
        transition: background 0.2s !important;
    }
    div[data-testid="stButton"] button:hover {
        background: #1e40af !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #1e2d42 !important;
        gap: 0 !important;
        margin-bottom: 20px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #64748b !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom: 2px solid #3b82f6 !important;
        background: transparent !important;
    }
    div[data-testid="stAlert"] {
        border-radius: 6px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Logo header
    st.markdown("""
    <div style="text-align:center;padding:48px 0 28px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:40px;
                  letter-spacing:0.08em;color:#ffffff;line-height:1;">
        RIPPLE<span style="color:#22d3ee;">POINT</span>
      </div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                  letter-spacing:0.16em;text-transform:uppercase;
                  color:#475569;margin-top:6px;">
        Global Macro Intelligence &nbsp;·&nbsp; Ripple Axis Systems
      </div>
      <div style="width:40px;height:1px;background:#1e2d42;margin:20px auto 0;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Check for forgot password mode
    if st.session_state.get("show_forgot_password"):
        st.markdown("""
        <div style="text-align:center;margin-bottom:20px;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                      color:#94a3b8;letter-spacing:0.06em;">
            RESET PASSWORD
          </div>
        </div>
        """, unsafe_allow_html=True)

        reset_email = st.text_input("Email Address", key="reset_email",
                                    placeholder="your@email.com")
        if st.button("SEND RESET LINK →", key="reset_btn"):
            if not reset_email:
                st.error("Please enter your email address.")
            else:
                ok = send_password_reset(reset_email)
                if ok:
                    st.success("✅ Reset link sent. Check your email inbox.")
                    st.session_state.show_forgot_password = False
                else:
                    st.error("Could not send reset email. Please try again.")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("← Back to Sign In", key="back_btn"):
            st.session_state.show_forgot_password = False
            st.rerun()
        return

    # Main tabs
    tab1, tab2 = st.tabs(["SIGN IN", "REQUEST ACCESS"])

    # ── SIGN IN ───────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        email    = st.text_input("Email Address", key="login_email",
                                 placeholder="your@email.com")
        password = st.text_input("Password", key="login_password",
                                 type="password", placeholder="••••••••")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("ACCESS RIPPLEPOINT →", key="login_btn"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner(""):
                    ok, result = supabase_sign_in(email, password)

                if not ok:
                    st.error(f"Login failed: {result}")
                else:
                    status = result.get("status", "pending")
                    if status == "pending":
                        st.warning(
                            "**Access Pending Approval** — Your request is under review. "
                            "Contact maheraman@gmail.com for expedited access."
                        )
                    elif status == "rejected":
                        st.error(
                            "**Access Not Granted** — Contact maheraman@gmail.com "
                            "for more information."
                        )
                   elif status == "approved":
                        token = result.get("access_token", "")
                        st.session_state.rp_logged_in      = True
                        st.session_state.rp_user           = result
                        st.session_state.rp_token          = token
                        st.session_state._rp_token_persist = token
                        st.session_state._rp_user_persist  = result
                        st.query_params["token"] = token
                        st.rerun()

        # Forgot password link
        st.markdown("""
        <div style="text-align:right;margin-top:8px;">
          <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                       color:#475569;letter-spacing:0.04em;">
            Forgot your password?
          </span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Reset password →", key="forgot_btn"):
            st.session_state.show_forgot_password = True
            st.rerun()

    # ── REQUEST ACCESS ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.session_state.get("signup_success"):
            st.markdown("""
            <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                        border-radius:8px;padding:20px;text-align:center;margin:10px 0;">
              <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;
                          color:#34d399;letter-spacing:0.06em;margin-bottom:8px;">
                REQUEST RECEIVED
              </div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                          color:#64748b;line-height:1.7;">
                Your access request has been submitted.<br>
                Ripple Axis Systems reviews all requests manually.<br>
                You will be notified at your registered email.<br><br>
                <span style="color:#94a3b8;">Expected response: 1–2 business days</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("← Back to Sign In", key="back_signup"):
                st.session_state.signup_success = False
                st.rerun()
        else:
            full_name = st.text_input("Full Name", key="reg_name",
                                      placeholder="Mahesh Rajaram")
            org       = st.text_input("Organisation", key="reg_org",
                                      placeholder="Fund / Family Office / Institution")
            reg_email = st.text_input("Email Address", key="reg_email",
                                      placeholder="your@email.com")
            reg_pw    = st.text_input("Password (min 8 characters)", key="reg_pw",
                                      type="password", placeholder="••••••••")
            reg_pw2   = st.text_input("Confirm Password", key="reg_pw2",
                                      type="password", placeholder="••••••••")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            if st.button("SUBMIT ACCESS REQUEST →", key="register_btn"):
                if not all([full_name, reg_email, reg_pw, reg_pw2]):
                    st.error("All fields except Organisation are required.")
                elif len(reg_pw) < 8:
                    st.error("Password must be at least 8 characters.")
                elif reg_pw != reg_pw2:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner(""):
                        ok, msg = supabase_sign_up(reg_email, reg_pw, full_name)
                    if ok:
                        st.session_state.signup_success = True
                        st.rerun()
                    else:
                        st.error(msg)

    # Footer
    st.markdown("""
    <div style="text-align:center;margin-top:32px;padding-bottom:40px;
                font-family:'IBM Plex Mono',monospace;font-size:9px;
                color:#334155;line-height:1.8;letter-spacing:0.04em;">
      FOR RESEARCH PURPOSES ONLY &nbsp;·&nbsp; NOT INVESTMENT ADVICE<br>
      NOT SEBI REGISTERED &nbsp;·&nbsp; © RIPPLE AXIS SYSTEMS 2026
    </div>
    """, unsafe_allow_html=True)
