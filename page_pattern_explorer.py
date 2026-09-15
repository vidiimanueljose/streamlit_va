import streamlit as st
import streamlit.components.v1 as components
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics.pairwise import cosine_similarity

from preprocessing import preprocess
from model_loader import load_model, load_norm_dict, VALENCE_INDEX, AROUSAL_INDEX

# ── CENTROID DATA ──────────────────────────────────────────────────────────────
CENTROIDS = {
    "Anxiety": {
        "Valence": -0.4114880273660205,
        "Arousal":  0.022217075256556442
    },
    "Depression": {
        "Valence": -0.44495064540622625,
        "Arousal": -0.13036783936556146
    },
    "ADHD": {
        "Valence": -0.32436708860759494,
        "Arousal": -0.014746835443037974
    }
}

CENTROID_COLORS = {
    "Anxiety":    "#7c83ff",   # purple
    "Depression": "#52b7c4",   # teal
    "ADHD":       "#f0896b",   # coral
}

MEDAL = ["🥇", "🥈", "🥉"]


# ── HELPER FUNCTIONS ───────────────────────────────────────────────────────────
def predict_va(text: str, tokenizer, model, norm_dict, noise_set):
    """Return (valence, arousal) for a single text."""
    cleaned = preprocess(text, norm_dict, noise_set)
    inputs = tokenizer(
        cleaned,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    )
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs["logits"][0].tolist()
    valence = logits[VALENCE_INDEX]
    arousal = logits[AROUSAL_INDEX]
    return valence, arousal


def compute_similarity(user_centroid: dict) -> dict:
    """
    Cosine similarity between user centroid and each disorder centroid.
    Normalized to 0–100% range.
    """
    u = np.array([[user_centroid["Valence"], user_centroid["Arousal"]]])
    results = {}
    for name, c in CENTROIDS.items():
        d = np.array([[c["Valence"], c["Arousal"]]])
        sim = cosine_similarity(u, d)[0][0]
        # cosine similarity: -1 to 1 → normalize to 0–100%
        results[name] = round((sim + 1) / 2 * 100, 1)
    return dict(sorted(results.items(), key=lambda x: -x[1]))


