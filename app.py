# app.py — tambah di bagian import atas
from model_loader import load_model, load_norm_dict

# Panggil sekali di awal sebelum routing page
# supaya model sudah di-cache sebelum page manapun dibuka
load_model()
load_norm_dict()

import streamlit as st

st.set_page_config(
    page_title="Valence-Arousal Model",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

/* ── FONT ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* ── ROOT TOKENS ────────────────────────────────────── */
:root {
    --bg-base:       #ffffff;
    --bg-surface:    #f5f7fb;
    --bg-card:       #ffffff;

    --text-primary:  #1a1a1a;
    --text-secondary:#4a5568;
    --text-muted:    #718096;

    --border:        #e2e8f0;
    --border-accent: rgba(82,183,196,0.35);
    --accent-blue:   #3d85c8;
    --accent-teal:   #38a89d;
    --accent-glow:   rgba(82,183,196,0.15);

    --radius-card:   12px;
    --radius-sm:     8px;
}

/* ── APP BACKGROUND ─────────────────────────────────── */
html, body {
    background: #ffffff !important;
    background-color: #ffffff !important;
}

.stApp,
.stApp > div,
.stApp > div > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div,
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMain"] > div,
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="block-container"],
.main, .main > div,
section.main, section.main > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
}

/* force custom HTML divs transparent */
.stMarkdown div,
.element-container div {
    background-color: transparent;
}

/* ── SIDEBAR ────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #f5f7fb;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text-secondary) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text-primary) !important;
}

/* ── HEADINGS ───────────────────────────────────────── */
h1, h2, h3, h4 {
    color: #1a1a1a !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

/* ── BODY TEXT (scoped to Streamlit native elements only) ── */
[data-testid="stMarkdown"] > div > p,
[data-testid="stMarkdown"] > div > ul > li,
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stRadio label {
    color: var(--text-secondary);
    line-height: 1.7;
}

/* ── CARD ───────────────────────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-card);
    padding: 28px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(61,133,200,0.04) 0%, transparent 60%);
    pointer-events: none;
}

/* card with accent border on left */
.card-accent {
    border-left: 2px solid var(--accent-teal);
}

/* ── ACCENT CARD (highlight box) ────────────────────── */
.info-box {
    background: rgba(61,133,200,0.07);
    border: 1px solid var(--border-accent);
    border-radius: var(--radius-sm);
    padding: 16px 20px;
    margin: 16px 0;
}

/* ── SECTION DIVIDER ────────────────────────────────── */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(82,183,196,0.3), transparent);
    margin: 48px 0;
}

/* ── METRIC ─────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card);
    border-radius: var(--radius-card);
    border: 1px solid var(--border);
    padding: 16px;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
}

/* ── BUTTON ─────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-teal));
    border: none;
    color: #f0f6ff;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-family: 'Sora', sans-serif;
    letter-spacing: 0.01em;
    transition: opacity 0.2s, transform 0.15s;
}

.stButton > button:hover {
    opacity: 0.88;
    transform: translateY(-1px);
}

/* ── INPUT ──────────────────────────────────────────── */
.stTextInput input,
.stTextArea textarea,
.stSelectbox select {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Sora', sans-serif !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--border-accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

/* ── RADIO / SELECTBOX ──────────────────────────────── */
[data-testid="stRadio"] label,
[data-testid="stSelectbox"] label {
    color: var(--text-secondary) !important;
}

/* ── TABS ───────────────────────────────────────────── */
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-family: 'Sora', sans-serif;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background: var(--accent-teal) !important;
}

/* ── CODE MONO ──────────────────────────────────────── */
code, pre {
    font-family: 'DM Mono', monospace !important;
    background: var(--bg-surface) !important;
    color: var(--accent-teal) !important;
    border-radius: 6px;
}

/* ── EXPANDER ───────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── HERO ───────────────────────────────────────────── */
.hero-title {
    text-align: center;
    font-size: clamp(32px, 5vw, 52px);
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    margin-top: 12px;
    line-height: 1.1;
}

.hero-title span {
    background: linear-gradient(120deg, var(--accent-blue), var(--accent-teal));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent !important;
}

.hero-sub {
    text-align: center;
    color: var(--text-muted);
    font-size: 15px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 40px;
}

/* ── TAG / BADGE ────────────────────────────────────── */
.badge {
    display: inline-block;
    background: rgba(61,133,200,0.12);
    color: var(--accent-teal);
    border: 1px solid var(--border-accent);
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── ENTRANCE ANIMATIONS ────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0);    }
}
.anim { opacity: 0; animation: fadeUp 0.55s cubic-bezier(0.22,1,0.36,1) forwards; }
.d0 { animation-delay: 0.00s; }
.d1 { animation-delay: 0.08s; }
.d2 { animation-delay: 0.16s; }
.d3 { animation-delay: 0.24s; }
.d4 { animation-delay: 0.32s; }
.d5 { animation-delay: 0.40s; }

