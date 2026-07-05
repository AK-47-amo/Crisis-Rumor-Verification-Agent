"""
Streamlit UI for the Crisis Rumor Verification Agent.

Entry point of the application. Provides a polished dashboard
for message input, analysis results, and recommendations.

Run with:
    streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go

from config import APP_ICON, APP_SUBTITLE, APP_TITLE
from models import VerificationReport
from pipeline import run_pipeline


# ── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crisis Rumor Verification Agent",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .main-header h1 {
        color: #fff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: rgba(255,255,255,0.65);
        font-size: 1rem;
        margin-top: 0.4rem;
    }

    .metric-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.06);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    .metric-card .label {
        color: rgba(255,255,255,0.5);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.5rem;
    }
    .metric-card .value {
        color: #fff;
        font-size: 1.5rem;
        font-weight: 600;
    }

    .verdict-box {
        padding: 1.8rem;
        border-radius: 14px;
        text-align: center;
        margin: 1.5rem 0;
    }
    .verdict-low {
        background: linear-gradient(135deg, #0a3d0a, #1b5e20);
        border: 1px solid #2e7d32;
    }
    .verdict-medium {
        background: linear-gradient(135deg, #4a3800, #e65100);
        border: 1px solid #ef6c00;
    }
    .verdict-high {
        background: linear-gradient(135deg, #4a0000, #b71c1c);
        border: 1px solid #c62828;
    }
    .verdict-critical {
        background: linear-gradient(135deg, #3e0000, #880e0e);
        border: 2px solid #ff1744;
        animation: pulse-border 2s infinite;
    }
    @keyframes pulse-border {
        0%, 100% { border-color: #ff1744; }
        50% { border-color: #ff5252; }
    }

    .breakdown-item {
        display: flex;
        justify-content: space-between;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .breakdown-item:last-child { border-bottom: none; }

    .disclaimer-box {
        background: rgba(255, 193, 7, 0.08);
        border: 1px solid rgba(255, 193, 7, 0.25);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
    }

    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        background: rgba(255,255,255,0.03) !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <h1>{APP_TITLE}</h1>
    <p>{APP_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 How It Works")
    st.markdown("""
    1. **Enter** a disaster-related message
    2. **LLM** extracts crisis features
    3. **ML Model** classifies real vs. non-crisis
    4. **Risk Score** is calculated (0–100)
    5. **Recommendation** is generated
    """)

    st.divider()

    st.markdown("### 🧪 Try These Examples")
    examples = [
        "BREAKING: Massive 7.8 earthquake hits central Turkey. Over 2,000 feared dead. FEMA deploying rescue teams.",
        "Just saw an amazing sunset over the beach. The sky looked like it was on fire! 🌅",
        "There is a huge wildfire spreading near our town but I haven't seen any news about it yet, is anyone else seeing this?",
        "According to Reuters, flash floods in southern Germany have displaced 10,000 residents. Red Cross shelters are open.",
        "The stock market crashed today, complete disaster for my portfolio 📉",
    ]
    for i, example in enumerate(examples):
        if st.button(
            f"Example {i + 1}",
            key=f"example_{i}",
            use_container_width=True,
        ):
            st.session_state["user_message"] = example


# ── Main Input ──────────────────────────────────────────────────────
st.markdown("### 💬 Enter a Message to Verify")

user_message = st.text_area(
    label="Message",
    value=st.session_state.get("user_message", ""),
    height=120,
    placeholder="Paste a disaster-related message here...",
    label_visibility="collapsed",
)

analyze_clicked = st.button(
    "🔍  Analyze Message",
    type="primary",
    use_container_width=True,
    disabled=not user_message.strip(),
)


# ── Analysis ────────────────────────────────────────────────────────
if analyze_clicked and user_message.strip():
    with st.spinner("🧠 Analyzing message... this may take a few seconds."):
        report: VerificationReport = run_pipeline(user_message.strip())

    st.markdown("---")

    # ── Verdict Banner ──────────────────────────────────────────────
    level = report.risk_assessment.level.lower()
    rec = report.recommendation

    st.markdown(f"""
    <div class="verdict-box verdict-{level}">
        <div style="font-size: 2.5rem; margin-bottom: 0.3rem;">{rec.emoji}</div>
        <div style="color: #fff; font-size: 1.5rem; font-weight: 700;">{rec.verdict}</div>
        <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 0.5rem;">
            Risk Score: {report.risk_assessment.score}/100 &nbsp;•&nbsp; Level: {report.risk_assessment.level}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics Row ─────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Crisis Type</div>
            <div class="value">{report.llm_analysis.crisis_type.title()}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Location</div>
            <div class="value">{report.llm_analysis.location}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        urgency_colors = {
            "low": "#4caf50", "medium": "#ff9800",
            "high": "#f44336", "critical": "#ff1744",
        }
        u_color = urgency_colors.get(report.llm_analysis.urgency, "#fff")
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Urgency</div>
            <div class="value" style="color: {u_color};">
                {report.llm_analysis.urgency.upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">ML Prediction</div>
            <div class="value" style="font-size: 1.1rem;">
                {report.ml_prediction.label}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detail Panels ──────────────────────────────────────────────
    left_col, right_col = st.columns(2)

    with left_col:
        # Risk Score Gauge
        st.markdown("#### 📊 Risk Score Gauge")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=report.risk_assessment.score,
            number={"suffix": "/100", "font": {"size": 40, "color": "#fff"}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#555",
                    "tickfont": {"color": "#aaa"},
                },
                "bar": {"color": "#6c63ff"},
                "bgcolor": "#1a1a2e",
                "steps": [
                    {"range": [0, 25], "color": "#1b5e20"},
                    {"range": [25, 50], "color": "#e65100"},
                    {"range": [50, 75], "color": "#b71c1c"},
                    {"range": [75, 100], "color": "#880e0e"},
                ],
                "threshold": {
                    "line": {"color": "#ff1744", "width": 3},
                    "thickness": 0.8,
                    "value": report.risk_assessment.score,
                },
            },
        ))
        fig.update_layout(
            height=280,
            margin=dict(l=30, r=30, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#fff"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # Score Breakdown
        with st.expander("📋 Score Breakdown", expanded=True):
            for component, points in report.risk_assessment.breakdown.items():
                max_pts = {
                    "ML Confidence": 30, "Urgency Level": 25,
                    "Source Absent": 10, "Evidence Absent": 10,
                    "Keyword Density": 15, "Message Length": 10,
                }.get(component, 10)
                st.markdown(f"""
                <div class="breakdown-item">
                    <span style="color: rgba(255,255,255,0.8);">{component}</span>
                    <span style="color: #6c63ff; font-weight: 600;">
                        +{points}/{max_pts}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    with right_col:
        # Recommendation
        st.markdown("#### 💡 Recommendation")
        st.markdown(rec.message)

        st.markdown(f"""
        <div class="disclaimer-box">
            {rec.disclaimer}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # LLM Extracted Features
        with st.expander("🔬 LLM Extracted Features", expanded=True):
            feat_col1, feat_col2 = st.columns(2)
            with feat_col1:
                st.markdown(f"**Source Cited:** {'✅ Yes' if report.llm_analysis.source_present else '❌ No'}")
            with feat_col2:
                st.markdown(f"**Evidence Found:** {'✅ Yes' if report.llm_analysis.evidence_present else '❌ No'}")

            if report.llm_analysis.raw_reasoning:
                st.markdown(f"**LLM Reasoning:** {report.llm_analysis.raw_reasoning}")

        # ML Details
        with st.expander("🤖 ML Classification Details"):
            st.markdown(f"**Model:** {report.ml_prediction.model_used}")
            st.markdown(f"**Confidence:** {report.ml_prediction.confidence:.1%}")

            # Confidence bar
            conf_pct = report.ml_prediction.confidence * 100
            bar_color = "#4caf50" if report.ml_prediction.label == "Likely Non-Crisis" else "#f44336"
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 8px;
                        height: 12px; overflow: hidden; margin-top: 0.5rem;">
                <div style="background: {bar_color}; width: {conf_pct}%;
                            height: 100%; border-radius: 8px;
                            transition: width 0.5s ease;"></div>
            </div>
            """, unsafe_allow_html=True)

    # ── Footer ──────────────────────────────────────────────────────
    st.markdown("---")
    st.caption(
        f"⏱️ Analysis completed in {report.processing_time_seconds:.2f}s  "
        f"&nbsp;•&nbsp; Crisis Rumor Verification Agent v1.0"
    )
