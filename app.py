
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import os

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="RIPPLEPOINT — Global Macro Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0d1117; color: #e6edf3; }
    .stApp { background-color: #0d1117; }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .phase-banner {
        background: #1c2d5a;
        border: 2px solid #388bfd;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #e6edf3 !important; }
    .stMetric label { color: #8b949e !important; }
    .stMetric value { color: #e6edf3 !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ───────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    json_path = os.environ.get(
        "RIPPLEPOINT_DATA",
        "dashboard_data.json"
    )
    with open(json_path, "r") as f:
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

# ── Helper: Phase info ─────────────────────────────────────
phase_names = {
    1:"Stable Equilibrium",    2:"Compression Building",
    3:"Volatility Expansion",  4:"Active Fragility",
    5:"Active Recovery",       6:"Conflicted Regime"
}
phase_colors = {
    1:"#10b981", 2:"#f59e0b", 3:"#f97316",
    4:"#ef4444", 5:"#22c55e", 6:"#8b5cf6"
}
phase = current.get("phase", 2)
pcolor = phase_colors.get(phase, "#f59e0b")

# ── HEADER ──────────────────────────────────────────────────
col_l, col_m, col_r = st.columns([1, 3, 1])
with col_m:
    st.markdown(
        "<h1 style='text-align:center; color:#58a6ff; "
        "font-size:2.5rem; margin-bottom:0'>📡 RIPPLEPOINT</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:#8b949e; "
        "font-size:1rem'>Global Macro Intelligence Architecture"
        " | India Lens</p>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ── PHASE BANNER ────────────────────────────────────────────
st.markdown(
    f"<div style='background:{pcolor}22; "
    f"border:2px solid {pcolor}; border-radius:10px; "
    f"padding:16px; text-align:center; margin-bottom:16px'>"
    f"<h2 style='color:{pcolor}; margin:0'>"
    f"PHASE {phase} — {phase_names.get(phase,'')}</h2>"
    f"<p style='color:#e6edf3; margin:4px 0'>"
    f"{current.get('active_rule','STANDARD MONITORING')}"
    f"</p></div>",
    unsafe_allow_html=True
)

# ── ENGINE SCORE METRICS ────────────────────────────────────
st.subheader("Engine Scores")
m1, m2, m3, m4, m5, m6 = st.columns(6)

gcpi = current.get("gcpi", 0)
gcpi_color = (
    "🔴" if gcpi >= 70 else
    "🟠" if gcpi >= 50 else
    "🟡" if gcpi >= 30 else "🟢"
)

with m1:
    st.metric(
        "GCPI",
        f"{gcpi:.1f}",
        f"{gcpi_color}"
    )
with m2:
    st.metric(
        "Eff GCPI",
        f"{current.get('effective_gcpi', 0):.1f}",
        ""
    )
with m3:
    grci = current.get("grci", 0)
    st.metric(
        "GRCI",
        f"{grci:.3f}",
        "🟢" if grci >= 0.80 else "🔴"
    )
with m4:
    st.metric(
        "CCI",
        f"{current.get('cci', 0):.3f}",
        current.get("cci_direction", "")[:10]
    )
with m5:
    st.metric(
        "Alpha (α)",
        f"{current.get('alpha', 0):.3f}",
        ""
    )
with m6:
    rbi = current.get("rbi_room", 0)
    st.metric(
        "RBI Room",
        f"{rbi:.1f}/10",
        "🔴 Constrained" if rbi <= 2 else "✅ Available"
    )

st.markdown("---")

# ── ROW 1: GCPI TREND + GRCI TREND ─────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 GCPI Daily Trend")
    dates = chart1.get("dates", [])
    gcpi_vals = chart1.get("gcpi", [])
    eff_vals  = chart1.get("eff_gcpi", [])

    fig1 = go.Figure()

    # Zone bands
    for zone, color, y0, y1 in [
        ("GREEN",  "rgba(16,185,129,0.08)",  0,  30),
        ("YELLOW", "rgba(245,158,11,0.08)",  30, 50),
        ("ORANGE", "rgba(249,115,22,0.08)",  50, 70),
        ("RED",    "rgba(239,68,68,0.08)",   70, 100),
    ]:
        fig1.add_hrect(
            y0=y0, y1=y1,
            fillcolor=color,
            line_width=0,
            annotation_text=zone,
            annotation_position="right",
            annotation_font_color="#8b949e",
            annotation_font_size=10,
        )

    fig1.add_trace(go.Scatter(
        x=dates, y=gcpi_vals,
        name="GCPI",
        line=dict(color="#388bfd", width=2.5),
        hovertemplate="%{x}<br>GCPI: %{y:.1f}<extra></extra>"
    ))
    fig1.add_trace(go.Scatter(
        x=dates, y=eff_vals,
        name="Effective GCPI",
        line=dict(color="#f85149", width=1.5,
                  dash="dot"),
        hovertemplate="%{x}<br>Eff GCPI: %{y:.1f}<extra></extra>"
    ))

    fig1.update_layout(
        height=300,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        legend=dict(
            bgcolor="#161b22",
            font_color="#e6edf3"
        ),
        xaxis=dict(
            gridcolor="#21262d",
            color="#8b949e"
        ),
        yaxis=dict(
            gridcolor="#21262d",
            color="#8b949e",
            range=[0, 100]
        ),
        margin=dict(l=40, r=40, t=20, b=40),
        hovermode="x unified"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🔄 GRCI Recovery Trend")
    grci_dates = chart2.get("dates", [])
    grci_vals  = chart2.get("grci", [])

    fig2 = go.Figure()

    # Zone bands
    for zone, color, y0, y1 in [
        ("STABLE",    "rgba(239,68,68,0.08)",    0,    0.40),
        ("WATCH",     "rgba(249,115,22,0.08)",   0.40, 0.60),
        ("BUILDING",  "rgba(245,158,11,0.08)",   0.60, 0.80),
        ("CONFIRMED", "rgba(16,185,129,0.08)",   0.80, 1.00),
    ]:
        fig2.add_hrect(
            y0=y0, y1=y1,
            fillcolor=color,
            line_width=0,
            annotation_text=zone,
            annotation_position="right",
            annotation_font_color="#8b949e",
            annotation_font_size=10,
        )

    fig2.add_trace(go.Scatter(
        x=grci_dates, y=grci_vals,
        name="GRCI",
        line=dict(color="#3fb950", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(63,185,80,0.1)",
        hovertemplate="%{x}<br>GRCI: %{y:.4f}<extra></extra>"
    ))

    # Confirmation threshold line
    fig2.add_hline(
        y=0.80,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text="Confirmation threshold",
        annotation_font_color="#f59e0b",
        annotation_font_size=10,
    )

    fig2.update_layout(
        height=300,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        legend=dict(bgcolor="#161b22"),
        xaxis=dict(gridcolor="#21262d", color="#8b949e"),
        yaxis=dict(
            gridcolor="#21262d",
            color="#8b949e",
            range=[0, 1]
        ),
        margin=dict(l=40, r=40, t=20, b=40),
        hovermode="x unified"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── ROW 2: RADAR + HEATMAP ──────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🕸️ GCPI Six Dimensions")
    dims   = chart3.get("dimensions", [])
    scores = chart3.get("scores", [])

    fig3 = go.Figure()
    fig3.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=dims + [dims[0]],
        fill="toself",
        fillcolor="rgba(56,139,253,0.2)",
        line=dict(color="#388bfd", width=2),
        name="Today",
        hovertemplate="%{theta}: %{r:.4f}<extra></extra>"
    ))

    # Alert threshold ring
    fig3.add_trace(go.Scatterpolar(
        r=[0.80] * (len(dims) + 1),
        theta=dims + [dims[0]],
        line=dict(color="#ef4444", width=1,
                  dash="dash"),
        name="Alert (0.80)",
        hoverinfo="skip"
    ))

    fig3.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor="#30363d",
                color="#8b949e",
                tickfont_color="#8b949e"
            ),
            angularaxis=dict(
                gridcolor="#30363d",
                color="#8b949e"
            )
        ),
        paper_bgcolor="#161b22",
        font_color="#e6edf3",
        height=320,
        legend=dict(bgcolor="#161b22"),
        margin=dict(l=40, r=40, t=20, b=20),
        annotations=[dict(
            text=f"α={chart3.get('alpha', 0):.3f}",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#f59e0b")
        )]
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🌍 Global Stretch Heatmap")
    tickers  = chart4.get("tickers", [])
    z_scores = chart4.get("z_scores", [])

    colors = []
    for z in z_scores:
        if   z < -2.0: colors.append("#ef4444")
        elif z < -1.0: colors.append("#f97316")
        elif z <  0.0: colors.append("#f59e0b")
        elif z <  1.0: colors.append("#10b981")
        elif z <  2.0: colors.append("#3b82f6")
        else:          colors.append("#8b5cf6")

    fig4 = go.Figure(go.Bar(
        x=z_scores,
        y=tickers,
        orientation="h",
        marker_color=colors,
        hovertemplate="%{y}: Z=%{x:.2f}<extra></extra>"
    ))

    fig4.add_vline(
        x=-2.0, line_dash="dash",
        line_color="#ef4444",
        annotation_text="Oversold",
        annotation_font_color="#ef4444",
        annotation_font_size=10
    )
    fig4.add_vline(
        x=2.0, line_dash="dash",
        line_color="#8b5cf6",
        annotation_text="Overbought",
        annotation_font_color="#8b5cf6",
        annotation_font_size=10
    )
    fig4.add_vline(x=0, line_color="#30363d")

    fig4.update_layout(
        height=320,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        xaxis=dict(
            gridcolor="#21262d",
            color="#8b949e",
            title="Z-Score (20D)"
        ),
        yaxis=dict(
            gridcolor="#21262d",
            color="#8b949e"
        ),
        margin=dict(l=20, r=60, t=20, b=40),
        showlegend=False
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── ROW 3: RSDM PAIRS + CCI ────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("⚖️ RSDM Key Pairs")

    pairs = chart5.get("pairs", {})
    if pairs:
        pair_options = list(pairs.keys())
        selected = st.selectbox(
            "Select pair:",
            pair_options,
            format_func=lambda x: x.replace("__", " / ")
        )

        if selected in pairs:
            pair_data = pairs[selected]
            dates_p   = pair_data.get("dates", [])
            ir_vals   = pair_data.get("ir", [])
            z_vals    = pair_data.get("z20", [])

            fig5 = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                row_heights=[0.65, 0.35],
                vertical_spacing=0.08
            )

            fig5.add_trace(
                go.Scatter(
                    x=dates_p, y=ir_vals,
                    name="Indexed Ratio (Base 100)",
                    line=dict(color="#388bfd", width=2),
                    hovertemplate=(
                        "%{x}<br>IR: %{y:.1f}<extra></extra>")
                ), row=1, col=1
            )
            fig5.add_hline(
                y=100,
                line_dash="dash",
                line_color="#30363d",
                row=1, col=1
            )

            fig5.add_trace(
                go.Bar(
                    x=dates_p, y=z_vals,
                    name="Z-Score 20D",
                    marker_color=[
                        "#ef4444" if z < -2 else
                        "#f59e0b" if z < 0  else
                        "#10b981"
                        for z in z_vals
                    ],
                    hovertemplate=(
                        "%{x}<br>Z: %{y:.2f}<extra></extra>")
                ), row=2, col=1
            )

            fig5.update_layout(
                height=320,
                paper_bgcolor="#161b22",
                plot_bgcolor="#0d1117",
                font_color="#e6edf3",
                legend=dict(bgcolor="#161b22"),
                xaxis2=dict(
                    gridcolor="#21262d",
                    color="#8b949e"
                ),
                yaxis=dict(
                    gridcolor="#21262d",
                    color="#8b949e",
                    title="Indexed Ratio"
                ),
                yaxis2=dict(
                    gridcolor="#21262d",
                    color="#8b949e",
                    title="Z-Score"
                ),
                margin=dict(l=40, r=20, t=10, b=20),
                showlegend=False
            )
            st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("RSDM pair data building...")

with col6:
    st.subheader("🛢️ CCI Commodity Snapshot")

    segments  = chart6.get("segments", {})
    cci_score = chart6.get("cci_score", 0)
    cci_dir   = chart6.get("cci_direction", "MIXED")
    rbi_room6 = chart6.get("rbi_room", 5)

    if segments:
        tickers_c = list(segments.keys())
        z_vals_c  = [
            segments[t].get("z20", 0) or 0
            for t in tickers_c
        ]
        prices_c  = [
            segments[t].get("price", 0) or 0
            for t in tickers_c
        ]

        colors_c = [
            "#ef4444" if z > 1.5 else
            "#f59e0b" if z > 0.5 else
            "#10b981" if z < -0.5 else
            "#8b949e"
            for z in z_vals_c
        ]

        fig6 = go.Figure(go.Bar(
            x=tickers_c,
            y=z_vals_c,
            marker_color=colors_c,
            hovertemplate=(
                "%{x}<br>Z-Score: %{y:.2f}<extra></extra>")
        ))
        fig6.add_hline(y=0, line_color="#30363d")
        fig6.add_hline(
            y=1.5, line_dash="dash",
            line_color="#ef4444",
            annotation_text="Stress",
            annotation_font_size=10,
            annotation_font_color="#ef4444"
        )

        fig6.update_layout(
            height=220,
            paper_bgcolor="#161b22",
            plot_bgcolor="#0d1117",
            font_color="#e6edf3",
            xaxis=dict(
                gridcolor="#21262d",
                color="#8b949e"
            ),
            yaxis=dict(
                gridcolor="#21262d",
                color="#8b949e",
                title="Z-Score (20D)"
            ),
            margin=dict(l=20, r=20, t=10, b=20),
            showlegend=False
        )
        st.plotly_chart(fig6, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("CCI Score",
                  f"{cci_score:.3f}", cci_dir[:8])
    with c2:
        st.metric("Direction", cci_dir[:12])
    with c3:
        st.metric("RBI Room",
                  f"{rbi_room6:.1f}/10",
                  "🔴" if rbi_room6 <= 2 else "✅")

st.markdown("---")

# ── ROW 4: PHASE TIMELINE ──────────────────────────────────
st.subheader("📅 Phase History Timeline")

dates_ph  = chart7.get("dates", [])
phases_ph = chart7.get("phases", [])
p_colors  = chart7.get("phase_colors", {})
p_names   = chart7.get("phase_names", {})

if dates_ph and phases_ph:
    color_list = [
        p_colors.get(str(p),
        p_colors.get(p, "#f59e0b"))
        for p in phases_ph
    ]

    fig7 = go.Figure(go.Bar(
        x=dates_ph,
        y=[1] * len(dates_ph),
        marker_color=color_list,
        hovertemplate=[
            f"%{{x}}<br>Phase {p}: "
            f"{p_names.get(str(p), p_names.get(p,''))}"
            f"<extra></extra>"
            for p in phases_ph
        ],
        showlegend=False
    ))

    # Add phase legend
    for p_num, p_name in p_names.items():
        color = p_colors.get(
            str(p_num),
            p_colors.get(p_num, "#f59e0b")
        )
        fig7.add_trace(go.Bar(
            x=[None], y=[None],
            marker_color=color,
            name=f"Ph{p_num}: {p_name}",
            showlegend=True
        ))

    fig7.update_layout(
        height=150,
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        font_color="#e6edf3",
        xaxis=dict(
            gridcolor="#21262d",
            color="#8b949e"
        ),
        yaxis=dict(
            visible=False,
            range=[0, 1.2]
        ),
        legend=dict(
            bgcolor="#161b22",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        barmode="overlay",
        bargap=0
    )
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# ── MARKET SNAPSHOT TABLE ──────────────────────────────────
st.subheader("📊 Market Snapshot")

snap_data = {
    "Market":   ["NIFTY 50","S&P 500","DXY",
                 "Brent","VIX","India VIX","USD/INR"],
    "Price":    [
        current.get("nifty"),
        current.get("sp500"),
        current.get("dxy"),
        current.get("brent"),
        current.get("vix"),
        current.get("india_vix"),
        current.get("usdinr"),
    ],
    "Signal":   [
        "⬇️ Oversold"   if current.get("nifty_z20",0) < -2
        else "➡️ Normal",
        "⬇️ Oversold"   if current.get("sp500_z20",0) < -2
        else "➡️ Normal",
        "⬆️ Overbought" if current.get("dxy_z20",0)  >  2
        else "➡️ Normal",
        "⬆️ Elevated"   if (current.get("brent") or 0) > 90
        else "➡️ Normal",
        "⚠️ Elevated"   if (current.get("vix") or 0)  > 20
        else "✅ Normal",
        "⚠️ Elevated"   if (current.get("india_vix") or 0) > 18
        else "✅ Normal",
        "⚠️ Pressure"   if current.get("usdinr_z20",0) > 1.5
        else "✅ Normal",
    ]
}

df_snap = pd.DataFrame(snap_data)
st.dataframe(
    df_snap,
    use_container_width=True,
    hide_index=True
)

# ── FOOTER ─────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:#8b949e; "
    f"font-size:0.8rem'>"
    f"RIPPLEPOINT | Ripple Axis Systems | "
    f"India Lens | Updated: {data.get('generated','')} | "
    f"Proprietary & Confidential | Not Investment Advice"
    f"</p>",
    unsafe_allow_html=True
)
