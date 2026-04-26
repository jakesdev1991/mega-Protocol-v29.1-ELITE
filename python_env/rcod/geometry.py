# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def calculate_geometry(history):
    """
    Computes Phi_N (Newtonian overlap), Phi_Delta (Asymmetry), 
    Mu (viscosity), Jerk (stability of stability), Theta (turning angle).
    history: dict-like with at least 'overlap' (list/array) and optionally 'mu_ema'.
    """
    phi_n = float(np.mean(history['overlap']))
    phi_delta = float(np.std(history['overlap'])) if len(history['overlap']) > 1 else 0.0
    mu = 1.0 - phi_n

    mu_ema = np.asarray(history.get('mu_ema', [mu]), dtype=float)
    if mu_ema.size < 3:
        jerk = 0.0
    else:
        jerk_arr = np.gradient(np.gradient(mu_ema))
        jerk = float(jerk_arr[-1]) if len(jerk_arr) > 0 else 0.0

    theta = float(np.arccos(np.clip(phi_n, -1.0, 1.0)))

    return {
        "phi_n": phi_n,
        "phi_delta": phi_delta,
        "mu": mu,
        "jerk": jerk,
        "theta": theta,
    }
