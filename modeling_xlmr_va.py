"""
modeling_xlmr_va.py

Custom model definition untuk Valence-Arousal Regression di atas XLM-RoBERTa.
Arsitektur ini SAMA PERSIS dengan yang dipakai di notebook training
(class XLMRRegression), cuma dibungkus supaya:

1. config.json yang dihasilkan benar-benar merepresentasikan arsitektur
   (bukan config bawaan backbone doang).
2. Ada save_pretrained() / load_pretrained() sendiri, karena model ini
   BUKAN turunan transformers.PreTrainedModel jadi gak bisa pakai
   AutoModelForSequenceClassification.from_pretrained().

PENTING: file ini WAJIB ikut di-upload/disertakan setiap kali model
di-share (ke Hugging Face, ke aplikasi Streamlit, dll). Tanpa file ini,
config.json + weights aja gak cukup buat merekonstruksi modelnya.
"""

import json
import os

import torch
import torch.nn as nn
from safetensors.torch import save_file, load_file
from transformers import AutoModel, AutoConfig


CONFIG_FILENAME = "config.json"
WEIGHTS_FILENAME = "model.safetensors"


class XLMRRegression(nn.Module):
    def __init__(
        self,
        model_name: str = "xlm-roberta-large",
        freeze_embeddings: bool = True,
        freeze_n_layers: int = 8,
        hidden_dims: list = [512, 128],
        num_labels: int = 2,
        dropout: float = 0.2,
        load_pretrained_backbone: bool = True,
    ):
        super().__init__()

        # Disimpan supaya bisa di-dump ke config.json apa adanya
        self.init_args = {
            "model_name": model_name,
            "freeze_embeddings": freeze_embeddings,
            "freeze_n_layers": freeze_n_layers,
            "hidden_dims": hidden_dims,
            "num_labels": num_labels,
            "dropout": dropout,
        }

        # Backbone
        # load_pretrained_backbone=False -> cuma download config.json (kecil, KB),
        # BUKAN bobot pretrained (ratusan MB - GB). Dipakai kalau kita toh mau
        # langsung timpa bobotnya pakai state_dict lokal (lihat load_pretrained_custom),
        # jadi download bobot pretrained di sini cuma buang-buang bandwidth & waktu.
        if load_pretrained_backbone:
            self.roberta = AutoModel.from_pretrained(model_name)
        else:
            backbone_config = AutoConfig.from_pretrained(model_name)
            self.roberta = AutoModel.from_config(backbone_config)
        backbone_hidden = self.roberta.config.hidden_size

        if freeze_embeddings:
            for p in self.roberta.embeddings.parameters():
                p.requires_grad = False

        if freeze_n_layers > 0:
            for layer in self.roberta.encoder.layer[:freeze_n_layers]:
                for p in layer.parameters():
                    p.requires_grad = False

        self.dropout = nn.Dropout(dropout)

        # Regression head (persis notebook: Linear -> LayerNorm -> GELU -> Dropout, berulang)
        layers = []
        in_dim = backbone_hidden
        for h in hidden_dims:
            layers += [nn.Linear(in_dim, h), nn.LayerNorm(h), nn.GELU(), nn.Dropout(dropout)]
            in_dim = h
        layers.append(nn.Linear(in_dim, num_labels))
        self.regressor = nn.Sequential(*layers)

        self.loss_fn = nn.SmoothL1Loss()

        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"Total parameter    : {total:,}")
        print(f"Trainable parameter: {trainable:,}")
        print(f"Frozen             : {total - trainable:,}")

    def mean_pooling(self, last_hidden_state, attention_mask):
        mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        summed = torch.sum(last_hidden_state * mask, dim=1)
        counts = torch.clamp(mask.sum(dim=1), min=1e-9)
        return summed / counts

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.mean_pooling(outputs.last_hidden_state, attention_mask)
        logits = self.regressor(self.dropout(pooled))

        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels.float())

        return {"loss": loss, "logits": logits}

    # ------------------------------------------------------------------
    # Save / Load helpers (pengganti save_pretrained/from_pretrained HF)
    # ------------------------------------------------------------------
    def save_pretrained_custom(self, save_dir: str):
        os.makedirs(save_dir, exist_ok=True)

        with open(os.path.join(save_dir, CONFIG_FILENAME), "w") as f:
            json.dump(self.init_args, f, indent=2)

        save_file(self.state_dict(), os.path.join(save_dir, WEIGHTS_FILENAME))
        print(f"Model tersimpan di: {save_dir}")
        print(f"  - {CONFIG_FILENAME} (arsitektur asli, bukan config bawaan backbone)")
        print(f"  - {WEIGHTS_FILENAME}")
        print("  Jangan lupa upload modeling_xlmr_va.py ini juga bareng foldernya!")

    @classmethod
    def load_pretrained_custom(cls, save_dir: str, device: str = "cpu"):
        with open(os.path.join(save_dir, CONFIG_FILENAME), "r") as f:
            config = json.load(f)

        # load_pretrained_backbone=False: gak perlu download bobot pretrained
        # dari Hugging Face, karena baris di bawah bakal langsung menimpanya
        # dengan state_dict lokal kamu.
        model = cls(**config, load_pretrained_backbone=False)

        weights_path = os.path.join(save_dir, WEIGHTS_FILENAME)
        bin_path = os.path.join(save_dir, "pytorch_model.bin")

        if os.path.exists(weights_path):
            state_dict = load_file(weights_path)
        elif os.path.exists(bin_path):
            state_dict = torch.load(bin_path, map_location="cpu")
        else:
            raise FileNotFoundError(f"Gak ketemu weights di {save_dir}")

        model.load_state_dict(state_dict)
        model.to(device)
        model.eval()
        return model