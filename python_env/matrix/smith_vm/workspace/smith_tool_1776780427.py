# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for the CDM‑Ω proposal.
Checks mathematical soundness and invariant compliance.
"""

import numpy as np

# -------------------------- Configuration --------------------------
N_OCCUPANTS = 50          # number of occupants (N)
D_FEATURES = 6            # dimensionality of β (d)
WINDOW_DAYS = 7           # sliding window length (not used directly)
TRAIL_DAYS = 30           # trailing window for features
DT = 1.0                  # time step in days (for derivative approx.)
# Normalisation constants (learned from baseline in practice)
R_MAX, C_MAX, A_MAX = 1.0, 1.0, 1.0   # assume features scaled to [0,1]
LOG_B = np.log(20)                # e.g., 20 direction bins -> max entropy
# Weights for CDI (must be non‑negative and sum to 1)
ALPHA = np.array([0.3, 0.3, 0.2, 0.2])   # [α1, α2, α3, α4]
assert np.all(ALPHA >= 0) and np.abs(ALPHA.sum() - 1.0) < 1e-9
# Mapping coefficients
ETA1, ETA2, ETA3, ETA4 = 0.4, 0.3, 0.2, 0.1
GAMMA1 = 1.0
TAU1, TAU2 = 7.0, 7.0   # days (lead times)
PHI_N0, PHI_D0 = 0.7, 0.0
LAMBDA_PSI = 0.5        # λ in ψ definition
# MPC‑Ω thresholds
CDI_MAX = 0.8
PHI_N_MIN = 0.6
S_DIR_MIN = 0.2         # after normalisation to [0,1]
# Anomaly detection
GPD_THRESHOLD = 0.95    # u = 95th percentile of |ψ|
ALERT_PSI = 0.01        # a_CDM < ALERT_PSI triggers alert
PHI_DELTA_HIGH = 0.7
PHI_N_LOW = 0.5

# -------------------------- Helper Functions --------------------------
def normalize(x, x_min, x_max):
    """Min‑max normalisation to [0,1]; guard against zero range."""
    if x_max - x_min < 1e-12:
        return np.zeros_like(x)
    return np.clip((x - x_min) / (x_max - x_min), 0.0, 1.0)

def mahalanobis_distance(x, mu, sigma_inv):
    """Compute sqrt((x‑mu)^T Σ⁻¹ (x‑mu))."""
    diff = x - mu
    return np.sqrt(np.dot(diff, np.dot(sigma_inv, diff)))

# -------------------------- Synthetic Data Generation --------------------------
np.random.seed(42)
T = 100   # time steps

# Simulate raw feature time‑series (before normalisation)
R_raw = np.random.exponential(scale=0.2, size=T)          # rate of change
C_raw = np.random.beta(a=2, b=5, size=T)                 # correlation in [0,1]
A_raw = np.random.chisquare(df=4, size=T) * 0.1          # anomaly‑like
S_dir_raw = np.random.uniform(low=0.0, high=LOG_B, size=T)  # raw Shannon entropy
# Simulate λ₂(t) (second eigenvalue of diffusion map) – stay positive
lambda2_raw = np.random.uniform(low=0.5, high=2.0, size=T)
lambda2_0 = lambda2_raw.mean()   # baseline

# -------------------------- Pre‑processing (normalisation) --------------------------
R = normalize(R_raw, R_raw.min(), R_raw.max())   # -> [0,1]
C = normalize(C_raw, C_raw.min(), C_raw.max())   # already [0,1] but keep
A = normalize(A_raw, A_raw.min(), A_raw.max())
S_dir = normalize(S_dir_raw, 0.0, LOG_B)         # now in [0,1]
lambda2 = lambda2_raw   # keep raw; we will guard against zero later

# -------------------------- Core Computations --------------------------
# CDI(t) = α1·R + α2·C + α3·A - α4·S_dir
CDI = (ALPHA[0] * R + ALPHA[1] * C + ALPHA[2] * A
       - ALPHA[3] * S_dir)
# Clip to [0,1] after linear combination (should hold if alphas sum to 1 and features in [0,1])
CDI = np.clip(CDI, 0.0, 1.0)

# Φ_N and Φ_Δ mappings (with time‑lag approximated by same index for simplicity)
Phi_N = PHI_N0 + ETA1 * np.tanh(GAMMA1 * C) - ETA2 * CDI**2
Phi_D = PHI_D0 + ETA3 * R - ETA4 * S_dir

# ψ(t) = ln( λ₂(t) / λ₂₀ ) + λ·CDI(t)
# Guard λ₂ against zero
eps = 1e-12
psi = np.log((lambda2 + eps) / lambda2_0) + LAMBDA_PSI * CDI

# Anomaly score via GPD (simplified: use empirical tail)
abs_psi = np.abs(psi)
u = np.percentile(abs_psi, GPD_THRESHOLD * 100)
excess = abs_psi - u
excess = excess[excess > 0]   # only positive excesses
if len(excess) > 0:
    # Fit shape ξ and scale β via L‑moments (here we use simple MLE for exponential as placeholder)
    # For demonstration we assume exponential GPD (shape=0) → CDF = 1‑exp(-x/β)
    beta = excess.mean()
    def GPD_cdf(x):
        return 1.0 - np.exp(-x / beta) if x >= 0 else 0.0
else:
    beta = 1.0
    def GPD_cdf(x):
        return 0.0

a_CDM = 1.0 - GPD_cdf(np.maximum(abs_psi - u, 0.0))

# -------------------------- Invariant Checks --------------------------
def assert_invariant(name, condition, msg):
    if not np.all(condition):
        raise AssertionError(f"Omega Invariant Violation [{name}]: {msg}")

# 1. CDI must be in [0,1]
assert_invariant("CDI_bounds", (CDI >= 0.0) & (CDI <= 1.0),
                 f"CDI out of range: min={CDI.min():.3f}, max={CDI.max():.3f}")

# 2. Φ_N must be non‑negative (protocol expects ≥0, we also enforce Φ_N≥0.6 later)
assert_invariant("Phi_N_nonneg", Phi_N >= 0.0,
                 f"Phi_N negative: min={Phi_N.min():.3f}")

# 3. Φ_Δ should be a real number (no NaN/Inf)
assert_invariant("Phi_D_finite", np.isfinite(Phi_D),
                 f"Phi_D contains non‑finite values")

# 4. ψ should be real (no NaN/Inf from log of zero/negative)
assert_invariant("Psi_finite", np.isfinite(psi),
                 f"Psi contains non‑finite values (lambda2 too small?)")

# 5. Entropy gauge S_dir ∈ [0,1] after normalisation
assert_invariant("S_dir_norm", (S_dir >= 0.0) & (S_dir <= 1.0),
                 f"S_dir out of [0,1]: min={S_dir.min():.3f}, max={S_dir.max():.3f}")

# 6. MPC‑Ω constraints (hard bounds)
assert_invariant("CDI_max", CDI <= CDI_MAX + 1e-9,
                 f"CDI exceeds threshold {CDI_MAX}: max={CDI.max():.3f}")
assert_invariant("Phi_N_min", Phi_N >= PHI_N_MIN - 1e-9,
                 f"Phi_N below minimum {PHI_N_MIN}: min={Phi_N.min():.3f}")
assert_invariant("S_dir_min", S_dir >= S_DIR_MIN - 1e-9,
                 f"S_dir below minimum {S_DIR_MIN}: min={S_dir.min():.3f}")

# 7. Anomaly score must be in [0,1]
assert_invariant("a_CDM_bounds", (a_CDM >= 0.0) & (a_CDM <= 1.0),
                 f"a_CDM out of range: {a_CDM:.3f}")

# 8. Alert condition: if a_CDM < ALERT_PSI then (Φ_Δ > PHI_DELTA_HIGH or Φ_N < PHI_N_LOW)
alert_mask = a_CDM < ALERT_PSI
if np.any(alert_mask):
    cond = (Phi_D[alert_mask] > PHI_DELTA_HIGH) | (Phi_N[alert_mask] < PHI_N_LOW)
    assert_invariant("Alert_logic", np.all(cond),
                     f"Alert triggered but Phi_N/Phi_D condition failed: "
                     f"Phi_D={Phi_D[alert_mask]}, Phi_N={Phi_N[alert_mask]}")

# -------------------------- If we reach here, all invariants hold --------------------------
print("All Omega Protocol invariants satisfied for the synthetic trial.")
print(f"  CDI range   : [{CDI.min():.3f}, {CDI.max():.3f}]")
print(f"  Φ_N range   : [{Phi_N.min():.3f}, {Phi_N.max():.3f}]")
print(f"  Φ_Δ range   : [{Phi_D.min():.3f}, {Phi_D.max():.3f}]")
print(f"  ψ range     : [{psi.min():.3f}, {psi.max():.3f}]")
print(f"  a_CDM       : {a_CDM:.3f}")