# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from .geometry import calculate_geometry

def phi_gate_scores(overlaps, mu_ema=None):
    history = {"overlap": overlaps}
    if mu_ema is not None:
        history["mu_ema"] = mu_ema
    return calculate_geometry(history)

def rcod_filter_indices(overlaps,
                        mu_threshold=0.25,
                        keep_flow_fraction=0.1):
    """
    overlaps: array of cosine similarities or overlap scores.
    Returns indices to KEEP.
    """
    novelty = 1.0 - overlaps
    high_mu_mask = novelty >= mu_threshold

    high_mu_idx = np.where(high_mu_mask)[0]
    low_mu_idx = np.where(~high_mu_mask)[0]

    k_flow = max(1, int(len(low_mu_idx) * keep_flow_fraction))
    flow_sample = np.random.choice(low_mu_idx, size=k_flow, replace=False)

    keep_idx = np.sort(np.concatenate([high_mu_idx, flow_sample]))
    return keep_idx
