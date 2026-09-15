import streamlit as st
from PIL import Image
import os


def show():

    st.markdown("""
    <style>

    /* ── STICKY HEADER ───────────────────────────────── */
    .sticky-header {
        position: sticky;
        top: 2.875rem;
        z-index: 999;
        padding: 20px 24px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        margin-bottom: 36px;
    }

    .sticky-title {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #111827;
        margin-bottom: 14px;
    }

    .sticky-nav {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .sticky-nav a {
        text-decoration: none;
        color: #4b5563;
        font-size: 13px;
        font-weight: 500;
        padding: 6px 14px;
        border-radius: 999px;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        transition: background 0.2s, color 0.2s, border-color 0.2s;
    }

    .sticky-nav a:hover {
        background: #e0f2fe;
        border-color: #bae6fd;
        color: #0369a1;
    }

    /* ── QUADRANT CARD ───────────────────────────────── */
    .quadrant-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 14px;
        min-height: 160px;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s cubic-bezier(0.22,1,0.36,1),
                    border-color 0.25s ease,
                    box-shadow 0.25s ease;
        cursor: default;
    }

    .quadrant-card::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(61,133,200,0.03) 0%, transparent 60%);
        pointer-events: none;
    }

    .quadrant-card:hover {
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(82,183,196,0.4);
        box-shadow: 0 12px 28px rgba(0,0,0,0.07),
                    0 0 0 1px rgba(82,183,196,0.2);
    }

    .quadrant-card:hover .quadrant-title {
        color: #38a89d !important;
    }

    .quadrant-card:hover .quadrant-label {
        color: rgba(56,168,157,0.8);
    }

    /* ── QUADRANT TEXT ───────────────────────────────── */
    .quadrant-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6b7280;
        margin-bottom: 8px;
        transition: color 0.25s ease;
    }

    .quadrant-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 10px;
        transition: color 0.25s ease;
    }

    .quadrant-desc {
        color: #4b5563;
        font-size: 14px;
        line-height: 1.65;
    }

    .quadrant-examples {
        margin-top: 10px;
        font-size: 12px;
        color: #6b7280;
    }

    .quadrant-examples span {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
        border-radius: 999px;
        padding: 2px 10px;
        margin: 2px 3px 0 0;
        font-size: 12px;
    }

    /* ── ARCH STEP ───────────────────────────────────── */
    .arch-step {
        display: flex;
        gap: 16px;
        align-items: flex-start;
        padding: 18px 20px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        margin-bottom: 12px;
        transition: transform 0.25s cubic-bezier(0.22,1,0.36,1),
                    border-color 0.25s ease,
                    box-shadow 0.25s ease;
        cursor: default;
    }

    .arch-step:hover {
        transform: translateX(5px);
        border-color: rgba(61,133,200,0.3);
        box-shadow: 0 6px 18px rgba(0,0,0,0.06),
                    -3px 0 0 #38a89d;
    }

    .arch-step-num {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3d85c8, #38a89d);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .arch-step:hover .arch-step-num {
        transform: scale(1.12);
        box-shadow: 0 0 12px rgba(82,183,196,0.4);
    }

    .arch-step-body h4 {
        color: #111827 !important;
        font-size: 0.95rem !important;
        margin: 0 0 6px !important;
    }

    .arch-step-body p {
        font-size: 13.5px;
        color: #4b5563;
        line-height: 1.65;
        margin: 0;
    }

    /* ── INLINE CODE ─────────────────────────────────── */
    code.inline-code {
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        background: #eef2ff;
        color: #1e40af;
        border-radius: 4px;
        padding: 1px 6px;
    }

    /* ── ENTRANCE ANIMATIONS ─────────────────────────── */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(22px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeLeft {
        from { opacity: 0; transform: translateX(-18px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    .anim {
        opacity: 0;
        animation: fadeUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .anim-left {
        opacity: 0;
        animation: fadeLeft 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .d0 { animation-delay: 0.00s; }
    .d1 { animation-delay: 0.08s; }
    .d2 { animation-delay: 0.16s; }
    .d3 { animation-delay: 0.24s; }
    .d4 { animation-delay: 0.32s; }
    .d5 { animation-delay: 0.40s; }
    .d6 { animation-delay: 0.48s; }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider anim d0"></div>', unsafe_allow_html=True)

    # ── SELF-ASSESSMENT MANIKIN ───────────────────────────────────────────────
    st.header("Self-Assessment Manikin (SAM)")

    st.markdown("""
    <div class="anim d0">
    <p>The <em>Self-Assessment Manikin</em> (SAM) is a visual affective rating instrument
    used by the 10 annotators in this study to assess the valence and arousal
    dimensions of each text in the dataset. SAM presents a series of pictographic
    figures arranged along a scale, allowing respondents to rate their emotional
    response intuitively without relying on verbal descriptions.</p>
    </div>

    <div class="anim d1">
    <p>SAM captures three affective dimensions through its pictographic scale: the
    degree of pleasantness versus unpleasantness (valence), the level of excitement
    versus calmness (arousal), and the sense of being controlled versus in control
    (dominance). For the purposes of this study, only the valence and arousal
    dimensions were used. Ratings were collected on a 1–9 scale and subsequently
    normalized to the range of −1 to 1 to align with the model's continuous output
    representation.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Valence Scale")
        if os.path.exists("./figure/valence_sam.png"):
            st.image(Image.open("./figure/valence_sam.png"), use_container_width=True)
    with col2:
        st.subheader("Arousal Scale")
        if os.path.exists("./figure/arousal_sam.png"):
            st.image(Image.open("./figure/arousal_sam.png"), use_container_width=True)

    st.markdown('<div class="section-divider anim d0"></div>', unsafe_allow_html=True)

    # ── EMOTION QUADRANTS ─────────────────────────────────────────────────────
    st.header("Emotion Quadrants")

    st.markdown("""
    <div class="anim d0">
    <p>The combination of valence and arousal values forms four distinct emotion
    quadrants within a two-dimensional affective space. Each quadrant represents
    a cluster of emotional states that share a similar direction and level of
    intensity.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="quadrant-card anim d1" style="border-top:2px solid #c46052;">
            <div class="quadrant-label">Quadrant II</div>
            <div class="quadrant-title">Negative Valence · High Arousal</div>
            <div class="quadrant-desc">Unpleasant and highly activated emotional states.</div>
            <div class="quadrant-examples">
                <span>Angry</span><span>Frustrated</span><span>Dissatisfied</span>
            </div>
        </div>

        <div class="quadrant-card anim d3" style="border-top:2px solid #3a4a5c;">
            <div class="quadrant-label">Quadrant III</div>
            <div class="quadrant-title">Negative Valence · Low Arousal</div>
            <div class="quadrant-desc">Unpleasant and low-activation emotional states.</div>
            <div class="quadrant-examples">
                <span>Sad</span><span>Anxious</span><span>Bored</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="quadrant-card anim d2" style="border-top:2px solid #52b7c4;">
            <div class="quadrant-label">Quadrant I</div>
            <div class="quadrant-title">Positive Valence · High Arousal</div>
            <div class="quadrant-desc">Pleasant and highly activated emotional states.</div>
            <div class="quadrant-examples">
                <span>Joyful</span><span>Amused</span><span>Excited</span>
            </div>
        </div>

        <div class="quadrant-card anim d4" style="border-top:2px solid #3d85c8;">
            <div class="quadrant-label">Quadrant IV</div>
            <div class="quadrant-title">Positive Valence · Low Arousal</div>
            <div class="quadrant-desc">Pleasant and low-activation emotional states.</div>
            <div class="quadrant-examples">
                <span>Relaxed</span><span>Peaceful</span><span>Calm</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider anim d0"></div>', unsafe_allow_html=True)

    # ── DATASET ───────────────────────────────────────────────────────────────
    st.header("About the Dataset")

    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        st.metric("Platform", "Twitter & Facebook")
    with col2:
        st.metric("Period", "2021 – 2025")
    with col3:
        st.metric("Annotators", "10 People")

    st.markdown("""
    <div class="anim d1">
    <p>The dataset used in this study was collected through web scraping from two
    social media platforms — Twitter (X) and Facebook — focusing on publicly
    available Indonesian-language posts related to mental health. Data collection
    covered the period from 2021 to 2025, with a specific focus on three mental
    health categories: anxiety, depression, and attention-deficit/hyperactivity
    disorder (ADHD).</p>

    <p>Each text was manually annotated by 10 trained annotators using the
    <em>Self-Assessment Manikin</em> (SAM) instrument on a 1–9 scale. The annotation
    scores were subsequently normalized to the range of −1 to 1 to ensure
    consistency with the continuous output representation used in the model.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider anim d0"></div>', unsafe_allow_html=True)

    # ── MODEL ARCHITECTURE ────────────────────────────────────────────────────
    st.header("Model Architecture")

    st.markdown("""
    <div class="anim d0">
    <p>The model employed in this study is <code class="inline-code">xlm-roberta-large</code>,
    a multilingual Transformer encoder pretrained on a large-scale cross-lingual corpus using
    a masked language modeling objective. Originally introduced by Conneau et al. (2020),
    XLM-RoBERTa Large consists of 24 Transformer encoder layers with a hidden dimensionality
    of 1,024, a feed-forward size of 4,096, and 16 attention heads, totaling approximately
    560 million parameters. Its multilingual pretraining makes it particularly well-suited
    for processing Indonesian-language social media text.</p>

    <p>The task is formulated as a multi-output regression problem: the model receives
    a tokenized text sequence and produces two continuous scalar outputs representing
    the valence and arousal dimensions, each bounded within the range [−1, 1].
    The full architecture is composed of four main components:</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="arch-step anim d1">
        <div class="arch-step-num">1</div>
        <div class="arch-step-body">
            <h4>Backbone Encoder with Partial Fine-Tuning</h4>
            <p>
                The <code class="inline-code">xlm-roberta-large</code> encoder processes each tokenized
                input sequence — padded or truncated to a fixed maximum length of 128 tokens — and
                produces a contextualized hidden-state matrix of shape [batch, 128, 1,024].
                To prevent catastrophic forgetting of cross-lingual representations and to reduce
                computational cost, the embedding layer and the lower 8 of the 24 encoder layers
                are frozen during training. Only the upper 16 encoder layers are updated via
                gradient descent, allowing the model to adapt to the affective regression task
                while preserving the general multilingual representations acquired during pretraining.
            </p>
        </div>
    </div>

    <div class="arch-step anim d2">
        <div class="arch-step-num">2</div>
        <div class="arch-step-body">
            <h4>Mean Pooling</h4>
            <p>
                Rather than relying solely on the <code class="inline-code">[CLS]</code> token
                representation, mean pooling is applied across all token positions in the last
                hidden state, weighted by the attention mask to exclude padding tokens. This
                operation produces a single dense vector of dimension 1,024 that serves as the
                sentence-level representation. Mean pooling has been shown empirically to yield
                more stable and informative sentence embeddings than the
                <code class="inline-code">[CLS]</code> token alone, particularly for regression
                tasks over variable-length inputs.
            </p>
        </div>
    </div>

    <div class="arch-step anim d3">
        <div class="arch-step-num">3</div>
        <div class="arch-step-body">
            <h4>Regression Head</h4>
            <p>
                The pooled sentence representation is passed through a Dropout layer (p = 0.2)
                before entering a three-stage multilayer perceptron (MLP):
            </p>
            <p style="margin-top:8px;">
                <code class="inline-code">Stage 1:</code> Linear(1,024 → 512) → LayerNorm(512) → GELU → Dropout(0.2)<br>
                <code class="inline-code">Stage 2:</code> Linear(512 → 128) → LayerNorm(128) → GELU → Dropout(0.2)<br>
                <code class="inline-code">Output:</code> Linear(128 → 2)
            </p>
            <p style="margin-top:8px;">
                Layer normalization is applied after each linear projection to stabilize
                activations across mini-batches, while GELU activation provides a smooth,
                non-linear transformation. Dropout at each stage regularizes the network and
                mitigates overfitting. The final linear layer projects the 128-dimensional
                representation to a 2-dimensional output, corresponding to the predicted
                valence and arousal scores respectively.
            </p>
        </div>
    </div>

    <div class="arch-step anim d4">
        <div class="arch-step-num">4</div>
        <div class="arch-step-body">
            <h4>Loss Function and Training Configuration</h4>
            <p>
                Training is supervised using Smooth L1 Loss (Huber Loss), defined as a quadratic
                function for small residuals and a linear function for large ones. This hybrid
                formulation retains the sensitivity of mean squared error near zero while being
                robust to outliers — a desirable property given the subjectivity and annotation
                noise inherent in affective scoring tasks. The loss is computed jointly over
                both the valence and arousal outputs.
            </p>
            <p style="margin-top:8px;">
                The model is optimized using AdamW with a learning rate of 2 × 10⁻⁵ and a
                linear warmup schedule covering the first 10% of training steps. A weight
                decay of 0.01 is applied to all non-bias parameters. Training is conducted
                with a per-device batch size of 16 and mixed-precision computation (fp16)
                enabled to accelerate processing on GPU hardware. Model selection is performed
                using early stopping based on validation loss, with the best checkpoint
                retained as the final model.
            </p>
            <p style="margin-top:8px;">
                The model produces two continuous output values in the range of −1 to 1,
                representing <strong style="color:var(--text-primary);">valence</strong> as
                the first output and
                <strong style="color:var(--text-primary);">arousal</strong> as the second.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)