import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from supabase import create_client
import os

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Verdant Innovations — Smart Grid Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styling ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1F4E2C 0%, #2d6e3e 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #70AD47;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #70AD47;
        margin: 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #a8d08d;
        margin: 4px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .header-bar {
        background: linear-gradient(90deg, #1F4E2C 0%, #2d6e3e 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 24px;
        border-left: 6px solid #70AD47;
    }
    .status-live {
        display: inline-block;
        background: #70AD47;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .section-header {
        color: #70AD47;
        font-size: 1.1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #1F4E2C;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ── Config ─────────────────────────────────────────────────────────────────
FORECAST_API = "https://api.verdant.evervia.co.uk"
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# ── Data functions ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_forecast():
    try:
        r = requests.get(f"{FORECAST_API}/forecast?hours=48", timeout=60)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def fetch_historical():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("elexon_demand") \
            .select("start_time, transmission_system_demand, national_demand") \
            .order("start_time", desc=True) \
            .limit(192) \
            .execute()
        df = pd.DataFrame(response.data)
        df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
        df = df.sort_values("start_time")
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_weather():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("weather_forecast") \
            .select("timestamp, temperature_2m, windspeed_10m, shortwave_radiation") \
            .order("timestamp", desc=True) \
            .limit(48) \
            .execute()
        df = pd.DataFrame(response.data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp")
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_api_summary():
    try:
        r = requests.get(f"{FORECAST_API}/data/summary", timeout=30)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
    <h1 style="color:white;margin:0;font-size:1.8rem;">
        ⚡ Verdant Innovations
    </h1>
    <p style="color:#a8d08d;margin:4px 0 0 0;font-size:0.95rem;">
        AI-Powered Smart Grid Optimisation Platform &nbsp;
        <span class="status-live">● LIVE</span>
    </p>
    <p style="color:#6b8f5a;margin:6px 0 0 0;font-size:0.8rem;">
        UK National Grid · Real-time Demand Forecasting · Powered by Gradient Boosting ML
    </p>
</div>
""", unsafe_allow_html=True)

# ── Refresh button ─────────────────────────────────────────────────────────
col_refresh, col_time = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_time:
    st.markdown(f"<p style='color:#6b8f5a;padding-top:8px;'>Last updated: {datetime.utcnow().strftime('%d %b %Y %H:%M UTC')}</p>", unsafe_allow_html=True)

st.markdown("---")

# ── Load data ──────────────────────────────────────────────────────────────
with st.spinner("Loading live UK grid data..."):
    forecast_data = fetch_forecast()
    historical_df = fetch_historical()
    weather_df = fetch_weather()
    api_summary = fetch_api_summary()

# ── Summary Cards ──────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 48-Hour Forecast Summary</p>', unsafe_allow_html=True)

if forecast_data and forecast_data.get("status") == "success":
    summary = forecast_data.get("summary", {})
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{summary.get('peak_demand_mw', 'N/A'):,.0f} MW</p>
            <p class="metric-label">⬆ Peak Demand</p>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{summary.get('avg_demand_mw', 'N/A'):,.0f} MW</p>
            <p class="metric-label">≈ Average Demand</p>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{summary.get('min_demand_mw', 'N/A'):,.0f} MW</p>
            <p class="metric-label">⬇ Min Demand</p>
        </div>""", unsafe_allow_html=True)

    with col4:
        peak_ts = summary.get('peak_timestamp', '')
        peak_fmt = pd.to_datetime(peak_ts).strftime('%d %b %H:%M') if peak_ts else 'N/A'
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value" style="font-size:1.4rem;">{peak_fmt}</p>
            <p class="metric-label">🕐 Peak Time</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Forecast Chart ─────────────────────────────────────────────────────
    st.markdown('<p class="section-header">📈 48-Hour Demand Forecast</p>', unsafe_allow_html=True)

    forecast_list = forecast_data.get("forecast", [])
    if forecast_list:
        fc_df = pd.DataFrame(forecast_list)
        fc_df["timestamp"] = pd.to_datetime(fc_df["timestamp"])

        fig = go.Figure()

        # Confidence band
        fig.add_trace(go.Scatter(
            x=pd.concat([fc_df["timestamp"], fc_df["timestamp"].iloc[::-1]]),
            y=pd.concat([fc_df["upper_bound_mw"], fc_df["lower_bound_mw"].iloc[::-1]]),
            fill="toself",
            fillcolor="rgba(112, 173, 71, 0.15)",
            line=dict(color="rgba(255,255,255,0)"),
            name="95% Confidence Interval",
            hoverinfo="skip"
        ))

        # Historical actual
        if not historical_df.empty:
            fig.add_trace(go.Scatter(
                x=historical_df["start_time"],
                y=historical_df["transmission_system_demand"],
                mode="lines",
                line=dict(color="#4A9EFF", width=2),
                name="Historical Actual (MW)",
                hovertemplate="%{x|%d %b %H:%M}<br>Actual: %{y:,.0f} MW<extra></extra>"
            ))

        # Forecast line
        fig.add_trace(go.Scatter(
            x=fc_df["timestamp"],
            y=fc_df["forecast_mw"],
            mode="lines",
            line=dict(color="#70AD47", width=2.5),
            name="AI Forecast (MW)",
            hovertemplate="%{x|%d %b %H:%M}<br>Forecast: %{y:,.0f} MW<extra></extra>"
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            height=420,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"
            ),
            xaxis=dict(
                gridcolor="#1a2e1a", showgrid=True,
                title="Date / Time (UTC)"
            ),
            yaxis=dict(
                gridcolor="#1a2e1a", showgrid=True,
                title="Demand (MW)"
            ),
            hovermode="x unified"
        )

       # Add vertical line for now
        fig.add_shape(
            type="line",
            x0=datetime.utcnow().isoformat(),
            x1=datetime.utcnow().isoformat(),
            y0=0, y1=1,
            yref="paper",
            line=dict(color="#FFD700", width=2, dash="dash")
        )
        fig.add_annotation(
            x=datetime.utcnow().isoformat(),
            y=1, yref="paper",
            text="Now", showarrow=False,
            font=dict(color="#FFD700", size=11),
            yanchor="bottom"
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ Forecast API is warming up — this can take up to 60 seconds on first load. Click Refresh in a moment.")

st.markdown("---")

# ── Historical Data + Weather ──────────────────────────────────────────────
col_hist, col_weather = st.columns([3, 2])

with col_hist:
    st.markdown('<p class="section-header">📡 Live Demand Data (Last 48hrs)</p>', unsafe_allow_html=True)
    if not historical_df.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=historical_df["start_time"],
            y=historical_df["transmission_system_demand"],
            mode="lines", fill="tozeroy",
            fillcolor="rgba(31, 78, 44, 0.3)",
            line=dict(color="#70AD47", width=2),
            name="Transmission System Demand",
            hovertemplate="%{x|%d %b %H:%M}<br>%{y:,.0f} MW<extra></extra>"
        ))
        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis=dict(gridcolor="#1a2e1a"),
            yaxis=dict(gridcolor="#1a2e1a", title="MW")
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Latest reading
        latest = historical_df.iloc[-1]
        st.markdown(f"""
        <div style="background:#1F4E2C;border-radius:8px;padding:12px;border-left:4px solid #70AD47;">
            <span style="color:#a8d08d;font-size:0.8rem;">LATEST READING</span><br>
            <span style="color:white;font-size:1.1rem;font-weight:600;">
                {latest['transmission_system_demand']:,.0f} MW
            </span>
            <span style="color:#6b8f5a;font-size:0.8rem;margin-left:8px;">
                at {pd.to_datetime(latest['start_time']).strftime('%d %b %H:%M UTC')}
            </span>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Loading demand data...")

with col_weather:
    st.markdown('<p class="section-header">🌤 Weather Inputs (London)</p>', unsafe_allow_html=True)
    if not weather_df.empty:
        latest_w = weather_df.iloc[-1]

        w1, w2 = st.columns(2)
        with w1:
            st.metric("🌡 Temperature", f"{latest_w['temperature_2m']:.1f}°C")
            st.metric("💨 Wind Speed", f"{latest_w['windspeed_10m']:.1f} km/h")
        with w2:
            st.metric("☀️ Solar Radiation", f"{latest_w['shortwave_radiation']:.0f} W/m²")

        # Temperature chart
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=weather_df["timestamp"],
            y=weather_df["temperature_2m"],
            mode="lines",
            line=dict(color="#FFD700", width=2),
            fill="tozeroy",
            fillcolor="rgba(255, 215, 0, 0.1)",
            hovertemplate="%{x|%d %b %H:%M}<br>%{y:.1f}°C<extra></extra>"
        ))
        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            height=160,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis=dict(gridcolor="#1a2e1a"),
            yaxis=dict(gridcolor="#1a2e1a", title="°C")
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Loading weather data...")

st.markdown("---")

# ── Data Pipeline Status ───────────────────────────────────────────────────
st.markdown('<p class="section-header">🔧 System Status</p>', unsafe_allow_html=True)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)

if api_summary:
    demand_info = api_summary.get("demand", {})
    weather_info = api_summary.get("weather", {})

    with col_s1:
        status = "✅ Live" if demand_info.get("ready_for_training") else "⚠️ Building"
        st.markdown(f"""
        <div style="background:#111;border-radius:8px;padding:12px;border:1px solid #1F4E2C;">
            <div style="color:#70AD47;font-size:0.75rem;text-transform:uppercase;">Elexon Pipeline</div>
            <div style="color:white;font-size:1.1rem;font-weight:600;">{status}</div>
            <div style="color:#6b8f5a;font-size:0.75rem;">{demand_info.get('rows', 0):,} rows · {demand_info.get('days_covered', 0)} days</div>
        </div>""", unsafe_allow_html=True)

    with col_s2:
        st.markdown(f"""
        <div style="background:#111;border-radius:8px;padding:12px;border:1px solid #1F4E2C;">
            <div style="color:#70AD47;font-size:0.75rem;text-transform:uppercase;">Weather Pipeline</div>
            <div style="color:white;font-size:1.1rem;font-weight:600;">✅ Live</div>
            <div style="color:#6b8f5a;font-size:0.75rem;">{weather_info.get('rows', 0):,} rows</div>
        </div>""", unsafe_allow_html=True)

    with col_s3:
        fc_status = "✅ Live" if forecast_data and forecast_data.get("status") == "success" else "⚠️ Warming up"
        fc_points = forecast_data.get("forecast_points", 0) if forecast_data else 0
        st.markdown(f"""
        <div style="background:#111;border-radius:8px;padding:12px;border:1px solid #1F4E2C;">
            <div style="color:#70AD47;font-size:0.75rem;text-transform:uppercase;">Forecast API</div>
            <div style="color:white;font-size:1.1rem;font-weight:600;">{fc_status}</div>
            <div style="color:#6b8f5a;font-size:0.75rem;">{fc_points} forecast points</div>
        </div>""", unsafe_allow_html=True)

    with col_s4:
        st.markdown(f"""
        <div style="background:#111;border-radius:8px;padding:12px;border:1px solid #1F4E2C;">
            <div style="color:#70AD47;font-size:0.75rem;text-transform:uppercase;">Supabase DB</div>
            <div style="color:white;font-size:1.1rem;font-weight:600;">✅ Connected</div>
            <div style="color:#6b8f5a;font-size:0.75rem;">bvxdfmfjcfjhubtbqqor</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#2d4a2d;font-size:0.75rem;padding:20px 0;">
    Verdant Innovations Ltd. · AI-Powered Smart Grid Optimisation · 
    Data: Elexon BMRS API + Open-Meteo · Model: Gradient Boosting Regressor
</div>
""", unsafe_allow_html=True)
