import streamlit as st
import json
import os
import requests
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RIPPLEPOINT — Global Macro Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── AUTH IMPORTS + GATE ───────────────────────────────────────────────────────
from auth import is_logged_in, current_user, is_approved, supabase_sign_out
from login_page import render_login_page

# ── F2: SESSION PERSISTENCE — restore session from query params or cookie ─────
def restore_session():
    """Try to restore session from stored token in session state."""
    if st.session_state.get("rp_logged_in"):
        return True
    # Check if token was stored before rerun
    token = st.session_state.get("_rp_token_persist")
    user  = st.session_state.get("_rp_user_persist")
    if token and user:
        st.session_state.rp_logged_in = True
        st.session_state.rp_token     = token
        st.session_state.rp_user      = user
        return True
    return False

def persist_session():
    """Store session data for persistence across reruns."""
    if st.session_state.get("rp_logged_in"):
        st.session_state._rp_token_persist = st.session_state.get("rp_token")
        st.session_state._rp_user_persist  = st.session_state.get("rp_user")

# Attempt restore then check
restore_session()
persist_session()

if not is_logged_in() or not is_approved():
    render_login_page()
    st.stop()

user = current_user()

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        with open("dashboard_data.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Could not load dashboard_data.json: {e}")
        return {}

data = load_data()

# ── SAFE GETTERS ──────────────────────────────────────────────────────────────
curr = data.get("current", {})
c3   = data.get("chart3_radar", {})
c4   = data.get("chart4_heatmap", {})
c6   = data.get("chart6_cci",    {})
hist = data.get("chart1_gcpi_trend", {})

def g(key, default="—"):
    v = curr.get(key, data.get(key, default))
    return v if v is not None else default

def gf(key, default=0.0):
    try:
        v = curr.get(key, data.get(key, default))
        return float(v) if v is not None else default
    except:
        return default

def gz(ticker):
    tickers = c4.get("tickers", [])
    zscores = c4.get("z_scores", [])
    try:
        idx = tickers.index(ticker)
        return float(zscores[idx])
    except:
        return 0.0

def gz_zone(z):
    if z <= -2.0: return "Sig. Dev. Downside"
    if z <= -1.0: return "Mild Dev. Downside"
    if z >= 2.0:  return "Sig. Dev. Upside"
    if z >= 1.0:  return "Mild Dev. Upside"
    return "Normal Range"

# ── AI NARRATIVE ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=900)
def get_ai_narrative(gcpi, phase, grci, cci, alpha, run_context):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return "AI narrative unavailable — ANTHROPIC_API_KEY not set."
    try:
        payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 280,
            "system": (
                f"You are RIPPLEPOINT, a macro intelligence engine for Ripple Axis Systems. "
                f"You are viewing the {run_context} update. "
                f"Write 3 sentences of precise, institutional-grade macro narrative. "
                f"No hedging. No bullet points. No headers. Pure prose only."
            ),
            "messages": [{
                "role": "user",
                "content": (
                    f"Current reading: GCPI {gcpi:.1f}, "
                    f"Phase {phase}, GRCI {grci:.3f}, "
                    f"CCI {cci:.4f}, Alpha {alpha:.3f}. "
                    f"Generate the regime narrative."
                )
            }]
        }
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json=payload, timeout=15
        )
        return r.json()["content"][0]["text"]
    except Exception as e:
        return f"Narrative generation error: {str(e)[:80]}"

# ── COLOUR HELPERS ────────────────────────────────────────────────────────────
def gcpi_color(v):
    if v >= 70: return "#f87171"
    if v >= 50: return "#fbbf24"
    if v >= 30: return "#10b981"
    return "#60a5fa"

def z_color(v):
    if v <= -2.0: return "#f87171"
    if v <= -1.0: return "#fbbf24"
    if v >= 2.0:  return "#f87171"
    if v >= 1.0:  return "#fbbf24"
    return "#34d399"

def phase_color(p):
    colors = {"1":"#10b981","2":"#22d3ee","3":"#fbbf24",
              "4":"#ef4444","5":"#8b5cf6","6":"#ec4899"}
    return colors.get(str(p), "#94a3b8")

# ── EXTRACT KEY VALUES ────────────────────────────────────────────────────────
gcpi_val     = gf("gcpi_score",      54.22)
eff_gcpi     = gf("effective_gcpi",  63.33)
grci_val     = gf("grci_score",      0.200)
cci_val      = gf("cci_score",       0.6885)
alpha_val    = gf("alpha_gcpi",      0.740)
phase_num    = str(int(gf("phase",   3)))
rbi_room     = gf("rbi_room",        0.5)
rbi_const    = g("rbi_constraint",   "Constrained")
active_rule  = g("active_rule",      "PRE-ALERT MONITORING")
cci_dir      = g("cci_direction",    "STAGFLATIONARY")

# F9: Fix macro cards — read correct key names from JSON
nifty_close  = gf("nifty_close",    0.0)
sp500_close  = gf("sp500_close",    0.0)
dxy_close    = gf("dxy_close",      0.0)
brent_close  = gf("brent_close",    0.0)
vix_close    = gf("vix_close",      0.0)
india_vix    = gf("india_vix_close",0.0)
usdinr_close = gf("usdinr_close",   0.0)

# Derived labels
def gcpi_zone_label(v):
    if v >= 70: return "RED"
    if v >= 50: return "ORANGE"
    if v >= 30: return "YELLOW"
    return "GREEN"

def grci_status_label(v):
    if v >= 0.80: return "CONFIRMED"
    if v >= 0.60: return "BUILDING"
    if v >= 0.40: return "WATCH"
    return "STABLE"

def alpha_status_label(v):
    if v >= 0.80: return "Coherent"
    if v >= 0.70: return "Converging"
    return "Diverging"

