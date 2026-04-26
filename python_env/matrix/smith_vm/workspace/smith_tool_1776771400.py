# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation: Informational Jerk Stability
------------------------------------------------------
Checks that the Jerk calculation from HSA unified‑memory data
obeys the stability bound derived in the Engine's analysis.
"""

import numpy as np

def shannon_entropy(probs: np.ndarray) -> float:
    """S_h = -∑ p_i log p_i, safe for zeros."""
    p = probs[probs > 0]
    return -np.sum(p * np.log(p))

def compute_jerk_sh(Sh: np.ndarray) -> np.ndarray:
    """
    Finite‑difference third derivative (step = 1):
    J[n] = Sh[n] - 3*Sh[n-1] + 3*Sh[n-2] - Sh[n-3]
    Returns array same length as Sh (first three entries set to NaN).
    """
    J = np.full_like(Sh, np.nan, dtype=float)
    J[3:] = Sh[3:] - 3*Sh[2:-1] + 3*Sh[1:-2] - Sh[0:-3]
    return J

def threshold_theta(lambd: float, I0: float, gDelta: float) -> float:
    """
    Θ = (λ I0^2 / 4π) * (1 + 3 gΔ^2 / 4π)
    """
    return (lambd * I0**2) / (4 * np.pi) * (1 + 3 * gDelta**2 / (4 * np.pi))

def validate_jerk(
    time: np.ndarray,
    access_counts: np.ndarray,   # shape (T, Nblocks) – raw access frequencies per bin
    lambd: float = 1.0,
    I0: float = 1.0,
    gDelta: float = 0.5,
    Jmax: float = 1e-2,
    var_window: int = 50
) -> dict:
    """
    Returns a dict with pass/fail flags and diagnostic values.
    """
    # 1️⃣ Estimate probabilities per time bin
    probs = access_counts / access_counts.sum(axis=1, keepdims=True)
    # 2️⃣ Compute Shannon entropy time series
    Sh = np.array([shannon_entropy(p) for p in probs])
    # 3️⃣ Jerk via finite differences
    J = compute_jerk_sh(Sh)
    # 4️⃣ Boundedness test (ignore NaNs)
    J_finite = J[~np.isnan(J)]
    bounded = np.all(np.abs(J_finite) < Jmax) if J_finite.size > 0 else False
    # 5️⃣ Variance over sliding window
    if len(J_finite) >= var_window:
        var_Js = np.array([
            np.var(J_finite[i:i+var_window])
            for i in range(len(J_finite)-var_window+1)
        ])
        sigma2 = np.max(var_Js)   # conservative: use worst‑case window
    else:
        sigma2 = np.var(J_finite) if J_finite.size > 1 else 0.0
    # 6️⃣ Theoretical threshold
    Theta = threshold_theta(lambd, I0, gDelta)
    stable_var = sigma2 <= Theta
    # 7️⃣ Overall pass
    passed = bounded and stable_var
    return {
        "Shannon_entropy": Sh,
        "Jerk": J,
        "Jerk_bounded": bounded,
        "Jerk_max_abs": np.nanmax(np.abs(J)),
        "Jerk_variance": sigma2,
        "Theta_threshold": Theta,
        "Variance_within_Theta": stable_var,
        "Overall_PASS": passed
    }

# ----------------------------------------------------------------------
# Example usage with the Engine's synthetic data: S_h(t) = 10 + sin(0.1t)
if __name__ == "__main__":
    T = 200
    t = np.linspace(0, 20*np.pi, T)          # enough periods to see pattern
    Sh_example = 10 + np.sin(0.1 * t)        # entropy-like signal
    # Convert entropy to pseudo‑access counts (monotonic transform for demo)
    # We need a probability distribution; use softmax over a fixed set of bins.
    Nblocks = 5
    # Create a base probability vector that varies with Sh_example
    base = np.exp(Sh_example[:, None])       # shape (T,1)
    base = np.tile(base, (1, Nblocks))       # same across blocks for simplicity
    # Add small random fluctuations to avoid degenerate distribution
    rng = np.random.default_rng(seed=42)
    access = base + rng.normal(scale=0.1, size=base.shape)
    access = np.clip(access, a_min=1e-8, a_max=None)  # ensure positivity

    result = validate_jerk(
        time=t,
        access_counts=access,
        lambd=1.0,
        I0=1.0,
        gDelta=0.5,
        Jmax=1e-2,
        var_window=30
    )
    print("=== Omega Protocol Jerk Validation ===")
    for k, v in result.items():
        if isinstance(v, np.ndarray):
            print(f"{k}: shape {v.shape}, first 5 = {v[:5]}")
        else:
            print(f"{k}: {v}")