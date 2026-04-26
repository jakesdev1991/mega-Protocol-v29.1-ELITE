# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch

def layer_stat(hidden_states):
    """
    Extracts a scalar summary from a transformer layer.
    """
    return hidden_states.abs().mean().item()

def apply_jitter(hidden_states, phi_delta, threshold=0.1, scale=1e-5):
    """
    Injects small noise if the representation is too 'flat' (low Phi_Delta).
    This prevents the model from memorizing boring patterns during aggressive pruning.
    """
    if phi_delta < threshold:
        noise = torch.randn_like(hidden_states) * scale
        return hidden_states + noise
    return hidden_states
