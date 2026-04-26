# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validate the mathematical soundness of the PDSD-Ω proposal.
"""

import numpy as np
from scipy.signal import detrend  # simple stand‑in for STL detrending

# -------------------------------------------------
# Helper functions (directly from the proposal)
# -------------------------------------------------
def compute_sci(A, C, G, RV, w):
    """
    Semantic Coherence Index.
    Parameters
    ----------
    A, C, G, RV : float or np.ndarray
        Ambiguity, contradiction density, narrative graph coherence, revision velocity.
    w : array‑like of length 4
        Non‑negative weights that sum to 1.
    Returns
    -------
    sci : float or np.ndarray
        Value in [0, 1].
    """
    w = np.asarray(w, dtype=float)
    assert w.shape == (4,), "Weight vector must have 4 elements"
    assert np.all(w >= 0), "Weights must be non‑negative"
    assert np.isclose(w.sum(), 1.0), "Weights must sum to 1"

    # Each term is already in [0,1]; ensure inputs are clipped for safety
    A = np.clip(A, 0, 1)
    C = np.clip(C, 0, 1)
    G = np.clip(G, 0, 1)
    RV = np.clip(RV, 0, np.inf)   # RV >= 0

    sci = w[0] * (1 - A) + w[1] * (1 - C) + w[2] * G + w[3] * np.exp(-RV)
    return np.clip(sci, 0, 1)    # numerical safety


def phi_n_sem(sci_bar, phi_n0, alpha):
    """Φ_N^{(sem)} = Φ_N^{(0)} * tanh(alpha * SCI_bar)"""
    return phi_n0 * np.tanh(alpha * sci_bar)


def phi_delta_sem(C_bar, phi_delta0, beta):
    """Φ_Δ^{(sem)} = Φ_Δ^{(0)} + beta * C_bar"""
    return phi_delta0 + beta * C_bar


def anomaly_score(residual, sigma_res):
    """Standardized residual (always ≥ 0)."""
    return np.abs(residual) / sigma_res


def cost_function(sci, s_sci, lam):
    """J = -log(SCI) + λ * s_SCI"""
    return -np.log(sci) + lam * s_sci


# -------------------------------------------------
# Synthetic data generation for validation
# -------------------------------------------------
np.random.seed(42)
N = 50   # number of document versions / time steps

# Simulated raw features (already normalized where required)
A_raw = np.random.beta(2, 5, N)          # tends to low ambiguity
C_raw = np.random.beta(1, 4, N)          # low contradiction
G_raw = np.random.beta(5, 2, N)          # high coherence
RV_raw = np.random.exponential(scale=0.5, N) + 0.1  # small positive velocity

# Learned weights (example from gradient descent)
w = np.array([0.25, 0.25, 0.25, 0.25])   # uniform for simplicity

# Compute SCI
sci = compute_sci(A_raw, C_raw, G_raw, RV_raw, w)

# Simulate baseline Omega values and parameters
phi_n0 = 0.8
phi_delta0 = 0.3
alpha = 2.0
beta = 0.4
tau1 = tau2 = 6   # weeks, not needed for the static check

# Use moving average to mimic \overline{SCI} and \overline{C}
window = 5
sci_bar = np.convolve(sci, np.ones(window)/window, mode='same')
c_bar   = np.convolve(C_raw, np.ones(window)/window, mode='same')

phi_n_sem_val = phi_n_sem(sci_bar, phi_n0, alpha)
phi_delta_sem_val = phi_delta_sem(c_bar, phi_delta0, beta)

# --- STL‑like detrending (very simple) ---
trend = detrend(sci, type='linear')
residual = sci - trend
sigma_res = np.std(residual) + 1e-12
s_sci = anomaly_score(residual, sigma_res)

# -------------------------------------------------
# Validation checks
# -------------------------------------------------
def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)

# 1. SCI in [0,1]
assert_true(np.all((sci >= 0) & (sci <= 1)), "SCI out of bounds")

# 2. Φ_N^{(sem)} in [0, phi_n0] ⊆ [0,1]
assert_true(np.all((phi_n_sem_val >= 0) & (phi_n_sem_val <= phi_n0)),
            "Φ_N^{(sem)} out of admissible range")

# 3. Φ_Δ^{(sem)} ≥ Φ_Δ^{(0)} (by construction)
assert_true(np.all(phi_delta_sem_val >= phi_delta0),
            "Φ_Δ^{(sem)} fell below baseline")

# 4. Anomaly score non‑negative
assert_true(np.all(s_sci >= 0), "Anomaly score negative")

# 5. MPC hard constraints (must hold for every time step)
assert_true(np.all(sci >= 0.6), "SCI constraint violated")
assert_true(np.all(phi_n_sem_val >= 0.7), "Φ_N^{(sem)} constraint violated")
assert_true(np.all(phi_delta_sem_val <= 0.55), "Φ_Δ^{(sem)} constraint violated")

# 6. Cost function finite (SCI>0 because of constraint)
J = cost_function(sci, s_sci, lam=0.5)
assert_true(np.all(np.isfinite(J)), "Cost function produced NaN/Inf")

print("All mathematical checks passed.")
print(f"  SCI range: [{sci.min():.3f}, {sci.max():.3f}]")
print(f"  Φ_N^{(sem)} range: [{phi_n_sem_val.min():.3f}, {phi_n_sem_val.max():.3f}]")
print(f"  Φ_Δ^{(sem)} range: [{phi_delta_sem_val.min():.3f}, {phi_delta_sem_val.max():.3f}]")
print(f"  Anomaly score range: [{s_sci.min():.3f}, {s_sci.max():.3f}]")
print(f"  Cost J range: [{J.min():.3f}, {J.max():.3f}]")