def make_scatter(predictions: list, user_centroid: dict) -> plt.Figure:
    """Scatter plot: individual user points + user centroid (▲) + disorder centroids (●)."""
    fig, ax = plt.subplots(figsize=(5, 4))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f5f7fb")

    # Grid & axes
    ax.axhline(0, color="#e2e8f0", linewidth=0.8, linestyle="--")
    ax.axvline(0, color="#e2e8f0", linewidth=0.8, linestyle="--")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_xlabel("Valence", color="#4a5568", fontsize=10)
    ax.set_ylabel("Arousal", color="#4a5568", fontsize=10)
    ax.tick_params(colors="#4a5568", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#e2e8f0")

    # Individual user points (small, transparent)
    vs = [p["valence"] for p in predictions]
    ars = [p["arousal"] for p in predictions]
    ax.scatter(vs, ars, color="#f0c040", alpha=0.4, s=30, zorder=3, label="_nolegend_")

    # Disorder centroids
    for name, c in CENTROIDS.items():
        ax.scatter(
            c["Valence"], c["Arousal"],
            color=CENTROID_COLORS[name],
            s=90, marker="o", zorder=5,
            edgecolors="white", linewidths=0.6,
        )
        ax.annotate(
            name,
            xy=(c["Valence"], c["Arousal"]),
            xytext=(6, 6), textcoords="offset points",
            color=CENTROID_COLORS[name], fontsize=8,
        )

    # User centroid (triangle)
    ax.scatter(
        user_centroid["Valence"], user_centroid["Arousal"],
        color="#f0c040", s=120, marker="^", zorder=6,
        edgecolors="white", linewidths=0.8, label="User centroid",
    )
    ax.annotate(
        "User ▲",
        xy=(user_centroid["Valence"], user_centroid["Arousal"]),
        xytext=(6, -14), textcoords="offset points",
        color="#f0c040", fontsize=8,
    )

    # Disorder legend patches
    patches = [
        mpatches.Patch(color=CENTROID_COLORS[n], label=n) for n in CENTROIDS
    ]
    patches.append(mpatches.Patch(color="#f0c040", label="User centroid"))
    ax.legend(
        handles=patches,
        fontsize=7,
        facecolor="#ffffff",
        edgecolor="#e2e8f0",
        labelcolor="#4a5568",
        loc="upper right",
    )

    ax.set_title("V–A Centroid Comparison", color="#1a1a1a", fontsize=11, pad=10)
    fig.tight_layout()
    return fig


def make_radar(similarity: dict) -> plt.Figure:
    """Radar / spider chart for 3 disorder similarities."""
    labels = list(similarity.keys())
    values = [similarity[k] / 100 for k in labels]
    N = len(labels)

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f5f7fb")

    ax.plot(angles, values, color="#38a89d", linewidth=1.5)
    ax.fill(angles, values, color="#38a89d", alpha=0.2)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        [f"{labels[i]}\n{similarity[labels[i]]:.1f}%" for i in range(N)],
        color="#4a5568", fontsize=9,
    )
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], color="#718096", fontsize=7)
    ax.set_ylim(0, 1)
    ax.tick_params(colors="#4a5568")
    ax.grid(color="#e2e8f0", linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_edgecolor("#e2e8f0")

    ax.set_title("Similarity Profile", color="#1a1a1a", fontsize=11, pad=18)
    fig.tight_layout()
    return fig


def render_ranking_html(similarity: dict) -> str:
    """Render ranking as a full HTML document for components.html."""
    rows = ""
    for i, (name, pct) in enumerate(similarity.items()):
        bar_color = CENTROID_COLORS.get(name, "#52b7c4")
        medal = MEDAL[i] if i < 3 else ""
        rows += f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                    border-bottom:1px solid #e2e8f0;">
            <span style="font-size:18px;min-width:28px;">{medal}</span>
            <span style="font-size:14px;font-weight:600;flex:1;color:#1a1a1a;">{name}</span>
            <div style="flex:2;height:6px;background:#f0f0f5;border-radius:3px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;background:{bar_color};border-radius:3px;"></div>
            </div>
            <span style="font-size:13px;color:#718096;min-width:52px;text-align:right;">{pct:.1f}%</span>
        </div>
        """
    return f"""
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: transparent; font-family: 'Sora', sans-serif; padding: 2px; }}
    </style>
    </head>
    <body>
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;padding:16px 20px;">
        {rows}
    </div>
    </body>
    </html>
    """


def get_quadrant(valence: float, arousal: float) -> tuple:
    """Return (quadrant_label, characteristic_description) for a V-A point, based on Russell's circumplex model of affect."""
    if valence >= 0 and arousal >= 0:
        return (
            "Quadrant I (high valence, high arousal)",
            "This quadrant generally reflects pleasant, energized emotional states such as "
            "excitement, happiness, elation, and enthusiasm."
        )
    elif valence < 0 and arousal >= 0:
        return (
            "Quadrant II (low valence, high arousal)",
            "This quadrant generally reflects unpleasant, energized emotional states such as "
            "anger, anxiety, tension, and distress."
        )
    elif valence < 0 and arousal < 0:
        return (
            "Quadrant III (low valence, low arousal)",
            "This quadrant generally reflects unpleasant, low-energy emotional states such as "
            "sadness, boredom, fatigue, and low mood."
        )
    else:
        return (
            "Quadrant IV (high valence, low arousal)",
            "This quadrant generally reflects pleasant, low-energy emotional states such as "
            "calmness, relaxation, contentment, and serenity."
        )


def get_confidence_level(pct: float) -> str:
    """Classify a similarity percentage into a qualitative likelihood level."""
    if pct >= 70:
        return "High"
    elif pct >= 40:
        return "Moderate"
    else:
        return "Low"


