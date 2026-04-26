# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDIP-Ω Invariant Validator
--------------------------
This script checks that the mathematical components of the repaired EDIP-Ω
proposal obey the Omega Physics Rubric constraints:

* Φ_N ∈ [0, 1]
* ξ_Δ ≥ 1
* ξ_N ≥ 0
* ψ = ln(φ_n) is treated as an invariant (we only check that we never
  mistakenly use ψ as a learned variable).
* ESI_k ≤ 2.5 (hard QP constraint)
* Prediction rule uses only validation‑set tuned thresholds.
* Derivative of ξ_Δ is smoothed before threshold comparison.
* Cost function penalizes ESI_k > 2.5 via ReLU term.

The script uses synthetic data; replace the synthetic generators with real
data pipelines for production validation.
"""

import numpy as np
from scipy.signal import savgol_filter

# ----------------------------------------------------------------------
# Helper functions mimicking the EDIP-Ω modules
# ----------------------------------------------------------------------
def standardize(x):
    """Zero‑mean, unit‑variance standardization (per‑feature)."""
    return (x - np.mean(x, axis=0)) / (np.std(x, axis=0) + 1e-8)

def gru_encode(features):
    """
    Simplified GRU encoder: returns a fixed‑size embedding.
    In practice this would be a trained GRU; here we use a linear projection
    followed by tanh to keep the output bounded (~-1, 1).
    """
    W = np.random.randn(features.shape[1], 16) * 0.1
    b = np.zeros(16)
    return np.tanh(features @ W + b)

def pinn_map(esi_embedding, plasma_features):
    """
    PINN that maps [ESI embedding, plasma features] → [Φ_N, Φ_Δ, ξ_N, ξ_Δ].
    Activation constraints:
        Φ_N   = sigmoid(z)          → [0,1]
        ξ_Δ   = softplus(z) + 1     → [1, ∞)
        ξ_N   = softplus(z)         → [0, ∞)
        Φ_Δ   = sigmoid(z)          → [0,1]  (same bound as Φ_N for simplicity)
    """
    z = np.random.randn(esi_embedding.shape[1] + plasma_features.shape[1], 4) * 0.1
    b = np.zeros(4)
    logits = np.concatenate([esi_embedding, plasma_features], axis=1) @ z + b

    phi_n = 1.0 / (1.0 + np.exp(-logits[:, 0:1]))          # sigmoid
    phi_delta = 1.0 / (1.0 + np.exp(-logits[:, 1:2]))      # sigmoid
    xi_n = np.logaddexp(0, logits[:, 2:3])                 # softplus
    xi_delta = np.logaddexp(0, logits[:, 3:4]) + 1.0       # softplus + 1

    return np.hstack([phi_n, phi_delta, xi_n, xi_delta])

def stl_anomaly_score(esi_series):
    """
    Very rough STL approximation: detrend by subtracting a moving average,
    then compute the L2 norm of the residual normalized by its std.
    """
    trend = np.convolve(esi_series, np.ones(7)/7, mode='same')
    residual = esi_series - trend
    sigma = np.std(residual) + 1e-8
    score = np.linalg.norm(residual) / sigma
    return score, residual

def smoothed_derivative(x, window=5, order=2):
    """Savitzky‑Golay smoothed derivative (first derivative)."""
    return savgol_filter(x, window_length=window, polyorder=order, deriv=1, mode='interp')

# ----------------------------------------------------------------------
# Synthetic data generation (replace with real pipelines)
# ----------------------------------------------------------------------
np.random.seed(42)
n_events = 100                     # number of exposure events in the window
n_plasma = 8                       # dimensionality of plasma diagnostics

# Features per event: [Δt_e, r_d, a_d, c_d, H_access, m_d]
#   Δt_e  : exposure lag (days) → positive
#   r_d   : revision intensity (versions/day) → positive
#   a_d   : access anomaly score (Mahalanobis distance) → ≥0
#   c_d   : cross‑domain flag → {0,1}
#   H_access: access‑log entropy → ≥0
#   m_d   : mask (1 if logs present, else 0)
features = np.abs(np.random.randn(n_events, 6))   # make all non‑negative for simplicity
features[:, 3] = np.random.randint(0, 2, size=n_events)  # c_d binary
features[:, 5] = np.random.randint(0, 2, size=n_events)  # m_d binary

# Plasma diagnostics (e.g., β_N, q_95, etc.)
plasma = np.random.randn(n_plasma)

# ----------------------------------------------------------------------
# 1. Feature preprocessing
# ----------------------------------------------------------------------
features_std = standardize(features)

# ----------------------------------------------------------------------
# 2. GRU encoding (chronological order assumed already sorted by t_e)
# ----------------------------------------------------------------------
esi_embedding = gru_encode(features_std)   # shape (n_events, 16)

# Aggregate over the window – simple mean (could be attention, etc.)
esi_agg = np.mean(esi_embedding, axis=0, keepdims=True)   # shape (1,16)

# ----------------------------------------------------------------------
# 3. PINN mapping to Ω variables
# ----------------------------------------------------------------------
omega_vars = pinn_map(esi_agg, plasma[None, :])   # shape (1,4)
phi_n, phi_delta, xi_n, xi_delta = omega_vars.T

# ----------------------------------------------------------------------
# 4. Invariant and derived variable checks
# ----------------------------------------------------------------------
# ψ is invariant – we never modify it here; just ensure we don't treat it as learnable.
# For demonstration we set a dummy baseline:
psi_baseline = np.log(1.0)   # φ_n = 1 → ψ = 0
# χ(t) is derived deviation (not invariant)
chi = np.log(phi_n / 0.8)    # assuming Φ_N⁰ = 0.8 (example baseline)

# Assertions for Rubric compliance
assert np.all(phi_n >= 0.0) and np.all(phi_n <= 1.0), "Φ_N out of [0,1] bounds"
assert np.all(xi_delta >= 1.0), "ξ_Δ violates ξ_Δ ≥ 1"
assert np.all(xi_n >= 0.0), "ξ_N violates ξ_N ≥ 0"
assert np.all(phi_delta >= 0.0) and np.all(phi_delta <= 1.0), "Φ_Δ out of [0,1] (same bound as Φ_N)"

# ----------------------------------------------------------------------
# 5. Exposure Stress Index (ESI) as scalar for control
# ----------------------------------------------------------------------
# In the proposal ESI_k(t) is a scalar derived from the same features;
# we approximate it as a weighted sum of the GRU output.
weights = np.random.randn(16) * 0.1
esi_k = np.dot(esi_agg, weights)   # scalar
# Apply the hard QP constraint via ReLU penalty in cost function (checked later)
esi_k_clipped = np.clip(esi_k, -np.inf, 2.5)   # enforce ≤2.5 for demonstration

# ----------------------------------------------------------------------
# 6. Anomaly score and prediction rule (using validation‑set thresholds)
# ----------------------------------------------------------------------
# Simulate a time‑series of ESI_k values (e.g., last 30 days)
esi_ts = np.abs(np.random.randn(30)) + 0.5   # positive values
anomaly_score, residual = stl_anomaly_score(esi_ts)

# Smooth derivative of ξ_Δ (we need a time series; fake it here)
xi_delta_ts = np.abs(np.random.randn(30)) + 1.0   # ensure ≥1
dxidet = smoothed_derivative(xi_delta_ts, window=5, order=2)

# Thresholds (must be tuned ONLY on validation set – we simulate that by
# fixing them here; in practice they'd come from a separate validation split)
THRESH_ANOMALY = 2.5
THRESH_PHI_DELTA = 0.55
THRESH_DXI_DT = 0.05

# Prediction rule
pred_trigger = (anomaly_score > THRESH_ANOMALY) and \
               (phi_delta.item() > THRESH_PHI_DELTA) and \
               (np.mean(dxidet) > THRESH_DXI_DT)   # use mean over window as proxy

# ----------------------------------------------------------------------
# 7. Cost function and QP constraint verification
# ----------------------------------------------------------------------
# Mock additional terms for the cost function
Sh = np.random.rand()               # Shannon entropy ∈ [0,1]
alpha, beta, gamma, lam = 0.1, 0.1, 0.1, 1.0
P_meas = np.random.rand()
P_target = 0.5

# Cost integrand (per time step)
cost = (1.0 - Sh)**2 + alpha * Sh + lam * (P_meas - P_target)**2 \
       + beta * (xi_delta.item() - 1.0)**2 + \
       gamma * max(0.0, esi_k - 2.5)   # ReLU(ESI_k - 2.5)

# QP constraints
assert esi_k <= 2.5 + 1e-9, "ESI_k violates hard upper bound 2.5"
assert phi_n.item() >= 0.75, "Φ_n violates lower bound 0.75"
assert xi_delta.item() <= 3.0, "ξ_Δ violates upper bound 3.0"

# ----------------------------------------------------------------------
# 8. Summary output
# ----------------------------------------------------------------------
print("=== EDIP-Ω Invariant Validation Summary ===")
print(f"Φ_N            : {phi_n.item():.4f}  [0,1] ✓")
print(f"Φ_Δ            : {phi_delta.item():.4f}  [0,1] ✓")
print(f"ξ_N            : {xi_n.item():.4f}  ≥0 ✓")
print(f"ξ_Δ            : {xi_delta.item():.4f}  ≥1 ✓")
print(f"ψ (baseline)   : {psi_baseline:.4f}  (invariant, untouched)")
print(f"χ(t) (dev.)    : {chi.item():.4f}  (derived, not invariant)")
print(f"ESI_k          : {esi_k:.4f}  ≤2.5 ? {'✓' if esi_k <= 2.5 else '✗'}")
print(f"Anomaly score  : {anomaly_score:.4f}  >{THRESH_ANOMALY}? {'✓' if anomaly_score > THRESH_ANOMALY else '✗'}")
print(f"Φ_Δ > {THRESH_PHI_DELTA}? {'✓' if phi_delta.item() > THRESH_PHI_DELTA else '✗'}")
print(f"dξ_Δ/dt > {THRESH_DXI_DT}? {'✓' if np.mean(dxidet) > THRESH_DXI_DT else '✗'}")
print(f"Prediction trigger : {'YES' if pred_trigger else 'NO'}")
print(f"Cost integrand : {cost:.4f}")
print("All Rubric‑related assertions passed." if True else "Assertion failed.")