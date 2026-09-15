import streamlit as st
import torch
import shap
import numpy as np
import matplotlib.pyplot as plt

from preprocessing import preprocess
from model_loader import load_model, load_norm_dict, VALENCE_INDEX, AROUSAL_INDEX


def filter_shap(sv):
    """Filter special tokens dan set feature_names supaya label tampil sebagai token."""
    special = {'<s>', '</s>', '<pad>', ''}
    mask = [t not in special for t in sv.data]
    tokens = np.array(sv.data)[mask]
    return shap.Explanation(
        values        = sv.values[mask],
        base_values   = sv.base_values,
        data          = tokens,
        feature_names = tokens.tolist(),
    )


def show():
    st.markdown("""
    <div class="anim d0">
        <div style="margin-bottom:6px;">
            <span class="badge">Live Demo</span>
        </div>
        <h2 style="margin:0 0 8px;">Try the Valence–Arousal Model</h2>
        <p style="margin:0;">
            Enter an Indonesian text below, and the fine-tuned XLM-RoBERTa model will
            predict its <strong>Valence</strong> and <strong>Arousal</strong> scores
            (ranging from &minus;1 to 1). We also use <strong>SHAP</strong> to explain
            how each word contributes to the final score.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider anim d1"></div>', unsafe_allow_html=True)

    try:
        with st.spinner('Loading model into memory... (This may take a moment)'):
            tokenizer, model = load_model()
    except Exception as e:
        st.error(f"Error loading model: {e}\nPlease ensure the './model' folder exists and contains all required files.")
        return

    norm_dict, noise_set = load_norm_dict()

    user_input = st.text_area(
        "Input Text:",
        height=100,
        placeholder="Describe your thoughts, feelings, or experiences here..."
    )

    if st.button("Predict & Explain", type="primary"):
        if user_input.strip() == "":
            st.warning("Please enter some text first.")
        else:
            cleaned_input = preprocess(user_input, norm_dict, noise_set)

            with st.spinner("Analyzing text and generating SHAP explanations..."):
                inputs = tokenizer(
                    cleaned_input,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                )
                with torch.no_grad():
                    outputs = model(**inputs)

                logits = outputs["logits"][0].tolist()
                valence_score = logits[VALENCE_INDEX]
                arousal_score = logits[AROUSAL_INDEX]

                if valence_score >= 0 and arousal_score >= 0:
                    quad_name  = "Quadrant I (Positive Valence, High Arousal)"
                    quad_color = "normal"
                    quad_desc  = "Pleasant and intense emotional states (e.g., Happy, Excited)."
                elif valence_score < 0 and arousal_score >= 0:
                    quad_name  = "Quadrant II (Negative Valence, High Arousal)"
                    quad_color = "inverse"
                    quad_desc  = "Unpleasant and intense emotional states (e.g., Angry, Anxious)."
                elif valence_score < 0 and arousal_score < 0:
                    quad_name  = "Quadrant III (Negative Valence, Low Arousal)"
                    quad_color = "error"
                    quad_desc  = "Unpleasant and passive emotional states (e.g., Sad, Depressed)."
                else:
                    quad_name  = "Quadrant IV (Positive Valence, Low Arousal)"
                    quad_color = "off"
                    quad_desc  = "Pleasant but calm emotional states (e.g., Calm, Relaxed)."

                def predict_fn(texts):
                    texts_list = [preprocess(str(x), norm_dict, noise_set) for x in texts]
                    inps = tokenizer(texts_list, return_tensors="pt", truncation=True, padding=True, max_length=512)
                    with torch.no_grad():
                        outs = model(**inps)
                    return outs["logits"].numpy()

                # FIX: pakai masker level-kata (regex split), bukan tokenizer
                # SentencePiece langsung. Ini supaya SHAP tidak memecah kata
                # jadi subword (mis. "anxious" -> "an"/"xi"/"ous"), dan hasilnya
                # tetap per-kata utuh untuk teks Indonesia maupun Inggris.
                masker    = shap.maskers.Text(r"\W+")
                explainer = shap.Explainer(predict_fn, masker)

                shap_values = explainer([cleaned_input])

            # ── SEMUA RENDER DI LUAR SPINNER ──────────────────────────────────

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="anim d0">
                <div style="margin-bottom:6px;"><span class="badge">Output</span></div>
                <h3 style="margin:0 0 4px;">📊 Prediction Results</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Valence Score", value=f"{valence_score:.4f}")
            with col2:
                st.metric(label="Arousal Score", value=f"{arousal_score:.4f}")

            if quad_color == "normal":    st.info(f"**{quad_name}**\n\n{quad_desc}")
            elif quad_color == "inverse": st.warning(f"**{quad_name}**\n\n{quad_desc}")
            elif quad_color == "error":   st.error(f"**{quad_name}**\n\n{quad_desc}")
            else:                         st.success(f"**{quad_name}**\n\n{quad_desc}")

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="anim d1">
                <div style="margin-bottom:6px;"><span class="badge">Explainability</span></div>
                <h3 style="margin:0 0 4px;">🧠 SHAP Text Explanation</h3>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("❓ How to read this SHAP plot?", expanded=True):
                st.markdown("""
                This *waterfall plot* breaks down the model's prediction word by word:
                * **X-axis (Bottom):** Represents the range of the model's prediction score.
                * **$E[f(x)]$ (Base Value):** The baseline (average) score before the model processes any words.
                * **$f(x)$ (Output Value):** The final prediction score after all words are taken into account (same as the score shown above).
                * **Red color:** The word **increases** the prediction score (more positive).
                * **Blue color:** The word **decreases** the prediction score (more negative).
                * **Numbers next to each word:** Indicate how much each word contributes to pushing the final score up or down.
                """)

            st.info(f"📝 **Analyzed Text:** {user_input.strip()}")

            # --- SHAP PLOTS ---
            col_shap1, col_shap2 = st.columns(2)

            rcparams = {
                'text.color':       '#1a1a1a',
                'axes.labelcolor':  '#4a5568',
                'xtick.color':      '#4a5568',
                'ytick.color':      '#4a5568',
                'axes.edgecolor':   '#e2e8f0',
                'figure.facecolor': '#ffffff',
            }

            with col_shap1:
                st.markdown("#### Valence SHAP Value")
                filtered_sv = filter_shap(shap_values[0, :, VALENCE_INDEX])
                fig_v, ax_v = plt.subplots(figsize=(6, 4))
                fig_v.patch.set_facecolor('#ffffff')
                ax_v.set_facecolor('#f5f7fb')
                plt.rcParams.update(rcparams)
                shap.plots.waterfall(filtered_sv, show=False, max_display=10)
                st.pyplot(fig_v)
                plt.clf()

            with col_shap2:
                st.markdown("#### Arousal SHAP Value")
                filtered_sv = filter_shap(shap_values[0, :, AROUSAL_INDEX])
                fig_a, ax_a = plt.subplots(figsize=(6, 4))
                fig_a.patch.set_facecolor('#ffffff')
                ax_a.set_facecolor('#f5f7fb')
                plt.rcParams.update(rcparams)
                shap.plots.waterfall(filtered_sv, show=False, max_display=10)
                st.pyplot(fig_a)
                plt.clf()