/* ── SCROLLBAR ──────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-accent); border-radius: 2px; }

/* ── HIDE STREAMLIT BRANDING ────────────────────────── */
#MainMenu, footer { visibility: hidden; }

/* ── CHAT INPUT BOTTOM BAR ──────────────────────────── */
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottom"] > div > div,
div[data-testid="stBottomBlockContainer"],
div[data-testid="stBottomBlockContainer"] > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
}

div[data-testid="stBottom"] {
    border-top: 1px solid rgba(82,183,196,0.15) !important;
}

div[data-testid="stChatInput"] {
    background: #f5f7fb !important;
    border: 1px solid rgba(82,183,196,0.25) !important;
    border-radius: 14px !important;
}

div[data-testid="stChatInput"] textarea {
    background: #f5f7fb !important;
    color: #1a1a1a !important;
    caret-color: #52b7c4 !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #718096 !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

st.sidebar.markdown("""
<style>
[data-testid="stSidebar"] {
    background: #f5f7fb !important;
    border-right: 1px solid rgba(82,183,196,0.18) !important;
}
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    color: #4a5568 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(82,183,196,0.08) !important;
    border-color: rgba(82,183,196,0.22) !important;
    color: #2d6fa3 !important;
}
</style>

<div style="padding: 24px 4px 8px;">
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
        <div style="
            width:36px; height:36px;
            background: linear-gradient(135deg, rgba(61,133,200,0.15), rgba(82,183,196,0.1));
            border: 1px solid rgba(82,183,196,0.25);
            border-radius: 10px;
            display:flex; align-items:center; justify-content:center;
            font-size: 18px; flex-shrink:0;
        ">🧠</div>
        <div>
            <div style="font-size:15px; font-weight:700; color:#1a1a1a; letter-spacing:-0.01em; line-height:1.2;">
                V–A Explorer
            </div>
            <div style="font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:#718096;">
                XLM-RoBERTa · Regression
            </div>
        </div>
    </div>
    <div style="height:1px; background:linear-gradient(90deg, transparent, rgba(82,183,196,0.3), transparent); margin: 16px 0 20px;"></div>
    <div style="font-size:10px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;
                color:#a0aec0; margin-bottom:10px; padding-left:4px;">
        Navigation
    </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "",
    [
        "📖  Model Overview",
        "📊  Affective Distribution",
        "🔍  Inference Interface",
        "🧠 Pattern Explorer"
    ]
)

st.sidebar.markdown("""
<div style="height:1px; background:linear-gradient(90deg, transparent, rgba(82,183,196,0.2), transparent); margin: 20px 0;"></div>

<div style="padding: 0 4px;">
    <div style="font-size:10px; font-weight:700; letter-spacing:0.14em; text-transform:uppercase;
                color:#a0aec0; margin-bottom:12px;">
        Model Metadata
    </div>
    <div style="display:flex; flex-direction:column; gap:8px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#718096;">Architecture</span>
            <span style="font-size:12px; color:#4a5568; font-family:'DM Mono',monospace;">XLM-RoBERTa</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#718096;">Task</span>
            <span style="font-size:12px; color:#4a5568; font-family:'DM Mono',monospace;">Regression</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#718096;">Output Dims</span>
            <span style="font-size:12px; color:#4a5568; font-family:'DM Mono',monospace;">Valence · Arousal</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#718096;">Domain</span>
            <span style="font-size:12px; color:#4a5568; font-family:'DM Mono',monospace;">Mental Health NLP</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:#718096;">Language</span>
            <span style="font-size:12px; color:#4a5568; font-family:'DM Mono',monospace;">Indonesian (id)</span>
        </div>
    </div>
</div>

<div style="height:1px; background:linear-gradient(90deg, transparent, rgba(82,183,196,0.2), transparent); margin: 20px 0;"></div>

<div style="
    background: rgba(61,133,200,0.06);
    border: 1px solid rgba(82,183,196,0.2);
    border-radius: 10px;
    padding: 12px 14px;
">
    <div style="font-size:11px; font-weight:700; color:#3d85c8; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:4px;">
        ⚡ SHAP-Powered
    </div>
    <div style="font-size:12px; color:#718096; line-height:1.6;">
        Token-level attribution via Shapley values for post-hoc interpretability.
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO HEADER ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-title">
    Valence–Arousal <span>Explorer</span>
</div>
<div class="hero-sub">
    Transformer-Based · Mental Health · Emotion Analysis
</div>
""", unsafe_allow_html=True)

# ── ROUTING ───────────────────────────────────────────────────────────────────

if page == "📖  Model Overview":
    import page_about
    page_about.show()

elif page == "📊  Affective Distribution":
    import page_visualization
    page_visualization.show()

elif page == "🔍  Inference Interface":
    import page_predict
    page_predict.show()

elif page == "🧠 Pattern Explorer":
    import page_pattern_explorer
    page_pattern_explorer.show()