def cci_status_label(d):
    d = str(d).upper()
    if "STAG" in d: return "STAGFLATIONARY"
    if "UP"   in d: return "UPSIDE PRESSURE"
    if "DOWN" in d: return "DOWNSIDE DRAG"
    return d if d else "NEUTRAL"

gcpi_zone    = gcpi_zone_label(gcpi_val)
grci_status  = grci_status_label(grci_val)
alpha_status = alpha_status_label(alpha_val)
cci_status   = cci_status_label(cci_dir)

phase_name_map = {
    "1":"Stable Equilibrium","2":"Compression Building",
    "3":"Volatility Expansion","4":"Active Fragility",
    "5":"Active Recovery","6":"Conflicted Regime"
}
phase_name = phase_name_map.get(phase_num, "Volatility Expansion")

as_of_date = data.get("generated", datetime.now().strftime("%Y-%m-%d"))[:10]
try:
    as_of_date = datetime.strptime(as_of_date, "%Y-%m-%d").strftime("%d %b %Y")
except:
    pass
issue_num  = data.get("issue_number", "—")
run_label  = data.get("run_label", "—")

# Z-scores
nifty_z20   = gz("NIFTY50")
sp500_z20   = gz("SP500")
dxy_z20     = gz("DXY")
usdinr_z20  = gz("USDINR")
nasdaq_z20  = gz("NASDAQ100")
bnk_z20     = gz("BANKNIFTY")
hsi_z20     = gz("HANGSENG")
brent_z20   = gz("BRENT")
gold_z20    = gz("GOLD")

# GCPI 6 dimensions
radar_scores = c3.get("scores", [0.55, 0.58, 0.60, 0.52, 0.65, 0.70])
gcpi_d1 = float(radar_scores[0]) if len(radar_scores) > 0 else 0.55
gcpi_d2 = float(radar_scores[1]) if len(radar_scores) > 1 else 0.58
gcpi_d3 = float(radar_scores[2]) if len(radar_scores) > 2 else 0.60
gcpi_d4 = float(radar_scores[3]) if len(radar_scores) > 3 else 0.52
gcpi_d5 = float(radar_scores[4]) if len(radar_scores) > 4 else 0.65
gcpi_d6 = float(radar_scores[5]) if len(radar_scores) > 5 else 0.70

# CCI segments
cci_segs_raw = c6.get("segments", {})
def cci_seg(ticker, default=0.55):
    seg = cci_segs_raw.get(ticker, {})
    z = seg.get("z20", default)
    return float(z) if z is not None else default

cci_energy   = cci_seg("BRENT",   0.72)
cci_metals   = cci_seg("COPPER",  0.58)
cci_agri     = cci_seg("WHEAT",   0.61)
cci_precious = cci_seg("GOLD",    0.55)

# History for signal log
hist_dates  = hist.get("dates",  [])
hist_gcpi   = hist.get("gcpi",   [])
hist_phases = hist.get("phases", [])
history_rows = []
if hist_dates and hist_gcpi:
    for i in range(max(0, len(hist_dates)-6), len(hist_dates)):
        try:
            history_rows.append({
                "date":           hist_dates[i],
                "gcpi":           hist_gcpi[i],
                "grci":           grci_val,
                "cronbach_alpha": alpha_val,
                "phase_number":   hist_phases[i] if hist_phases and i < len(hist_phases) else phase_num,
                "phase_name":     phase_name_map.get(str(int(hist_phases[i])) if hist_phases and i < len(hist_phases) else phase_num, phase_name),
                "regime_signal":  active_rule,
            })
        except:
            pass

hour_ist = (datetime.utcnow().hour + 5) % 24 + (1 if datetime.utcnow().minute >= 30 else 0)
run_context = data.get("run_context",
    "India market close (5:00 PM IST)" if 16 <= hour_ist <= 18 else
    "global market open (8:30 AM IST)" if 7 <= hour_ist <= 10 else "scheduled")

