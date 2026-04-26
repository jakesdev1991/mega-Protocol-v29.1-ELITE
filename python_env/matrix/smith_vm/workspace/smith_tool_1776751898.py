# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Informational Jerk Validator
------------------------------------------
Given a time series of memory‑access probabilities, this script:
  * Computes Shannon conditional entropy S_h(t)
  * Estimates the third time derivative (informational jerk) J_I
  * Tests boundedness against a user‑provided threshold Θ
  * Enforces the narrative‑only output by printing a single paragraph.
"""

import numpy as np

def shannon_entropy(p: np.ndarray) -> float:
    """Conditional entropy for a probability vector p (avoids log(0))."""
    p = np.asarray(p, dtype=float)
    p = p[p > 0]               # drop zero probabilities
    return -np.sum(p * np.log(p))

def compute_jerk(S: np.ndarray, dt: float) -> np.ndarray:
    """
    Finite‑difference approximation of the third derivative:
        J[n] = (S[n] - 3*S[n-1] + 3*S[n-2] - S[n-3]) / dt**3
    Returns an array aligned with S[3:].
    """
    if len(S) < 4:
        raise ValueError("Need at least 4 samples to compute jerk.")
    J = (S[3:] - 3*S[2:-1] + 3*S[1:-2] - S[:-3]) / (dt**3)
    return J

def stability_check(J: np.ndarray, threshold: float) -> bool:
    """Returns True if |J| < threshold for all samples."""
    return np.all(np.abs(J) < threshold)

def main():
    # ----- Simulated HSA unified‑memory access data -----
    # Suppose we have 5 memory blocks; we generate a smooth periodic
    # access pattern plus small random noise.
    np.random.seed(42)
    t = np.linspace(0, 100, 1000)          # time axis
    dt = t[1] - t[0]

    # Base frequencies (probabilities) for each block
    freqs = np.array([0.4, 0.2, 0.15, 0.15, 0.1])
    # Modulate with a low‑frequency sinusoid to create entropy variation
    mod = 1 + 0.3 * np.sin(0.05 * t)[:, None]   # shape (N,1)
    raw = freqs * mod
    # Normalize each time step to a proper probability distribution
    p_t = raw / raw.sum(axis=1, keepdims=True)

    # ----- Compute entropy time series -----
    S_h = np.array([shannon_entropy(p_t[i]) for i in range(len(t))])

    # ----- Compute informational jerk -----
    J_I = compute_jerk(S_h, dt)

    # ----- Stability threshold (example value) -----
    # In a real deployment Θ would be derived from ξ_Δ → ∞ condition.
    Theta = 1e-4   # arbitrary but illustrative

    stable = stability_check(J_I, Theta)

    # ----- Narrative‑only output (Omega Protocol compliant) -----
    msg = (
        f"Over the observation window the informational jerk ranged "
        f"from {J_I.min():.3e} to {J_I.max():.3e} (units s⁻³). "
        f"The stability threshold is Θ = {Theta:.3e}. "
        f"The system is {'STABLE' if stable else 'UNSTABLE'} with respect "
        f"to the informational jerk criterion."
    )
    print(msg)

if __name__ == "__main__":
    main()