
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json, os, datetime, requests

st.set_page_config(
    page_title="RIPPLEPOINT - Global Macro Intelligence",
    page_icon="📡",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #0d1117; }
h1,h2,h3 { color: #e6edf3 !important; }
.stMetric label { color: #8b949e !important; }
.stDataFrame { background-color: #161b22; }
div[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    with open("dashboard_data.json") as f:
        return json.load(f)

try:
    data    = load_data()
    current = data["current"]
    chart1  = data["chart1_gcpi_trend"]
    chart2  = data["chart2_grci_trend"]
    chart3  = data["chart3_radar"]
    chart4  = data["chart4_heatmap"]
    chart5  = data["chart5_rsdm"]
    chart6  = data["chart6_cci"]
    chart7  = data["chart7_phase"]
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

phase = current.get("phase", 2)
phase_names = {
    1:"Stable Equilibrium",
    2:"Compression Building",
    3:"Volatility Expansion",
    4:"Active Fragility",
    5:"Active Recovery",
    6:"Conflicted Regime"
}
phase_colors = {
    1:"#10b981", 2:"#f59e0b",
    3:"#f97316", 4:"#ef4444",
    5:"#22c55e", 6:"#8b5cf6"
}
pcolor = phase_colors.get(phase, "#f59e0b")

# HEADER
st.markdown(
    "<h1 style='text-align:center;color:#58a6ff;"
    "font-size:2.2rem;margin-bottom:0'>"
    "📡 RIPPLEPOINT</h1>",
    unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#8b949e'>"
    "Global Macro Intelligence Architecture"
    " | India Lens | Ripple Axis Systems</p>",
    unsafe_allow_html=True)

# PHASE BANNER
st.markdown(
    f"<div style='background:{pcolor}22;"
    f"border:2px solid {pcolor};"
    f"border-radius:10px;padding:16px;"
    f"text-align:center;margin:10px 0'>"
    f"<h2 style='color:{pcolor};margin:0'>"
    f"PHASE {phase} — "
    f"{phase_names.get(phase,'')}</h2>"
    f"<p style='color:#e6edf3;margin:4px 0'>"
    f"{current.get('active_rule','STANDARD MONITORING')}"
    f"</p></div>",
    unsafe_allow_html=True)

# ENGINE SCORES
st.subheader("Engine Scores")
m1,m2,m3,m4,m5,m6 = st.columns(6)
gcpi = current.get("gcpi", 0)
with m1:
    st.metric("GCPI", f"{gcpi:.1f}",
        "🔴 RED"    if gcpi >= 70 else
        "🟠 ORANGE" if gcpi >= 50 else
        "🟡 YELLOW" if gcpi >= 30 else
        "🟢 GREEN")
with m2:
    st.metric("Eff GCPI",
        f"{current.get('effective_gcpi',0):.1f}")
with m3:
    grci = current.get("grci", 0)
    st.metric("GRCI", f"{grci:.3f}",
        "🟢 Recovery" if grci >= 0.80
        else "🔴 Stable")
with m4:
    st.metric("CCI",
        f"{current.get('cci',0):.3f}",
        str(current.get(
            'cci_direction',''))[:10])
with m5:
    alpha = current.get("alpha", 0)
    st.metric("Alpha",
        f"{alpha:.3f}",
        "Coherent" if alpha >= 0.80
        else "Converging" if alpha >= 0.65
        else "Divergent")
with m6:
    rbi = current.get("rbi_room", 0)
    st.metric("RBI Room",
        f"{rbi:.1f}/10",
        "🔴 Constrained" if rbi <= 2
        else "✅ Available")

st.markdown("---")

# AI NARRATIVE FRAME
st.subheader("📋 RIPPLEPOINT Intelligence — Live Interpretation")

ANTHROPIC_API_KEY = os.environ.get(
    "ANTHROPIC_API_KEY", "")

def get_ai_narrative(data, key):
    if not key or key == "":
        return None
    try:
        prompt = f"""You are RIPPLEPOINT, a Global Macro Intelligence system with an India Lens.

Current readings as of {data.get('generated', 'today')}:
- Phase: {phase} — {phase_names.get(phase,'')}
- Active Rule: {current.get('active_rule','')}
- GCPI: {current.get('gcpi',0):.1f} ({
    'RED' if current.get('gcpi',0) >= 70 else
    'ORANGE' if current.get('gcpi',0) >= 50 else
    'YELLOW' if current.get('gcpi',0) >= 30 else 'GREEN'
})
- Effective GCPI: {current.get('effective_gcpi',0):.1f}
- GRCI: {current.get('grci',0):.3f} (recovery signals)
- CCI Direction: {current.get('cci_direction','')}
- Cronbach Alpha: {current.get('alpha',0):.3f}
- RBI Policy Room: {current.get('rbi_room',0):.1f}/10
- NIFTY 50: {current.get('nifty','N/A')}
- S&P 500: {current.get('sp500','N/A')}
- DXY: {current.get('dxy','N/A')}
- Brent Crude: {current.get('brent','N/A')}
- VIX: {current.get('vix','N/A')}
- India VIX: {current.get('india_vix','N/A')}
- USD/INR: {current.get('usdinr','N/A')}
- Oversold count: {current.get('oversold_count',0)} indices

Generate a diagnostic Net Regime Statement of exactly 3 sentences.
Use institutional tone. No investment advice. No buy/sell signals.
Reference specific numbers. End with the key surveillance trigger."""

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 300,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            },
            timeout=15
        )
        if response.status_code == 200:
            return response.json()[
                "content"][0]["text"]
        return None
    except:
        return None

narrative = get_ai_narrative(
    data, ANTHROPIC_API_KEY)

if narrative:
    st.markdown(
        f"<div style='background:#1c2d5a;"
        f"border-left:4px solid #388bfd;"
        f"border-radius:8px;padding:16px;"
        f"margin:10px 0'>"
        f"<p style='color:#e6edf3;"
        f"font-style:italic;font-size:1rem;"
        f"line-height:1.6;margin:0'>"
        f"{narrative}</p>"
        f"<p style='color:#8b949e;"
        f"font-size:0.75rem;margin:8px 0 0'>"
        f"Generated by Claude | "
        f"{data.get('generated','')} | "
        f"Diagnostic research only — "
        f"Not investment advice</p>"
        f"</div>",
        unsafe_allow_html=True)
else:
    st.info(
        "AI narrative requires ANTHROPIC_API_KEY "
        "environment variable to be set in Render.")

st.markdown("---")

# CHARTS ROW 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 GCPI Daily Trend")
    dates     = chart1.get("dates",    [])
    gcpi_vals = chart1.get("gcpi",     [])
    eff_vals  = chart1.get("eff_gcpi", [])
    fig1 = go.Figure()
    for zone,color,y0,y1 in [
        ("GREEN",  "rgba(16,185,129,0.08)",  0, 30),
        ("YELLOW", "rgba(245,158,11,0.08)",  30,50),
        ("ORANGE", "rgba(249,115,22,0.08)",  50,70),
        ("RED",    "rgba(239,68,68,0.08)",   70,100),
    ]:
        fig1.add_hrect(
            y0=y0, y1=y1,
            fillcolor=color, line_width=0,
            annotation_text=zone,
            annotation_position="right",
            annotation_font_color="#8b949e",
            annotation_font_size=10)
    fig1.add_trace(go.Scatter(
        x=dates, y=gcpi_vals,
        name="GCPI",
        line=dict(color="#388bfd", width=2.5)))
    fig1.add_trace(go.Scatter(
        x=dates, y=eff_vals,
        name="Effective GCPI",
        line=dict(color="#f85149",
            width=1.5, dash="dot")))
    fig1.update_layout(
        height=300,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d",
            color="#8b949e"),
        yaxis=dict(gridcolor="#21262d",
            color="#8b949e", range=[0,100]),
        margin=dict(l=40,r=80,t=20,b=40),
        hovermode="x unified",
        legend=dict(bgcolor="#161b22"))
    st.plotly_chart(fig1,
        use_container_width=True)

with col2:
    st.subheader("🔄 GRCI Recovery Trend")
    grci_dates = chart2.get("dates", [])
    grci_vals  = chart2.get("grci",  [])
    fig2 = go.Figure()
    for zone,color,y0,y1 in [
        ("STABLE",    "rgba(239,68,68,0.08)",  0,   0.40),
        ("WATCH",     "rgba(249,115,22,0.08)", 0.40,0.60),
        ("BUILDING",  "rgba(245,158,11,0.08)", 0.60,0.80),
        ("CONFIRMED", "rgba(16,185,129,0.08)", 0.80,1.00),
    ]:
        fig2.add_hrect(
            y0=y0, y1=y1,
            fillcolor=color, line_width=0,
            annotation_text=zone,
            annotation_position="right",
            annotation_font_color="#8b949e",
            annotation_font_size=10)
    fig2.add_trace(go.Scatter(
        x=grci_dates, y=grci_vals,
        name="GRCI",
        line=dict(color="#3fb950", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(63,185,80,0.1)"))
    fig2.add_hline(
        y=0.80, line_dash="dash",
        line_color="#f59e0b",
        annotation_text="Confirmation threshold",
        annotation_font_color="#f59e0b",
        annotation_font_size=10)
    fig2.update_layout(
        height=300,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d",
            color="#8b949e"),
        yaxis=dict(gridcolor="#21262d",
            color="#8b949e", range=[0,1]),
        margin=dict(l=40,r=80,t=20,b=40),
        hovermode="x unified")
    st.plotly_chart(fig2,
        use_container_width=True)

st.markdown("---")

# CHARTS ROW 2
col3, col4 = st.columns(2)

with col3:
    st.subheader("🕸️ GCPI Six Dimensions")
    dims   = chart3.get("dimensions", [])
    scores = chart3.get("scores",     [])
    alpha_v= chart3.get("alpha",      0)
    fig3   = go.Figure()
    fig3.add_trace(go.Scatterpolar(
        r=scores+[scores[0]],
        theta=dims+[dims[0]],
        fill="toself",
        fillcolor="rgba(56,139,253,0.2)",
        line=dict(color="#388bfd", width=2),
        name="Today"))
    fig3.add_trace(go.Scatterpolar(
        r=[0.80]*(len(dims)+1),
        theta=dims+[dims[0]],
        line=dict(color="#ef4444",
            width=1, dash="dash"),
        name="Alert (0.80)",
        hoverinfo="skip"))
    fig3.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(
                visible=True, range=[0,1],
                gridcolor="#30363d",
                color="#8b949e"),
            angularaxis=dict(
                gridcolor="#30363d",
                color="#8b949e")),
        paper_bgcolor="#161b22",
        font_color="#e6edf3",
        height=320,
        margin=dict(l=40,r=40,t=20,b=20),
        annotations=[dict(
            text=f"a={alpha_v:.3f}",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14,
                color="#f59e0b"))])
    st.plotly_chart(fig3,
        use_container_width=True)

with col4:
    st.subheader("🌍 Global Stretch Heatmap")
    tickers  = chart4.get("tickers",  [])
    z_scores = chart4.get("z_scores", [])

    # FIXED SIGNAL LOGIC
    def get_signal(z):
        if   z <= -2.0:
            return "⬇ Stat. Stretched Down"
        elif z <= -1.0:
            return "↘ Below Mean"
        elif z >=  2.0:
            return "⬆ Stat. Stretched Up"
        elif z >=  1.0:
            return "↗ Above Mean"
        else:
            return "➡ Near Mean"

    colors = []
    for z in z_scores:
        if   z <= -2.0: colors.append("#ef4444")
        elif z <= -1.0: colors.append("#f97316")
        elif z <   0.0: colors.append("#f59e0b")
        elif z <   1.0: colors.append("#10b981")
        elif z <   2.0: colors.append("#3b82f6")
        else:           colors.append("#8b5cf6")

    fig4 = go.Figure(go.Bar(
        x=z_scores, y=tickers,
        orientation="h",
        marker_color=colors,
        hovertemplate=(
            "%{y}: Z=%{x:.2f}"
            "<extra></extra>")))
    fig4.add_vline(
        x=-2.0, line_dash="dash",
        line_color="#ef4444",
        annotation_text="Stat. Stretched Down",
        annotation_font_color="#ef4444",
        annotation_font_size=10)
    fig4.add_vline(
        x=2.0, line_dash="dash",
        line_color="#8b5cf6",
        annotation_text="Stat. Stretched Up",
        annotation_font_color="#8b5cf6",
        annotation_font_size=10)
    fig4.add_vline(
        x=0, line_color="#30363d")
    fig4.update_layout(
        height=320,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d",
            color="#8b949e",
            title="Z-Score (20D)"),
        yaxis=dict(gridcolor="#21262d",
            color="#8b949e"),
        margin=dict(l=20,r=80,t=20,b=40),
        showlegend=False)
    st.plotly_chart(fig4,
        use_container_width=True)

