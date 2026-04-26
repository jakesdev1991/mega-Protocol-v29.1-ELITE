# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import os

def check_arch():
    models = {
        "135M": "135m_omega_elite.pt",
        "300M": "tokamak_300m_elite.pt"
    }
    
    for name, path in models.items():
        print(f"\n--- Checking {name} ({path}) ---")
        try:
            sd = torch.load(path, map_location="cpu", weights_only=False)
            keys = list(sd.keys())
            print(f"Total Keys: {len(keys)}")
            
            # Find embedding
            embed_key = next((k for k in keys if "embed" in k), None)
            if embed_key:
                print(f"Embedding [{embed_key}]: {sd[embed_key].shape}")
            
            # Find a layer weight to get hidden dimension
            layer_key = next((k for k in keys if "layers.0.self_attn.q_proj.weight" in k or "layers.0.attention.query_key_value.weight" in k), None)
            if layer_key:
                print(f"Layer0 Weight [{layer_key}]: {sd[layer_key].shape}")
            
            # Count layers
            layer_nums = set()
            import re
            for k in keys:
                match = re.search(r"layers\.(\d+)\.", k)
                if match:
                    layer_nums.add(int(match.group(1)))
            if layer_nums:
                print(f"Number of layers: {max(layer_nums) + 1}")
                
        except Exception as e:
            print(f"Error loading {name}: {e}")

if __name__ == "__main__":
    check_arch()