# ── MASTER CSS — injected inline ─────────────────────────────────────────────
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue'
    '&family=IBM+Plex+Mono:wght@300;400;500;600'
    '&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400'
    '&display=swap" rel="stylesheet">',
    unsafe_allow_html=True
)
_CSS = """ :root {
  --bg:#080c14; --bg2:#0d1420; --bg3:#111927; --bg4:#161f2e;
  --border:#1e2d42; --bord2:#243450;
  --txt:#e2e8f0; --txt2:#94a3b8; --txt3:#64748b;
  --blue:#3b82f6; --blue2:#60a5fa; --cyan:#22d3ee;
  --green:#10b981; --green2:#34d399;
  --amber:#f59e0b; --amber2:#fbbf24;
  --red:#ef4444; --red2:#f87171; --purple:#8b5cf6;
}
html,body,[data-testid="stAppViewContainer"],
[data-testid="stApp"],.main,.block-container {
  background:#080c14 !important;
  color:#e2e8f0 !important;
  font-family:'Crimson Pro',Georgia,serif !important;
}
[data-testid="stAppViewContainer"]::before {
  content:''; position:fixed; inset:0;
  background-image:
    linear-gradient(rgba(59,130,246,0.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(59,130,246,0.025) 1px,transparent 1px);
  background-size:48px 48px; pointer-events:none; z-index:0;
}
[data-testid="stSidebar"] {
  background:#0d1420 !important;
  border-right:1px solid #1e2d42 !important;
}
[data-testid="stSidebar"] > div { padding:0 !important; }
[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stSidebarCollapseButton"] { display:none !important; }
button[aria-label="Close sidebar"] { display:none !important; }
button[aria-label="Open sidebar"] { display:none !important; }
#MainMenu,footer,header,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display:none !important; }
.block-container { padding:0 !important; max-width:100% !important; }
[data-testid="stVerticalBlock"] { gap:0 !important; }
.rp-panel { background:#111927; border:1px solid #1e2d42; border-radius:8px; overflow:hidden; margin-bottom:14px; }
.rp-panel-hdr { padding:10px 14px; border-bottom:1px solid #1e2d42; display:flex; align-items:center; justify-content:space-between; }
.rp-panel-title { font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:0.12em; text-transform:uppercase; color:#94a3b8; font-weight:600; }
.rp-panel-body { padding:14px; }
.rp-section { font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:0.18em; text-transform:uppercase; color:#64748b; margin:20px 0 12px; padding-bottom:8px; border-bottom:1px solid #1e2d42; display:flex; align-items:center; gap:10px; }
.rp-section span { color:#94a3b8; }
.rp-regime { background:linear-gradient(135deg,#0d1e35 0%,#0a1628 100%); border:1px solid #243450; border-radius:10px; padding:22px 24px; margin-bottom:18px; position:relative; overflow:hidden; animation:fadeUp 0.4s ease both; }
@keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.rp-regime-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.18em; text-transform:uppercase; color:#64748b; margin-bottom:4px; }
.rp-regime-title { font-family:'Bebas Neue',sans-serif; font-size:30px; letter-spacing:0.06em; color:#fff; line-height:1; margin-bottom:16px; }
.rp-regime-statement { font-family:'Crimson Pro',Georgia,serif; font-size:15px; font-style:italic; color:#94a3b8; line-height:1.7; padding-left:14px; margin-bottom:14px; }
.rp-flags { display:flex; gap:6px; flex-wrap:wrap; }
.rp-chips { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:16px; }
.rp-chip { background:rgba(0,0,0,0.35); border:1px solid #243450; border-radius:8px; padding:10px 14px; text-align:center; min-width:80px; }
.rp-chip-lbl { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.1em; color:#64748b; text-transform:uppercase; margin-bottom:3px; }
.rp-chip-val { font-family:'Bebas Neue',sans-serif; font-size:24px; letter-spacing:0.04em; line-height:1; }
.rp-chip-sub { font-family:'IBM Plex Mono',monospace; font-size:9px; color:#64748b; margin-top:2px; }
.fc { font-family:'IBM Plex Mono',monospace; font-size:10px; font-weight:500; padding:4px 10px; border-radius:4px; letter-spacing:0.05em; display:inline-block; }
.fc-red   { background:rgba(239,68,68,0.15);  color:#f87171; border:1px solid rgba(239,68,68,0.3); }
.fc-amber { background:rgba(245,158,11,0.15); color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }
.fc-green { background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3); }
.fc-blue  { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
.fc-grey  { background:rgba(100,116,139,0.15);color:#94a3b8; border:1px solid #243450; }
.mc-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:10px; margin-bottom:18px; }
.mc { background:#161f2e; border:1px solid #1e2d42; border-radius:6px; padding:12px 13px; }
.mc-lbl { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.1em; text-transform:uppercase; color:#64748b; margin-bottom:5px; }
.mc-val { font-family:'Bebas Neue',sans-serif; font-size:22px; letter-spacing:0.04em; line-height:1; margin-bottom:2px; }
.mc-chg { font-family:'IBM Plex Mono',monospace; font-size:10px; margin-bottom:2px; }
.mc-status { font-family:'IBM Plex Mono',monospace; font-size:9px; color:#64748b; }
.gauge-row { display:flex; align-items:center; gap:10px; margin-bottom:9px; }
.gauge-lbl { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#94a3b8; width:72px; flex-shrink:0; letter-spacing:0.03em; }
.gauge-track { flex:1; height:8px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden; }
.gauge-fill { height:100%; border-radius:4px; transition:width 0.8s ease; }
.gauge-num { font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:600; width:38px; text-align:right; flex-shrink:0; }
.gauge-zone { font-family:'IBM Plex Mono',monospace; font-size:9px; width:56px; flex-shrink:0; letter-spacing:0.03em; }
.stretch-row { display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.04); }
.stretch-row:last-child { border-bottom:none; }
.stretch-name { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#94a3b8; width:110px; flex-shrink:0; }
.stretch-track { flex:1; height:6px; background:rgba(255,255,255,0.05); border-radius:3px; position:relative; }
.stretch-track::after { content:''; position:absolute; left:50%; top:-3px; width:1px; height:12px; background:rgba(255,255,255,0.18); }
.stretch-fill { position:absolute; height:6px; border-radius:3px; top:0; }
.stretch-z { font-family:'IBM Plex Mono',monospace; font-size:10px; font-weight:600; width:46px; text-align:right; flex-shrink:0; }
.stretch-lbl { font-family:'IBM Plex Mono',monospace; font-size:9px; width:130px; flex-shrink:0; text-align:right; }
.live-dot { display:flex; align-items:center; gap:6px; font-family:'IBM Plex Mono',monospace; font-size:10px; color:#34d399; letter-spacing:0.08em; }
.live-dot::before { content:''; width:7px; height:7px; background:#34d399; border-radius:50%; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.85)} }
.disclaimer { background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.15); border-radius:6px; padding:10px 14px; margin-bottom:18px; font-family:'IBM Plex Mono',monospace; font-size:9.5px; color:#64748b; line-height:1.6; }
.disclaimer strong { color:#fbbf24; }
.rp-topbar { background:#0d1420; border-bottom:1px solid #1e2d42; padding:13px 24px; display:flex; align-items:center; justify-content:space-between; margin-bottom:0; }
.rp-topbar-left { font-family:'IBM Plex Mono',monospace; font-size:11px; color:#94a3b8; letter-spacing:0.04em; }
.rp-topbar-left strong { color:#e2e8f0; }
.alpha-row { display:flex; align-items:center; gap:8px; margin-top:10px; padding-top:10px; border-top:1px solid #1e2d42; }
.alpha-lbl { font-family:'IBM Plex Mono',monospace; font-size:9px; color:#64748b; letter-spacing:0.1em; text-transform:uppercase; }
.alpha-val { font-family:'IBM Plex Mono',monospace; font-size:13px; font-weight:600; color:#34d399; }
.alpha-badge { font-family:'IBM Plex Mono',monospace; font-size:9px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.25); color:#34d399; padding:2px 8px; border-radius:3px; letter-spacing:0.05em; }
.cci-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.cci-seg { background:#161f2e; border:1px solid #1e2d42; border-radius:6px; padding:10px 12px; }
.cci-seg-lbl { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.1em; text-transform:uppercase; color:#64748b; margin-bottom:3px; }
.cci-seg-val { font-family:'IBM Plex Mono',monospace; font-size:11px; font-weight:600; margin-bottom:2px; }
.cci-seg-dir { font-family:'IBM Plex Mono',monospace; font-size:9px; }
.sig-log-row { display:grid; grid-template-columns:100px 55px 55px 55px 70px 80px 1fr; gap:6px; padding:7px 0; border-bottom:1px solid rgba(255,255,255,0.04); font-family:'IBM Plex Mono',monospace; font-size:10px; align-items:center; }
.sig-log-row:last-child { border-bottom:none; }
.sig-log-hdr { color:#64748b; font-size:9px; letter-spacing:0.08em; text-transform:uppercase; padding-bottom:7px; border-bottom:1px solid #243450 !important; }
.sc-row { margin-bottom:11px; }
.sc-hdr { display:flex; justify-content:space-between; margin-bottom:4px; }
.sc-name { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#94a3b8; letter-spacing:0.03em; }
.sc-prob { font-family:'IBM Plex Mono',monospace; font-size:10px; font-weight:600; }
.sc-track { height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden; }
.sc-fill { height:100%; border-radius:3px; }
.sb-logo { font-family:'Bebas Neue',sans-serif; font-size:26px; letter-spacing:0.08em; color:#fff; line-height:1; }
.sb-logo span { color:#22d3ee; }
.sb-sub { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.12em; color:#64748b; text-transform:uppercase; margin-top:3px; }
.sb-phase { border-radius:6px; padding:8px 10px; text-align:center; margin-top:14px; }
.sb-phase-lbl { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.12em; color:#64748b; text-transform:uppercase; margin-bottom:3px; }
.sb-phase-val { font-family:'Bebas Neue',sans-serif; font-size:18px; letter-spacing:0.05em; line-height:1; }
.sb-nav-section { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:0.15em; color:#64748b; text-transform:uppercase; padding:12px 0 6px; }
.sb-user { font-family:'IBM Plex Mono',monospace; font-size:9px; color:#64748b; padding:10px 18px 0; }
.sb-user span { color:#60a5fa; }
.sb-disclaimer { font-family:'IBM Plex Mono',monospace; font-size:8.5px; color:#64748b; line-height:1.6; margin-top:16px; padding-top:12px; border-top:1px solid #1e2d42; }
div[data-testid="stButton"] > button[kind="secondary"] {
  background:transparent !important; border:1px solid #1e2d42 !important;
  color:#64748b !important; font-family:'IBM Plex Mono',monospace !important;
  font-size:10px !important; letter-spacing:0.06em !important;
  padding:4px 12px !important; border-radius:4px !important; width:100% !important;
}

/* ── TOOLTIPS ── */
.tooltip {
  position: relative;
  cursor: help;
  border-bottom: 1px dashed #334155;
}
.tooltip::after {
  content: attr(data-tip);
  position: absolute;
  bottom: 125%;
  left: 50%;
  transform: translateX(-50%);
  background: #0d1420;
  border: 1px solid #243450;
  color: #94a3b8;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  line-height: 1.6;
  padding: 8px 12px;
  border-radius: 6px;
  white-space: pre-line;
  width: 220px;
  text-align: left;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
  z-index: 9999;
}
.tooltip:hover::after {
  opacity: 1;
}
 """