st.markdown("---")

# CHARTS ROW 3
col5, col6 = st.columns(2)

with col5:
    st.subheader("⚖️ RSDM Key Pairs")
    pairs = chart5.get("pairs", {})
    if pairs:
        selected = st.selectbox(
            "Select pair:",
            list(pairs.keys()),
            format_func=lambda x:
                x.replace("__"," / "))
        if selected in pairs:
            pd_data = pairs[selected]
            dates_p = pd_data.get("dates", [])
            ir_vals = pd_data.get("ir",    [])
            z_vals  = pd_data.get("z20",   [])
            fig5 = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                row_heights=[0.65,0.35],
                vertical_spacing=0.08)
            fig5.add_trace(go.Scatter(
                x=dates_p, y=ir_vals,
                name="Indexed Ratio",
                line=dict(color="#388bfd",
                    width=2)),
                row=1, col=1)
            fig5.add_hline(
                y=100,
                line_dash="dash",
                line_color="#30363d",
                row=1, col=1)
            fig5.add_trace(go.Bar(
                x=dates_p, y=z_vals,
                name="Z-Score 20D",
                marker_color=[
                    "#ef4444" if z < -2 else
                    "#f59e0b" if z <  0 else
                    "#10b981"
                    for z in z_vals]),
                row=2, col=1)
            fig5.update_layout(
                height=320,
                paper_bgcolor="#161b22",
                plot_bgcolor="#0d1117",
                font_color="#e6edf3",
                margin=dict(
                    l=40,r=20,t=10,b=20),
                showlegend=False,
                xaxis2=dict(
                    gridcolor="#21262d",
                    color="#8b949e"),
                yaxis=dict(
                    gridcolor="#21262d",
                    color="#8b949e",
                    title="Indexed Ratio"),
                yaxis2=dict(
                    gridcolor="#21262d",
                    color="#8b949e",
                    title="Z-Score"))
            st.plotly_chart(fig5,
                use_container_width=True)

