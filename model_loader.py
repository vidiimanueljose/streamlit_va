"""
model_loader.py — single source of truth untuk loading model & normalization dict.
"""

import streamlit as st
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

from preprocessing import load_normalization_dict
from modeling_xlmr_va import XLMRRegression


# ── OUTPUT-INDEX CONSTANTS ─────────────────────────────────────────────────────

VALENCE_INDEX = 0
AROUSAL_INDEX = 1


# ── CACHED LOADERS ─────────────────────────────────────────────────────────────

@st.cache_resource
def load_model():
    """Download and load the private Hugging Face model."""

    model_path = snapshot_download(
        repo_id="josevidiimanuel/va_model_xlm_roberta",
        token=st.secrets["HF_TOKEN"]
    )

    tokenizer = AutoTokenizer.from_pretrained(model_path)

    model = XLMRRegression.load_pretrained_custom(model_path)

    model.eval()

    return tokenizer, model


@st.cache_resource
def load_norm_dict(csv_path: str = "./file/normalization.csv"):
    """Load normalization dict + noise set sekali, cache selamanya."""

    return load_normalization_dict(csv_path)