import streamlit as st
from PIL import Image
import os


def show():

    st.markdown("""
    <style>

    /* ── ENTRANCE ANIMATIONS ─────────────────────────── */
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

    /* ── IMAGE CARD ──────────────────────────────────── */
    .img-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        padding: 16px 16px 12px;
        margin-bottom: 4px;
        transition: transform 0.25s cubic-bezier(0.22,1,0.36,1),
                    border-color 0.25s ease,
                    box-shadow 0.25s ease;
        cursor: default;
    }

    .img-card:hover {
        transform: translateY(-5px) scale(1.015);
        border-color: rgba(82,183,196,0.45);
        box-shadow: 0 18px 36px rgba(0,0,0,0.45),
                    0 0 0 1px rgba(82,183,196,0.22),
                    0 0 20px rgba(61,133,200,0.15);
    }

    .img-card:hover .img-card-label {
        color: var(--accent-teal) !important;
    }

    .img-card-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 10px;
        transition: color 0.25s ease;
    }

    .img-card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-top: 10px;
        margin-bottom: 2px;
    }

    .img-card-sub {
        font-size: 12px;
        color: var(--text-muted);
    }

    .img-card img {
        border-radius: 8px;
        width: 100%;
    }

    /* ── INTERPRETATION CARD ─────────────────────────── */
    .interp-item {
        display: flex;
        gap: 14px;
        align-items: flex-start;
        padding: 14px 16px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-card);
        margin-bottom: 10px;
        transition: transform 0.25s cubic-bezier(0.22,1,0.36,1),
                    border-color 0.25s ease,
                    box-shadow 0.25s ease;
    }

    .interp-item:hover {
        transform: translateX(5px);
        border-color: rgba(61,133,200,0.3);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3),
                    -3px 0 0 var(--accent-teal);
    }

    .interp-icon {
        font-size: 18px;
        flex-shrink: 0;
        margin-top: 1px;
    }

    .interp-body strong {
        color: var(--text-primary);
        font-size: 14px;
    }

    .interp-body p {
        font-size: 13.5px;
        color: var(--text-secondary);
        line-height: 1.65;
        margin: 4px 0 0;
    }

    </style>
    """, unsafe_allow_html=True)

    # ── PAGE HEADER ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="anim d0">
        <div style="margin-bottom:6px;">
            <span class="badge">Visualization</span>
        </div>
        <h2 style="margin:0 0 8px;">Valence–Arousal Distribution</h2>
        <p style="margin:0;">
            Distribution of valence and arousal scores across the overall dataset
            and each mental health category — Anxiety, Depression, and ADHD.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider anim d1"></div>', unsafe_allow_html=True)

    # ── CHARTS ────────────────────────────────────────────────────────────────
    images = [
        ("all_data.png",   "Overall",    "All Categories"),
        ("anxiety.png",    "Anxiety",    "Mental Health · Anxiety"),
        ("depression.png", "Depression", "Mental Health · Depression"),
        ("adhd.png",       "ADHD",       "Mental Health · ADHD"),
    ]

    # Row 1: overall (full width)
    label, title, sub = images[0]
    label = os.path.join(".", "figure", label)
    st.markdown(f"""
    <div class="img-card anim d2">
        <div class="img-card-label">Overall Dataset</div>
        {"<img src='data:image/png;base64," + _img_b64(label) + "'/>" if os.path.exists(label) else "<p style='color:var(--text-muted);font-size:13px;'>File not found: " + label + "</p>"}
        <div class="img-card-title">{title}</div>
        <div class="img-card-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

    # Row 2: 3 conditions side by side
    col1, col2, col3 = st.columns(3, gap="medium")
    delays = ["d3", "d4", "d5"]
    for col, (fname, title, sub), delay in zip([col1, col2, col3], images[1:], delays):
        fname = os.path.join(".", "figure", fname)
        with col:
            st.markdown(f"""
            <div class="img-card anim {delay}">
                <div class="img-card-label">By Condition</div>
                {"<img src='data:image/png;base64," + _img_b64(fname) + "'/>" if os.path.exists(fname) else "<p style='color:var(--text-muted);font-size:13px;'>File not found: " + fname + "</p>"}
                <div class="img-card-title">{title}</div>
                <div class="img-card-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider anim d0"></div>', unsafe_allow_html=True)

    # ── INTERPRETATION ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="anim d0">
        <div style="margin-bottom:16px;">
            <span class="badge">Findings</span>
            <h3 style="margin:8px 0 4px;">Interpreting the Results</h3>
            <p style="font-size:14px; margin:0;">
                These figures illustrate the distribution of valence and arousal scores
                for the overall dataset and each mental health category. In general, the
                highest density is concentrated in the negative-valence region, particularly
                at low to moderate arousal levels — consistent with the nature of the collected
                data, which primarily consist of mental health-related complaints and emotional
                concerns shared on social media platforms.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    interpretations = [
        ("🗂️", "Overall Dataset",
         "The distribution is mainly located in Quadrants II and III, indicating that negative emotional expressions are more dominant than positive ones. This suggests that discussions related to mental health are generally associated with unfavorable emotional states regardless of their level of activation."),
        ("😰", "Anxiety",
         "The density is spread across Quadrants II and III, indicating the presence of negative emotions accompanied by varying levels of arousal. Users discussing anxiety may experience a range of emotional activation — from relatively calm negative states to more intense and activated emotional responses."),
        ("😔", "Depression",
         "The distribution shows a stronger concentration in Quadrant III, representing negative valence and low arousal. Compared with anxiety and ADHD, depression-related texts are more frequently associated with low-activation emotional states — consistent with characteristics such as sadness, hopelessness, fatigue, and reduced energy."),
        ("⚡", "ADHD",
         "Similar to anxiety, the density spans Quadrants II and III, suggesting negative emotions at varying arousal levels. This range of activation is consistent with the varied emotional experiences reported in ADHD, from low-energy frustration to more intense and activated states."),
        ("📊", "Overall Takeaway",
         "While all three categories are characterized by predominantly negative emotional valence, differences can be observed in their arousal distributions. Anxiety and ADHD exhibit a broader range of arousal levels, whereas depression tends to concentrate in low-arousal negative emotional states — suggesting that the arousal dimension provides additional information for distinguishing emotional patterns across mental health conditions."),
    ]

    for i, (icon, title, body) in enumerate(interpretations):
        delay = ["d1","d2","d3","d4","d5"][i]
        st.markdown(f"""
        <div class="interp-item anim {delay}">
            <div class="interp-icon">{icon}</div>
            <div class="interp-body">
                <strong>{title}</strong>
                <p>{body}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── HELPER: base64 encode image ───────────────────────────────────────────────
def _img_b64(path: str) -> str:
    import base64
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""