# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class LLMRegime:
    """
    Manages multiple local LLM instantiations for the Omega Protocol.
    Tiers: 135M (Edge), 300M (Tokamak/Physicist), 1.7B (General Reasoner)
    """
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.tokenizers = {}
        self.paths = {
            "edge": "/home/jake/Downloads/training/base_model",
            "physicist": "/home/jake/Downloads/training/tokamak_300m_training/checkpoint-50000",
            "reasoner": "/home/jake/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM2-1.7B/snapshots/effd688a12921b4cc83e3312b6feb579f70f9c71"
        }

    def load_tier(self, tier):
        if tier not in self.paths:
            print(f"❌ Unknown tier: {tier}")
            return
        
        if tier in self.models:
            return self.models[tier], self.tokenizers[tier]

        print(f"✦ [Regime] Loading {tier.upper()} tier manifold into {self.device}...")
        path = self.paths[tier]
        
        self.tokenizers[tier] = AutoTokenizer.from_pretrained(path)
        self.models[tier] = AutoModelForCausalLM.from_pretrained(
            path, 
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
            device_map=self.device
        )
        return self.models[tier], self.tokenizers[tier]

    def chat(self, tier, prompt, max_new_tokens=128):
        model, tokenizer = self.load_tier(tier)
        inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    regime = LLMRegime()
    print(f"✦ Regime Manager initialized on {regime.device}")