def render_interpretation(similarity: dict, user_centroid: dict) -> str:
    """Auto-generated interpretation text based on ranking — framed as dataset pattern similarity, not diagnosis."""
    names = list(similarity.keys())
    pcts  = list(similarity.values())

    top_name    = names[0];  top_pct    = pcts[0]
    second_name = names[1];  second_pct = pcts[1]
    third_name  = names[2];  third_pct  = pcts[2]

    diff_1_2 = round(top_pct - second_pct, 1)

    # Narrative for how dominant the top pattern is
    if diff_1_2 < 2:
        dominance = (
            f"All three patterns are very close to each other "
            f"(top gap is only {diff_1_2:.1f}%), reflecting the proximity of "
            f"affective distributions across groups in the dataset."
        )
    elif diff_1_2 < 5:
        dominance = (
            f"The <strong style='color:#ffffff;'>{top_name}</strong> pattern is slightly more dominant "
            f"than {second_name} (gap: {diff_1_2:.1f}%)."
        )
    else:
        dominance = (
            f"The <strong style='color:##000000;'>{top_name}</strong> pattern stands out "
            f"compared to the others (gap: {diff_1_2:.1f}% from second place)."
        )

    top_color = CENTROID_COLORS.get(top_name, "#52b7c4")

    # ── Cartesian quadrant interpretation ──────────────────────────────────
    quadrant_label, quadrant_desc = get_quadrant(
        user_centroid["Valence"], user_centroid["Arousal"]
    )

    # ── Radar chart likelihood interpretation (top pattern only) ───────────
    top_level = get_confidence_level(top_pct)

    consult_note = ""
    if top_level in ("High", "Moderate"):
        consult_note = f"""
        <p style="font-size:13px;color:#1a1a1a;line-height:1.7;margin:0 0 12px;
                  background:#fff7e6;border:1px solid #ffe0a3;border-radius:10px;padding:10px 14px;">
            💡 <strong>Suggestion:</strong> The {top_name} pattern falls into a
            <strong>{top_level.lower()}</strong> likelihood range. While this is
            <strong>not a diagnosis</strong>, it may still be worth talking to a mental
            health professional such as a psychologist or psychiatrist for a proper
            assessment and guidance.
        </p>"""

    return f"""
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: transparent; font-family: 'Sora', sans-serif; padding: 2px; }}
    </style>
    </head>
    <body>
    <div style="background:#ffffff;border:1px solid #e2e8f0;border-left:3px solid {top_color};
                border-radius:14px;padding:16px 20px;">
        <div style="font-size:12px;font-weight:700;letter-spacing:0.08em;color:{top_color};
                    text-transform:uppercase;margin-bottom:8px;">Interpretation</div>

        <p style="font-size:14px;color:#4a5568;line-height:1.7;margin:0 0 12px;">
            The Valence-Arousal profile of the submitted texts most closely matches
            the affective pattern of the
            <strong style="color:#1a1a1a;">{top_name}</strong>
            group in the dataset ({top_pct:.1f}%), followed by
            <strong style="color:#1a1a1a;">{second_name}</strong> ({second_pct:.1f}%) and
            <strong style="color:#1a1a1a;">{third_name}</strong> ({third_pct:.1f}%).
            {dominance}
            Based on the average Valence ({user_centroid['Valence']:.4f}) and Arousal
            ({user_centroid['Arousal']:.4f}) values, the user centroid falls into
            <strong style="color:#1a1a1a;">{quadrant_label}</strong>, so {quadrant_desc[0].lower()}{quadrant_desc[1:]}
            On the radar chart, the highest similarity value belongs to
            <strong style="color:#1a1a1a;">{top_name}</strong> at {top_pct:.1f}%, which falls
            into the <strong>{top_level.lower()}</strong> likelihood range.
        </p>
        {consult_note}

        <p style="font-size:12px;color:#718096;line-height:1.6;margin:0;
                  border-top:1px solid #e2e8f0;padding-top:10px;">
            ⚠️ This result <strong>only reflects affective pattern similarity</strong>
            between the submitted texts and the average of each group in the training dataset.
            It is not a prediction of any psychological condition and cannot be used as
            a basis for medical or psychological diagnosis in any form.
        </p>
    </div>
    </body>
    </html>
    """