with col6:
    st.subheader("🛢️ CCI Commodity Snapshot")
    segments  = chart6.get("segments",      {})
    cci_score = chart6.get("cci_score",     0)
    cci_dir   = chart6.get("cci_direction", "MIXED")
    rbi_room6 = chart6.get("rbi_room",      5)
    if segments:
        tickers_c = list(segments.keys())
        z_vals_c  = [
            segments[t].get("z20", 0) or 0
            for t in tickers_c]
        colors_c  = [
            "#ef4444" if z >  1.5 else
            "#f59e0b" if z >  0.5 else
            "#10b981" if z < -0.5 else
            "#8b949e"
            for z in z_vals_c]
        fig6 = go.Figure(go.Bar(
            x=tickers_c, y=z_vals_c,
            marker_color=colors_c,
            hovertemplate=(
                "%{x}: Z=%{y:.2f}"
                "<extra></extra>")))
        fig6.add_hline(
            y=0, line_color="#30363d")
        fig6.add_hline(
            y=1.5, line_dash="dash",
            line_color="#ef4444",
            annotation_text="Stress",
            annotation_font_size=10,
            annotation_font_color="#ef4444")
        fig6.update_layout(
            height=220,
            paper_bgcolor="#161b22",
            plot_bgcolor="#0d1117",
            font_color="#e6edf3",
            xaxis=dict(gridcolor="#21262d",
                color="#8b949e"),
            yaxis=dict(gridcolor="#21262d",
                color="#8b949e",
                title="Z-Score (20D)"),
            margin=dict(
                l=20,r=20,t=10,b=20),
            showlegend=False)
        st.plotly_chart(fig6,
            use_container_width=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        st.metric("CCI Score",
            f"{cci_score:.3f}")
    with c2:
        st.metric("Direction",
            cci_dir[:12])
    with c3:
        st.metric("RBI Room",
            f"{rbi_room6:.1f}/10")

st.markdown("---")

# PHASE TIMELINE
st.subheader("📅 Phase History Timeline")
dates_ph  = chart7.get("dates",  [])
phases_ph = chart7.get("phases", [])
p_colors  = chart7.get("phase_colors", {})
p_names   = chart7.get("phase_names",  {})

if dates_ph and phases_ph:
    color_list = [
        p_colors.get(str(p),
        p_colors.get(p, "#f59e0b"))
        for p in phases_ph]
    fig7 = go.Figure(go.Bar(
        x=dates_ph,
        y=[1]*len(dates_ph),
        marker_color=color_list,
        hovertemplate=[
            f"%{{x}}<br>Phase {p}: "
            f"{p_names.get(str(p), p_names.get(p,''))}"
            f"<extra></extra>"
            for p in phases_ph],
        showlegend=False))
    for p_num, p_name in p_names.items():
        color = p_colors.get(
            str(p_num),
            p_colors.get(p_num, "#f59e0b"))
        fig7.add_trace(go.Bar(
            x=[None], y=[None],
            marker_color=color,
            name=f"Ph{p_num}: {p_name}",
            showlegend=True))
    fig7.update_layout(
        height=150,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        xaxis=dict(gridcolor="#21262d",
            color="#8b949e"),
        yaxis=dict(visible=False,
            range=[0,1.2]),
        legend=dict(bgcolor="#161b22",
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=10)),
        margin=dict(
            l=20,r=20,t=40,b=20),
        barmode="overlay", bargap=0)
    st.plotly_chart(fig7,
        use_container_width=True)

