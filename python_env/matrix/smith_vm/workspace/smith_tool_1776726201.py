# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for CERM‑Ω v2
-------------------------------------------------
This script checks the mathematical soundness of the refined CERM‑Ω v2
proposal against the core Omega invariants (Φ_N, Φ_Δ, J*) and the
rubric‑compliant quantities introduced in the audit.

It is deliberately lightweight: it works with synthetic data so that
you can see where a violation would occur. Replace the synthetic
generation with real data pipelines for production validation.
"""

import numpy as np
import scipy.stats as stats

# ----------------------------------------------------------------------
# Configuration (tweak to match your calibration)
# ----------------------------------------------------------------------
N_INST = 5                     # number of financial institutions
T_STEPS = 100                  # time steps (days)
SEED = 42

# Omega‑Protocol constants (as given in the proposal)
SCEI_MAX = 1.5                 # hard upper bound on systemic exposure
PHI_N_MIN = 0.7                # lower bound on consensus
PSI_BOUND = 0.0                # ψ_CES ≤ ψ_bound (originally 0)
EPS = 1e-12                    # small regulariser to avoid div0

# Rubric‑compliant parameters (example values; should be calibrated)
GAMMA = 0.05                   # exploitation rate (1/day)
ALPHA = 0.3                    # Φ_N coupling
BETA = 0.2                     # Φ_Δ coupling
TAU1 = 7.0                     # days lag for Φ_N
TAU2 = 7.0                     # days lag for Φ_Δ
THETA = 0.1                    # threshold for Φ_Δ activation

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def poisson_exploitation_rate(t_c, t, w, valid):
    """Contribution of a single credential to CES_i(t)."""
    if t < t_c:
        return 0.0
    return w * np.exp(-GAMMA * (t - t_c)) * (1.0 if valid else 0.0)

def compute_CES(cred_events, t):
    """
    cred_events: list of tuples (inst_idx, t_c, w, valid)
    Returns CES_i(t) for each institution as an array shape (N_INST,).
    """
    CES = np.zeros(N_INST)
    for inst, t_c, w, valid in cred_events:
        if t >= t_c:
            CES[inst] += poisson_exploitation_rate(t_c, t, w, valid)
    return CES

def compute_SCEI(CES, sizes):
    """Systemic Credential Exposure Index (dimensionless)."""
    weighted = CES * sizes
    return np.sum(weighted) / np.sum(sizes)

def psi_CES(SCEI, SCEI0):
    """Scalar invariant (dimensionless)."""
    if SCEI <= 0 or SCEI0 <= 0:
        raise ValueError("SCEI and SCEI0 must be > 0 for log.")
    return np.log(SCEI / SCEI0)

def radial_corr_len(CES, features):
    """
    ξ_N^(CES) = ( (1/N) Σ ||∇_i CES_i||^2 )^{-1/2}
    features: array shape (N_INST, n_feat) – e.g., [log(size), sector_onehot, lat, lon]
    We approximate ∇_i CES_i by finite difference across institutions in feature space.
    """
    # Simple gradient approximation: CES variation per unit feature distance
    # Using pairwise differences; for demo we use std dev / mean feature distance
    if N_INST < 2:
        return np.inf
    feat_dist = np.linalg.norm(features[:, None, :] - features[None, :, :], axis=2)
    # Avoid zero diagonal
    np.fill_diagonal(feat_dist, np.inf)
    # Weighted differences
    diff = CES[:, None] - CES[None, :]          # (N,N)
    grad_approx = np.abs(diff) / feat_dist      # (N,N)
    # Mean squared gradient per institution
    mean_sq_grad = np.mean(grad_approx**2, axis=1)
    xi_N = np.sqrt(1.0 / np.mean(mean_sq_grad))
    return xi_N

def poloidal_corr_len(CES, tier_labels):
    """
    ξ_Δ^(CES) = (max_k σ_k^2 + ε) / (min_k σ_k^2 + ε)
    tier_labels: array of ints (0,1,2) indicating tier for each institution's dominant exposure.
    """
    vars_by_tier = []
    for k in range(3):
        mask = (tier_labels == k)
        if np.any(mask):
            vars_by_tier.append(np.var(CES[mask]))
        else:
            vars_by_tier.append(0.0)   # no exposure in this tier
    vars_by_tier = np.array(vars_by_tier)
    xi_Delta = (np.max(vars_by_tier) + EPS) / (np.min(vars_by_tier) + EPS)
    return xi_Delta

def entropy_exposure(CES):
    """Shannon entropy of exposure distribution; returns 0 if total exposure = 0."""
    total = np.sum(CES)
    if total < EPS:
        return 0.0
    p = CES / total
    # Avoid log(0)
    p = np.clip(p, EPS, None)
    return -np.sum(p * np.log(p))

def jerk_stability_metric(phi_n_series):
    """
    Safe jerk‑stability metric: S_j = (1 + |κ|)^{-1}
    where κ is excess kurtosis of the jerk (third derivative).
    """
    # Compute jerk via central difference (requires at least 5 points)
    if len(phi_n_series) < 5:
        return 1.0   # neutral if not enough data
    # First derivative (velocity)
    vel = np.gradient(phi_n_series)
    # Second derivative (acceleration)
    acc = np.gradient(vel)
    # Third derivative (jerk)
    jerk = np.gradient(acc)
    # Excess kurtosis
    kappa = stats.kurtosis(jerk, fisher=True)  # returns excess kurtosis
    S_j = 1.0 / (1.0 + np.abs(kappa))
    return S_j

# ----------------------------------------------------------------------
# Synthetic data generation (for demonstration)
# ----------------------------------------------------------------------
np.random.seed(SEED)

# Institution sizes (market footprint) – log‑normal distribution
sizes = np.random.lognormal(mean=10, sigma=0.5, size=N_INST)
sizes = sizes / np.mean(sizes)   # normalise so mean size = 1

# Feature vector for radial correlation length: [log(size), sector_onehot, lat, lon]
# For simplicity we use only log(size) and a random sector (0,1,2)
log_size = np.log(sizes)
sector = np.random.randint(0, 3, size=N_INST)   # one‑hot encoded later
features = np.column_stack([log_size, sector])  # shape (N_INST, 2)

# Tier label per institution (dominant exposure tier)
tier_labels = np.random.randint(0, 3, size=N_INST)

# Generate credential leak events (Poisson process per institution)
cred_events = []   # list of (inst, t_c, w, valid)
for inst in range(N_INST):
    # Number of leaks in the window ~ Poisson(λ_leak * T)
    n_leaks = np.random.poisson(0.02 * T_STEPS)  # low leak rate
    for _ in range(n_leaks):
        t_c = np.random.randint(0, T_STEPS)
        # weight by tier (Tier1=1.0, Tier2=0.5, Tier3=0.2)
        w = {0:1.0, 1:0.5, 2:0.2}[tier_labels[inst]]
        # validity: 80% chance still valid at leak time
        valid = np.random.rand() < 0.8
        cred_events.append((inst, t_c, w, valid))

# ----------------------------------------------------------------------
# Time‑series evaluation
# ----------------------------------------------------------------------
SCEI_series = np.zeros(T_STEPS)
phi_n_series = np.zeros(T_STEPS)   # dummy Φ_N (we will update via coupling)
phi_delta_series = np.zeros(T_STEPS)

# Initialize Φ_N, Φ_Δ at baseline values
phi_n_series[0] = 1.0
phi_delta_series[0] = 0.5

# Reference SCEI0 (median over a burn‑in period)
burn_in = 20
SCEI0_est = None

for t in range(T_STEPS):
    CES_t = compute_CES(cred_events, t)
    SCEI_t = compute_SCEI(CES_t, sizes)
    SCEI_series[t] = SCEI_t

    # Update Φ_N and Φ_Δ using the proposed linear mappings (with lags)
    if t >= int(TAU1):
        psi = psi_CES(SCEI_series[t - int(TAU1)], np.median(SCEI_series[:t - int(TAU1)+1]) + EPS)
        phi_n_series[t] = 1.0 - ALPHA * psi   # baseline Φ_N^{(0)} = 1.0
    else:
        phi_n_series[t] = 1.0

    if t >= int(TAU2):
        xi_Delta = poloidal_corr_len(CES_t, tier_labels)
        phi_delta_series[t] = 0.5 + BETA * np.max([0.0, xi_Delta - THETA])
    else:
        phi_delta_series[t] = 0.5

    # Enforce hard bounds (these are the Omega invariants we must respect)
    if phi_n_series[t] < PHI_N_MIN:
        raise ValueError(f"Phi_N violation at t={t}: {phi_n_series[t]} < {PHI_N_MIN}")
    if SCEI_t > SCEI_MAX:
        raise ValueError(f"SCEI violation at t={t}: {SCEI_t} > {SCEI_MAX}")

    # ψ_CES bound (optional, depends on calibration)
    if t >= burn_in:
        if SCEI0_est is None:
            SCEI0_est = np.median(SCEI_series[:t+1])
        psi_t = psi_CES(SCEI_t, SCEI0_est)
        if psi_t > PSI_BOUND:
            raise ValueError(f"ψ_CES violation at t={t}: {psi_t} > {PSI_BOUND}")

# ----------------------------------------------------------------------
# Additional invariant checks (entropy, correlation lengths, jerk metric)
# ----------------------------------------------------------------------
# Entropy check (should never raise)
for t in range(T_STEPS):
    CES_t = compute_CES(cred_events, t)
    _ = entropy_exposure(CES_t)   # will return 0 if total exposure = 0

# Poloidal correlation length regularisation check (ensure finite)
for t in range(T_STEPS):
    CES_t = compute_CES(cred_events, t)
    xi_D = poloidal_corr_len(CES_t, tier_labels)
    if not np.isfinite(xi_D):
        raise ValueError(f"ξ_Δ^(CES) non‑finite at t={t}")

# Jerk‑stability metric sanity (should be in (0,1])
for t in range(4, T_STEPS):
    S_j = jerk_stability_metric(phi_n_series[:t+1])
    if not (0.0 < S_j <= 1.0):
        raise ValueError(f"Jerk stability metric out of range at t={t}: {S_j}")

# ----------------------------------------------------------------------
# If we reach here, all tested invariants hold for this synthetic run
# ----------------------------------------------------------------------
print("✅ All Omega‑Protocol invariants satisfied for the synthetic scenario.")
print(f"   Final Φ_N = {phi_n_series[-1]:.4f}  (min = {np.min(phi_n_series):.4f})")
print(f"   Final Φ_Δ = {phi_delta_series[-1]:.4f}")
print(f"   Final SCEI = {SCEI_series[-1]:.4f}  (max observed = {np.max(SCEI_series):.4f})")
print(f"   ψ_CES (last) = {psi_CES(SCEI_series[-1], np.median(SCEI_series)+EPS):.4f}")