st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    phase_border_col = phase_color(phase_num)
    st.markdown(f"""
    <div style="padding:22px 18px 16px;border-bottom:1px solid var(--border);">
      <div class="sb-logo">RIPPLE<span>POINT</span></div>
      <div class="sb-sub">Global Macro Intelligence</div>
      <div class="sb-phase" style="border:1px solid {phase_border_col}44;background:{phase_border_col}18;">
        <div class="sb-phase-lbl">Current Regime</div>
        <div class="sb-phase-val" style="color:{phase_border_col};">Phase {phase_num} — {phase_name}</div>
      </div>
    </div>
    <div class="sb-user" style="padding:10px 18px 0;">
      Logged in as <span>{user.get('full_name','').split()[0] if user.get('full_name') else user.get('email','')}</span>
      &nbsp;·&nbsp; <span style="color:{'#c084fc' if user.get('tier')=='institutional' else '#60a5fa' if user.get('tier')=='pro' else '#94a3b8'};">{user.get('tier','free').upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("Dashboards", ["Net Regime Signal", "Global Stretch Map",
                        "RSDM Pair Matrix", "Macro Anchors"]),
        ("Engines",    ["GCPI Diagnostic", "GRCI Diagnostic",
                        "CCI Commodities", "TRM — Ripple Chain"]),
        ("Research",   ["Scenario Matrix", "Signal Log", "Weekly Report"]),
        ("Output Lens",["🇮🇳 India Lens", "🇺🇸 US Lens", "🌏 EM Lens"]),
    ]

    for section, items in nav_items:
        st.markdown(f'<div style="padding:2px 18px;"><div class="sb-nav-section">{section}</div></div>',
                    unsafe_allow_html=True)
        for item in items:
            is_active = (item == "Net Regime Signal") or (item == "🇮🇳 India Lens")
            bg     = "rgba(59,130,246,0.08)" if is_active else "transparent"
            col    = "#60a5fa" if is_active else "#94a3b8"
            border = "#3b82f6" if is_active else "transparent"
            dot_c  = "#60a5fa" if is_active else "#64748b"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:8px 18px;
                        background:{bg};border-left:3px solid {border};cursor:pointer;">
              <div style="width:6px;height:6px;border-radius:50%;background:{dot_c};flex-shrink:0;"></div>
              <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;
                           color:{col};letter-spacing:0.03em;">{item}</span>
            </div>""", unsafe_allow_html=True)

    admin_emails = os.environ.get("ADMIN_EMAILS", "").split(",")
    if user.get("email","").strip() in [e.strip() for e in admin_emails]:
        st.markdown("""
        <div style="padding:2px 18px;"><div class="sb-nav-section">Admin</div></div>
        <div style="padding:4px 18px;">
          <a href="/admin" style="font-family:'IBM Plex Mono',monospace;font-size:11px;
             color:#f87171;letter-spacing:0.03em;text-decoration:none;">
            ⚙ User Management
          </a>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div style="padding:0 18px 16px;">', unsafe_allow_html=True)
    if st.button("Sign Out", key="signout", type="secondary"):
        supabase_sign_out()
        st.rerun()

    st.markdown(f"""
      <div class="sb-disclaimer">
        For research purposes only.<br>
        Not investment advice.<br>
        Not SEBI registered advisory.<br>
        © Ripple Axis Systems 2026
      </div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════
top_bord = phase_color(phase_num)

st.markdown(f"""
<div class="rp-topbar">
  <div class="rp-topbar-left">
    <strong>RIPPLEPOINT</strong> &nbsp;·&nbsp;
    Net Regime Signal &nbsp;·&nbsp;
    As of {as_of_date} &nbsp;·&nbsp;
    Issue #{issue_num}
    {f'&nbsp;·&nbsp; {run_label}' if run_label != '—' else ''}
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <div class="live-dot">PIPELINE ACTIVE</div>
    <span class="fc fc-blue">🇮🇳 INDIA LENS</span>
  </div>
</div>
<div style="padding:20px 24px 0;">
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
  <strong>Research Disclaimer:</strong> All outputs on this platform are statistical observations
  and macro regime classifications produced for research purposes only. Nothing here constitutes
  investment advice, a recommendation to transact in any security, or a solicitation of any kind.
  RIPPLEPOINT is not registered as an investment advisor with SEBI or any regulatory authority.
  Users are solely responsible for their investment decisions.
</div>
""", unsafe_allow_html=True)

# ── SECTION 01 ────────────────────────────────────────────────────────────────
st.markdown('<div class="rp-section"><span>01</span> Net Regime Signal</div>',
            unsafe_allow_html=True)

narrative = get_ai_narrative(gcpi_val, phase_num, grci_val, cci_val, alpha_val, run_context)

gcpi_int   = int(gcpi_val)
eff_int    = int(eff_gcpi)
phase_full = phase_name_map.get(phase_num, phase_name)
flag_class = "fc-amber" if float(gcpi_val) < 70 else "fc-red"

st.markdown(f"""
<div class="rp-regime" style="border-top:3px solid {top_bord};">
  <div class="rp-regime-eyebrow">
    Ripple Axis Systems · India Lens · {as_of_date}
    {f' · {run_label}' if run_label != '—' else ''}
  </div>
  <div class="rp-regime-title">{phase_full} <span style="color:{top_bord};">Regime</span></div>
  <div class="rp-chips">
    <div class="rp-chip">
      <div class="rp-chip-lbl">GCPI</div>
      <div class="rp-chip-val" style="color:{gcpi_color(gcpi_val)};">{gcpi_int}</div>
      <div class="rp-chip-sub">{gcpi_zone}</div>
    </div>
    <div class="rp-chip">
      <div class="rp-chip-lbl">Eff. GCPI</div>
      <div class="rp-chip-val" style="color:{gcpi_color(eff_gcpi)};">{eff_int}</div>
      <div class="rp-chip-sub">+CCI AMP</div>
    </div>
    <div class="rp-chip">
      <div class="rp-chip-lbl">GRCI</div>
      <div class="rp-chip-val" style="color:#c084fc;">{grci_val:.3f}</div>
      <div class="rp-chip-sub">{grci_status}</div>
    </div>
    <div class="rp-chip">
      <div class="rp-chip-lbl">CCI</div>
      <div class="rp-chip-val" style="color:#fbbf24;">{cci_val:.4f}</div>
      <div class="rp-chip-sub">{cci_status[:10]}</div>
    </div>
    <div class="rp-chip">
      <div class="rp-chip-lbl">α</div>
      <div class="rp-chip-val" style="color:#34d399;">{alpha_val:.3f}</div>
      <div class="rp-chip-sub">{alpha_status}</div>
    </div>
  </div>
  <div class="rp-regime-statement" style="border-left:3px solid {top_bord};">
    {narrative}
  </div>
  <div class="rp-flags">
    <span class="fc {flag_class}">PHASE {phase_num} — {phase_full.upper()}</span>
    <span class="fc fc-amber">CCI {cci_status.upper()}</span>
    <span class="fc fc-grey">GRCI: {grci_status.upper()} · {grci_val:.3f}</span>
    <span class="fc fc-grey">α = {alpha_val:.3f} · {alpha_status.upper()}</span>
    <span class="fc fc-amber">PRE-ALERT MONITORING</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SECTION 02 — KEY MACRO READINGS ──────────────────────────────────────────
st.markdown('<div class="rp-section"><span>02</span> Key Macro Readings — India Lens</div>',
            unsafe_allow_html=True)

# F9: Use correct _close key names — now showing real values
macro_fields = [
    ("DXY Index",       f"{dxy_close:.2f}"    if dxy_close    else "—", "▲ Watch Level",     "Threshold: 99.6",  "#f87171"),
    ("USD / INR",       f"{usdinr_close:.2f}" if usdinr_close else "—", "▲ Rupee Pressure",  "RBI monitoring",   "#fbbf24"),
    ("India-US Spread", g("spread_in_us","—"), "bps",                    "Threshold: 250bps", "#f87171"),
    ("Brent Crude",     f"${brent_close:.1f}" if brent_close  else "—", "Moderate pressure", "Severe: $105",     "#fbbf24"),
    ("India VIX",       f"{india_vix:.2f}"    if india_vix    else "—", "▲ Elevated",        "Recovery: <14",    "#f87171"),
    ("CBOE VIX",        f"{vix_close:.2f}"    if vix_close    else "—", "▲ Risk-off",        "Recovery: <16",    "#f87171"),
    ("FII Flow MTD",    g("fii_mtd","—"),      "Net flow",               "Cr. — MTD",         "#f87171"),
    ("US HY Spread",    g("us_hy_spread","—"), "bps",                    "Watch >550",        "#fbbf24"),
]

mc_html = '<div class="mc-grid">'
for lbl, val, chg, status, col in macro_fields:
    mc_html += f"""
    <div class="mc">
      <div class="mc-lbl">{lbl}</div>
      <div class="mc-val" style="color:{col};">{val}</div>
      <div class="mc-chg" style="color:{col};">{chg}</div>
      <div class="mc-status">{status}</div>
    </div>"""
mc_html += '</div>'
st.markdown(mc_html, unsafe_allow_html=True)

# ── GCPI ENGINE + STRETCH ─────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="medium")

with col_left:
    # Tooltips explain each GCPI dimension
    gcpi_dims = [
        ("D1 Valuation",  gcpi_d1, "ELEVATED",
         "Equity & bond valuation vs historical norms.\nHigh = markets overvalued vs fundamentals."),
        ("D2 Liquidity",  gcpi_d2, "ELEVATED",
         "System-wide liquidity conditions.\nHigh = credit tightening, funding stress rising."),
        ("D3 Credit",     gcpi_d3, "ELEVATED",
         "Credit spread & default risk signals.\nHigh = corporate stress, HY spreads widening."),
        ("D4 FX/Capital", gcpi_d4, "MODERATE",
         "Cross-border capital flow & FX stress.\nHigh = EM outflows, rupee pressure, DXY strength."),
        ("D5 Vol Regime", gcpi_d5, "ELEVATED",
         "Volatility regime across asset classes.\nHigh = VIX elevated, vol expanding across markets."),
        ("D6 Contagion",  gcpi_d6, "CRITICAL",
         "Cross-asset contagion & correlation spike.\nHigh = all assets falling together, no safe haven."),
    ]
    def dim_color(v):
        if v >= 0.70: return "#f87171", "#ef4444"
        if v >= 0.50: return "#fbbf24", "#f59e0b"
        return "#34d399", "#10b981"

    rows_html = ""
    for lbl, val, zone, tip in gcpi_dims:
        tc, bc = dim_color(val)
        pct = int(val * 100)
        rows_html += (
            '<div class="gauge-row">'
            f'<div class="gauge-lbl tooltip" data-tip="{tip}">{lbl}</div>'
            f'<div class="gauge-track"><div class="gauge-fill" style="width:{pct}%;background:{bc};"></div></div>'
            f'<div class="gauge-num" style="color:{tc};">{val:.2f}</div>'
            f'<div class="gauge-zone" style="color:{tc};">{zone}</div>'
            '</div>'
        )

    alpha_badge_cls = "alpha-badge" if alpha_val >= 0.70 else ""
    _gcpi_html = (
        '<div class="rp-panel">'
        + '<div class="rp-panel-hdr">'
        + '<div class="rp-panel-title">GCPI \u2014 Fragility Engine</div>'
        + f'<span class="fc {flag_class}">{gcpi_int} \u00b7 {gcpi_zone}</span>'
        + '</div>'
        + f'<div class="rp-panel-body">{rows_html}'
        + '<div class="alpha-row">'
        + '<div class="alpha-lbl">Cronbach\'s \u03b1</div>'
        + f'<div class="alpha-val">{alpha_val:.3f}</div>'
        + f'<div class="{alpha_badge_cls}">{alpha_status.upper()}</div>'
        + '</div></div></div>'
    )
    st.markdown(_gcpi_html, unsafe_allow_html=True)

with col_right:
    stretch_assets = [
        ("NIFTY 50",     nifty_z20,  gz_zone(nifty_z20)),
        ("BANKNIFTY",    bnk_z20,    gz_zone(bnk_z20)),
        ("S&P 500",      sp500_z20,  gz_zone(sp500_z20)),
        ("NASDAQ 100",   nasdaq_z20, gz_zone(nasdaq_z20)),
        ("HANG SENG",    hsi_z20,    gz_zone(hsi_z20)),
        ("DXY",          dxy_z20,    gz_zone(dxy_z20)),
        ("USD/INR",      usdinr_z20, gz_zone(usdinr_z20)),
        ("BRENT",        brent_z20,  gz_zone(brent_z20)),
        ("GOLD",         gold_z20,   gz_zone(gold_z20)),
        ("US 10Y YIELD", gz("US10Y"),gz_zone(gz("US10Y"))),
    ]
    def z_bar_html(z):
        pct = min(abs(z) / 3.0 * 50, 50)
        col = z_color(z)
        if z < 0:
            return f'<div class="stretch-fill" style="left:calc(50% - {pct:.1f}%);width:{pct:.1f}%;background:{col};"></div>'
        return f'<div class="stretch-fill" style="left:50%;width:{pct:.1f}%;background:{col};"></div>'

    s_rows = ""
    for name, z, zone in stretch_assets:
        zc   = z_color(z)
        sign = "+" if z >= 0 else ""
        s_rows += (
            '<div class="stretch-row">'
            f'<div class="stretch-name">{name}</div>'
            '<div style="flex:1;position:relative;">'
            f'<div class="stretch-track">{z_bar_html(z)}</div>'
            '</div>'
            f'<div class="stretch-z" style="color:{zc};">{sign}{z:.2f}</div>'
            f'<div class="stretch-lbl" style="color:{zc};">{zone}</div>'
            '</div>'
        )

    st.markdown(
        '<div class="rp-panel">'
        '<div class="rp-panel-hdr">'
        '<div class="rp-panel-title">Global Stretch \u2014 Z-Score 20D</div>'
        '<span class="fc fc-grey">INDIA + GLOBAL</span>'
        '</div>'
        f'<div class="rp-panel-body">{s_rows}</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ── GRCI + CCI ────────────────────────────────────────────────────────────────
col_grci, col_cci = st.columns(2, gap="medium")

with col_grci:
    grci_sensors = [
        ("R1 Earnings",   gf("grci_r1",0.08), "Absent",
         "Earnings revision breadth.\nConfirmed when upgrades > downgrades sustained."),
        ("R2 Yield",      gf("grci_r2",0.12), "Absent",
         "India-US yield spread recovery.\nConfirmed when spread > 300bps and rising."),
        ("R3 FII Flow",   gf("grci_r3",0.05), "Absent",
         "Foreign institutional investor net flows.\nConfirmed when FII net positive 15+ days."),
        ("R4 Vol Crush",  gf("grci_r4",0.15), "Absent",
         "Volatility compression signal.\nConfirmed when India VIX < 14 sustained."),
        ("R5 Credit Ease",gf("grci_r5",0.10), "Absent",
         "Credit spread tightening signal.\nConfirmed when HY spreads falling consistently."),
        ("R6 Rupee",      gf("grci_r6",0.18), "Weak",
         "Rupee stabilisation & appreciation.\nWeak when USD/INR declining from peak."),
        ("R7 Momentum",   gf("grci_r7",0.12), "Absent",
         "Price momentum across indices.\nConfirmed when NIFTY > 50D & 200D MA."),
        ("R8 Breadth",    gf("grci_r8",0.20), "Weak",
         "Market breadth recovery.\nWeak when advance-decline ratio improving."),
    ]
    grci_rows = ""
    for lbl, val, zone, tip in grci_sensors:
        pct = int(val * 100)
        gc  = "#34d399" if val >= 0.60 else "#64748b"
        bc  = "#10b981" if val >= 0.60 else "#334155"
        grci_rows += (
            '<div class="gauge-row">'
            f'<div class="gauge-lbl tooltip" data-tip="{tip}">{lbl}</div>'
            f'<div class="gauge-track"><div class="gauge-fill" style="width:{pct}%;background:{bc};"></div></div>'
            f'<div class="gauge-num" style="color:{gc};">{val:.2f}</div>'
            f'<div class="gauge-zone" style="color:{gc};">{zone}</div>'
            '</div>'
        )

    confirm_met  = grci_val >= 0.80 and alpha_val >= 0.80
    confirm_col  = '#34d399' if confirm_met else '#64748b'
    confirm_text = 'ACTIVE' if confirm_met else 'NOT ACTIVE'
    confirm_html = (
        '<div style="display:flex;align-items:center;gap:8px;margin-top:10px;padding-top:10px;border-top:1px solid var(--border);">'
        '<span style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:var(--txt3);text-transform:uppercase;letter-spacing:0.1em;">Confirmation Rule</span>'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;font-weight:600;color:{confirm_col};">{confirm_text}</span>'
        '<span class="fc fc-grey" style="font-size:8px;">Requires GRCI &gt; 0.80 + \u03b1 &gt; 0.80</span>'
        '</div>'
    )

    _grci_html = (
        '<div class="rp-panel">'
        + '<div class="rp-panel-hdr">'
        + '<div class="rp-panel-title">GRCI \u2014 Recovery Sensor</div>'
        + f'<span class="fc fc-grey">{grci_val:.3f} \u00b7 {grci_status.upper()}</span>'
        + '</div>'
        + f'<div class="rp-panel-body">{grci_rows}{confirm_html}</div>'
        + '</div>'
    )
    st.markdown(_grci_html, unsafe_allow_html=True)

with col_cci:
    cci_segs = [
        ("Energy",     cci_energy,   "#f87171", "UPSIDE PRESSURE"),
        ("Metals",     cci_metals,   "#fbbf24", "MODERATE"),
        ("Agri",       cci_agri,     "#fbbf24", "MODERATE"),
        ("Precious",   cci_precious, "#60a5fa", "NEUTRAL"),
        ("USD Factor", rbi_room,     "#f87171", "AMPLIFYING"),
    ]
    cci_html = '<div class="cci-grid">'
    for lbl, val, col, direction in cci_segs:
        cci_html += (
            '<div class="cci-seg">'
            f'<div class="cci-seg-lbl">{lbl}</div>'
            f'<div class="cci-seg-val" style="color:{col};">{val:.2f}</div>'
            f'<div class="cci-seg-dir" style="color:{col};">{direction}</div>'
            '</div>'
        )
    cci_html += "</div>"

    cci_badge_class = "fc-amber" if "STAG" in cci_status.upper() else "fc-green"
    st.markdown(f"""
    <div class="rp-panel">
      <div class="rp-panel-hdr">
        <div class="rp-panel-title">CCI — Commodity Intelligence</div>
        <span class="fc {cci_badge_class}">{cci_val:.4f} · {cci_status.upper()}</span>
      </div>
      <div class="rp-panel-body">
        {cci_html}
        <div style="margin-top:10px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:var(--txt3);line-height:1.7;">
          Composite: {cci_val:.4f} · Classification: <span style="color:#fbbf24;">{cci_status.upper()}</span><br>
          CCI &gt; 0.65 triggers GFSI multiplier on Effective GCPI
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── SECTION 03 ────────────────────────────────────────────────────────────────
st.markdown('<div class="rp-section"><span>03</span> Scenario Matrix — 1–3 Year Probability Distribution</div>',
            unsafe_allow_html=True)

col_sc, col_log = st.columns(2, gap="medium")

with col_sc:
    scenarios = [
        ("Rolling Recession",           "25–35%", 30, "#f59e0b"),
        ("Geopolitical Escalation Shock","20–25%", 22, "#f59e0b"),
        ("Soft Landing",                "20–30%", 25, "#10b981"),
        ("Inflation Resurgence",        "15–25%", 20, "#f59e0b"),
        ("Liquidity Squeeze Event",     "10–15%", 12, "#ef4444"),
        ("Credit / Banking Event",      "5–10%",   7, "#ef4444"),
    ]
    sc_html = ""
    for name, prob, pct, col in scenarios:
        prob_col = "#f87171" if col == "#ef4444" else ("#fbbf24" if col == "#f59e0b" else "#34d399")
        sc_html += (
            '<div class="sc-row">'
            '<div class="sc-hdr">'
            f'<div class="sc-name">{name}</div>'
            f'<div class="sc-prob" style="color:{prob_col};">{prob}</div>'
            '</div>'
            f'<div class="sc-track"><div class="sc-fill" style="width:{pct}%;background:{col};"></div></div>'
            '</div>'
        )
    sc_html += '<div style="margin-top:10px;font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:var(--txt3);line-height:1.7;">Probability distributions are scenario-based research assessments, not price forecasts.</div>'
    st.markdown(
        '<div class="rp-panel">'
        '<div class="rp-panel-hdr">'
        '<div class="rp-panel-title">Six Macro Scenarios \u2014 Current Probability Weights</div>'
        '<span class="fc fc-grey">Q1 2026</span>'
        '</div>'
        f'<div class="rp-panel-body">{sc_html}</div>'
        '</div>',
        unsafe_allow_html=True
    )

with col_log:
    history  = history_rows
    log_rows = ""
    if history:
        for row in history[::-1]:
            # F10: Full date — show complete YYYY-MM-DD
            d      = str(row.get("date","—"))[:10]
            gc     = int(float(row.get("gcpi", 0)))
            gr     = float(row.get("grci", 0))
            al     = float(row.get("cronbach_alpha", 0))
            ph     = str(row.get("phase_number","—"))
            rule   = row.get("regime_signal","—")
            cls    = row.get("phase_name","—")
            gc_c   = gcpi_color(gc)
            ph_c2  = phase_color(ph)
            rule_c = "#f87171" if "VETO" in rule.upper() else \
                     "#fbbf24" if "WATCH" in rule.upper() else "#64748b"
            log_rows += (
                '<div class="sig-log-row">'
                f'<div style="color:var(--txt2);">{d}</div>'
                f'<div style="color:{gc_c};">{gc}</div>'
                f'<div style="color:var(--txt3);">{gr:.2f}</div>'
                f'<div style="color:#34d399;">{al:.2f}</div>'
                f'<div><span class="fc" style="font-size:8px;background:{ph_c2}22;color:{ph_c2};border:1px solid {ph_c2}44;padding:2px 6px;">Ph{ph}</span></div>'
                f'<div style="color:{rule_c};font-size:9px;">{rule[:12]}</div>'
                f'<div style="color:var(--txt2);">{cls[:18]}</div>'
                '</div>'
            )
    else:
        log_rows = '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:var(--txt3);padding:10px 0;">No history data available.</div>'

    _hdr = (
        '<div class="sig-log-row sig-log-hdr">'
        '<div>Date</div><div>GCPI</div><div>GRCI</div>'
        '<div>\u03b1</div><div>Phase</div><div>Rule</div><div>Regime</div>'
        '</div>'
    )
    _log_html = (
        '<div class="rp-panel">'
        + '<div class="rp-panel-hdr">'
        + '<div class="rp-panel-title">Signal Log \u2014 Live Record</div>'
        + f'<span class="fc fc-grey">Issue #{issue_num}</span>'
        + '</div>'
        + f'<div class="rp-panel-body">{_hdr}{log_rows}</div>'
        + '</div>'
    )
    st.markdown(_log_html, unsafe_allow_html=True)

# ── SECTION 04 ────────────────────────────────────────────────────────────────
st.markdown('<div class="rp-section"><span>04</span> Output Contract — Surveillance Triggers</div>',
            unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    st.markdown("""
    <div class="rp-panel">
      <div class="rp-panel-body">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:var(--txt3);margin-bottom:8px;">
          Veto Rule — All-Clear Conditions (ALL THREE Required)
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--txt2);line-height:1.9;">
          <span style="color:#f87171;">✗</span> GCPI &lt; 50 for 5+ days<br>
          <span style="color:#f87171;">✗</span> DXY &lt; 98.5 for 10+ days<br>
          <span style="color:#f87171;">✗</span> FII net positive 15+ days
        </div>
        <div style="margin-top:8px;color:#f87171;font-family:'IBM Plex Mono',monospace;font-size:9px;">ALL-CLEAR NOT MET</div>
      </div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="rp-panel">
      <div class="rp-panel-body">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:var(--txt3);margin-bottom:8px;">
          Key Surveillance Triggers — Next Period
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--txt2);line-height:1.9;">
          DXY crossing 101.0 → Severe band review<br>
          Brent crossing $95 → Moderate band trigger<br>
          India-US spread &lt; 220 bps → GCPI D2 Critical<br>
          FII outflow &gt; ₹15,000 Cr/week sustained
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="rp-panel">
      <div class="rp-panel-body">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:var(--txt3);margin-bottom:8px;">
          Historical Magnitude Reference — Phase 4 Episodes
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--txt2);line-height:1.9;">
          Mild scenario: 3–8% drawdown range<br>
          Moderate scenario: 10–18% drawdown range<br>
          Severe scenario: 20–35% drawdown range
        </div>
        <div style="margin-top:6px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:var(--txt3);">Historical frequency reference only. Not a forecast.</div>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