# ── MAIN PAGE ──────────────────────────────────────────────────────────────────
def show():
    # ── PAGE HEADER ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="anim d0">
        <div style="margin-bottom:6px;">
            <span class="badge">Pattern Analysis</span>
        </div>
        <h2 style="margin:0 0 8px;">Mental Health Pattern Explorer</h2>
        <p style="margin:0;">
            Enter one or more Indonesian texts. The model will predict
            <strong>Valence</strong> and <strong>Arousal</strong> for each text,
            then compare the emotional profile against the average affective patterns of
            the <em>Anxiety</em>, <em>Depression</em>, and <em>ADHD</em>
            groups in the dataset, to find <strong>which pattern most closely matches</strong>
            the texts you entered.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider anim d1"></div>', unsafe_allow_html=True)

    # ── DISCLAIMER ────────────────────────────────────────────────────────────
    st.info(
        "⚠️ **Important note:** This feature only compares the Valence–Arousal patterns "
        "of the submitted texts against the group averages in the dataset. "
        "These results are **not** a prediction of any psychological condition and **cannot** "
        "be used as a medical or psychological diagnosis."
    )

    # ── LOAD MODEL ────────────────────────────────────────────────────────────
    try:
        with st.spinner("Loading model... (This may take a moment)"):
            tokenizer, model = load_model()
    except Exception as e:
        st.error(
            f"Error loading model: {e}\n\n"
            "Please ensure the `./model` folder exists and contains all required files."
        )
        return

    norm_dict, noise_set = load_norm_dict()

    # ── TEXT INPUT (dynamic) ──────────────────────────────────────────────────
    st.markdown("""
    <div class="anim d2">
        <div style="margin-bottom:6px;"><span class="badge">Input</span></div>
        <h3 style="margin:0 0 4px;">Text Input</h3>
    </div>
    """, unsafe_allow_html=True)

    # Number of text areas controlled by session_state
    if "n_texts" not in st.session_state:
        st.session_state.n_texts = 3

    col_add, col_remove, _ = st.columns([1, 1, 4])
    with col_add:
        if st.button("＋ Add text") and st.session_state.n_texts < 20:
            st.session_state.n_texts += 1
    with col_remove:
        if st.button("－ Remove text") and st.session_state.n_texts > 1:
            st.session_state.n_texts -= 1

    texts = []
    for i in range(st.session_state.n_texts):
        t = st.text_area(
            f"Text {i + 1}:",
            key=f"text_{i}",
            height=80,
            placeholder=f"Enter text {i + 1} here...",
        )
        texts.append(t)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    if st.button("🔍 Analyze Emotional Pattern", type="primary"):
        valid_texts = [t.strip() for t in texts if t.strip()]
        if len(valid_texts) == 0:
            st.warning("Please enter at least one text.")
            return

        with st.spinner("Predicting Valence–Arousal for each text..."):
            predictions = []
            for t in valid_texts:
                v, a = predict_va(t, tokenizer, model, norm_dict, noise_set)
                predictions.append({"text": t, "valence": v, "arousal": a})

        # ── USER CENTROID ──────────────────────────────────────────────────
        user_centroid = {
            "Valence": float(np.mean([p["valence"] for p in predictions])),
            "Arousal": float(np.mean([p["arousal"] for p in predictions])),
        }

        # ── SIMILARITY ────────────────────────────────────────────────────
        similarity = compute_similarity(user_centroid)

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 1 — User Emotional Profile
        # ═══════════════════════════════════════════════════════════════════
        st.markdown("""
        <div class="anim d0">
            <div style="margin-bottom:6px;"><span class="badge">Output</span></div>
            <h3 style="margin:0 0 4px;">📊 User Emotional Profile</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Valence (avg)", f"{user_centroid['Valence']:.4f}")
        with col2:
            st.metric("Arousal (avg)", f"{user_centroid['Arousal']:.4f}")
        with col3:
            st.metric("Text count", len(predictions))

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 2 — Per-Text Prediction Table
        # ═══════════════════════════════════════════════════════════════════
        st.markdown("""
        <div class="anim d1">
            <div style="margin-bottom:6px;"><span class="badge">Detail</span></div>
            <h3 style="margin:0 0 4px;">🗒️ Per-Text Predictions</h3>
        </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame([
            {
                "#": i + 1,
                "Text (first 50 chars)": p["text"][:50] + ("…" if len(p["text"]) > 50 else ""),
                "Valence": round(p["valence"], 4),
                "Arousal": round(p["arousal"], 4),
            }
            for i, p in enumerate(predictions)
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 3 — Similarity Ranking
        # ═══════════════════════════════════════════════════════════════════
        st.markdown("""
        <div class="anim d2">
            <div style="margin-bottom:6px;"><span class="badge">Ranking</span></div>
            <h3 style="margin:0 0 4px;">🏆 Affective Pattern Similarity</h3>
        </div>
        """, unsafe_allow_html=True)

        components.html(render_ranking_html(similarity), height=175)

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 4 — Visualization (Scatter + Radar)
        # ═══════════════════════════════════════════════════════════════════
        st.markdown("""
        <div class="anim d3">
            <div style="margin-bottom:6px;"><span class="badge">Visualization</span></div>
            <h3 style="margin:0 0 4px;">📈 Centroid Comparison</h3>
        </div>
        """, unsafe_allow_html=True)

        col_scatter, col_radar = st.columns(2)

        with col_scatter:
            fig_scatter = make_scatter(predictions, user_centroid)
            st.pyplot(fig_scatter)
            plt.close(fig_scatter)
            st.caption(
                "▲ = your centroid  ●  = average centroid of each group in the dataset"
            )

        with col_radar:
            fig_radar = make_radar(similarity)
            st.pyplot(fig_radar)
            plt.close(fig_radar)
            st.caption(
                "Radar chart showing how close your profile is "
                "to the affective pattern of each group."
            )

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════════
        # SECTION 5 — Automatic Interpretation
        # ═══════════════════════════════════════════════════════════════════
        st.markdown("""
        <div class="anim d4">
            <div style="margin-bottom:6px;"><span class="badge">Interpretation</span></div>
            <h3 style="margin:0 0 4px;">💬 Automatic Interpretation</h3>
        </div>
        """, unsafe_allow_html=True)

        components.html(render_interpretation(similarity, user_centroid), height=380)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("❓ How do I read the similarity scores?"):
            st.markdown("""
            - **Similarity scores** are calculated using **cosine similarity** between
              your emotional centroid (average Valence & Arousal) and the average centroid
              of each group in the training dataset.
            - Values are normalized to a **0–100%** range, where 100% means the emotional
              vectors are identical in direction.
            - All three groups (Anxiety, Depression, ADHD) have centroids that are close
              together in V–A space, so **differences between groups are usually small**
              (1–5%). This is a characteristic of the dataset's affective distribution.
            - The label **"Affective Pattern Similarity"** is intentional,
              not "Condition Prediction", because this feature only measures
              **how similar your V–A pattern is to the group averages in the dataset**,
              not a diagnosis of any psychological condition.
            """)