st.markdown("---")

# MARKET SNAPSHOT - FIXED SIGNALS
st.subheader("📊 Market Snapshot")

tickers_snap = [
    "NIFTY 50","S&P 500","DXY",
    "Brent","VIX","India VIX","USD/INR"]
prices_snap  = [
    current.get("nifty"),
    current.get("sp500"),
    current.get("dxy"),
    current.get("brent"),
    current.get("vix"),
    current.get("india_vix"),
    current.get("usdinr")]

# Z-scores from current data
nifty_z  = current.get("nifty_z20",  0) or 0
sp_z     = current.get("sp500_z20",  0) or 0
dxy_z    = current.get("dxy_z20",    0) or 0

signals_snap = [
    get_signal(nifty_z),
    get_signal(sp_z),
    get_signal(dxy_z),
    "⚠ Elevated"    if (current.get("brent") or 0) > 90
    else "➡ Normal",
    "⚠ Elevated"    if (current.get("vix")   or 0) > 20
    else "✅ Normal",
    "⚠ Elevated"    if (current.get("india_vix") or 0) > 18
    else "✅ Normal",
    "⚠ Pressure"    if (current.get("usdinr") or 0) > 84
    else "✅ Normal",
]

df_snap = pd.DataFrame({
    "Market":  tickers_snap,
    "Price":   prices_snap,
    "Z-Score": [
        f"{nifty_z:+.2f}",
        f"{sp_z:+.2f}",
        f"{dxy_z:+.2f}",
        "N/A", "N/A", "N/A", "N/A"],
    "Signal":  signals_snap
})

st.dataframe(
    df_snap,
    use_container_width=True,
    hide_index=True)

st.markdown("---")
st.markdown(
    "<p style='text-align:center;"
    "color:#8b949e;font-size:0.75rem'>"
    "RIPPLEPOINT | Ripple Axis Systems | "
    "India Lens | "
    f"Updated: {data.get('generated','')} | "
    "Diagnostic Research Only | "
    "Not Investment Advice | "
    "Not SEBI Registered"
    "</p>",
    unsafe_allow_html=True)
