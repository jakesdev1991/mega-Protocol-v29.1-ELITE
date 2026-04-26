# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLEM‑Ω v2 invariant validator.
Agent Smith – Matrix Guardian.
"""

import numpy as np
from scipy.stats import genpareto

# ------------------- CONFIGURATION -------------------
np.random.seed(42)
N_UNITS = 5               # number of business units
N_CREDS_PER_UNIT = 20     # credentials per unit
TIME_STEPS = 100          # temporal length for anomaly detection

# Hyper‑parameters (to be tuned from data)
ALPHA, BETA, GAMMA, DELTA = 0.3, 0.4, 0.2, 0.1   # CLE weights (must sum to 1)
ETA1, ETA2 = 0.5, 0.3                         # mapping to Ω vars
TAU1, TAU2 = 3, 4                             # weeks (converted to steps if needed)
CLE0_REF = 1.0                                 # reference CLE (median of calibration)
EPS = 1e-9                                      # regularisation to avoid div‑by‑zero
DELTA_PSI = 1e-3                                # allowed slack for ψ_CLE ≤ 0
GPD_THRESH_PERC = 90                            # percentile for GPD threshold
TAIL_PROB = 0.01                                # 1% tail for anomaly flag

# ------------------- HELPERS -------------------
def standardise(x):
    """Z‑score; returns (xz, mean, std) and flags zero‑std."""
    mu = np.mean(x)
    sigma = np.std(x)
    if sigma < EPS:
        return np.zeros_like(x), mu, sigma, True   # zero‑std → flag
    return (x - mu) / sigma, mu, sigma, False

def safe_log_ratio(x, x0):
    """ψ = ln(x/x0) with guard for non‑positive x."""
    if x <= 0:
        return -np.inf
    return np.log(x / x0)

def radial_corr_len(cle_per_unit, unit_features):
    """
    ξ_N^{(CLE)} = ( (1/B) Σ ‖∇_b CLE_b‖² )^{-1/2}
    Approximate gradient by finite difference w.r.t. each unit feature.
    unit_features: shape (B, F) – already standardised.
    """
    B, F = unit_features.shape
    grad_sq_sum = 0.0
    for b in range(B):
        # central difference for each feature
        grad = np.zeros(F)
        for f in range(F):
            eps_step = 1e-4
            pert = unit_features[b].copy()
            pert[f] += eps_step
            # Re‑compute CLE for perturbed unit (linear in features)
            cle_pert = (ALPHA * pert[0] + BETA * pert[1] +
                        GAMMA * pert[2] + DELTA * pert[3])  # placeholder
            cle_base = (ALPHA * unit_features[b,0] + BETA * unit_features[b,1] +
                        GAMMA * unit_features[b,2] + DELTA * unit_features[b,3])
            grad[f] = (cle_pert - cle_base) / eps_step
        grad_sq_sum += np.dot(grad, grad)
    xi = ((grad_sq_sum / B) + EPS) ** (-0.5)
    return xi

def poloidal_corr_len(feature_matrix):
    """
    ξ_Δ^{(CLE)} = (max_f σ_f² + ε) / (min_f σ_f² + ε)
    feature_matrix: shape (N_creds, 4) – [R, S, E, M] already standardised.
    """
    var_per_feat = np.var(feature_matrix, axis=0) + EPS
    return np.max(var_per_feat) / np.min(var_per_feat)

def cred_entropy(weights):
    """
    S_h^{(CLE)} = - Σ p ln p,  p = w / Σw ; guard Σw = 0 → entropy = 0.
    """
    w_sum = np.sum(weights)
    if w_sum < EPS:
        return 0.0
    p = weights / w_sum
    # avoid log(0)
    p = np.clip(p, EPS, None)
    return -np.sum(p * np.log(p))

def fit_gpd_exceedances(data, threshold):
    """Fit GPD to exceedances over threshold; return shape, loc, scale."""
    exceed = data[data > threshold] - threshold
    if len(exceed) < 2:
        return 0.0, threshold, 1.0   # fallback: exponential
    shape, loc, scale = genpareto.fit(exceed, floc=0)
    return shape, loc, scale

def tail_prob_gpd(x, threshold, shape, loc, scale):
    """Survival function 1‑F(x) for GPD."""
    if x <= threshold:
        return 1.0
    z = (x - threshold - loc) / scale
    return genpareto.sf(z, shape, loc=0, scale=scale)

# ------------------- DATA SYNTHESIS -------------------
# Simulate four features per credential: R, S, E, M (already standardised)
feat_all = []   # list of (unit_id, cred_id, feature_vector)
cle_per_unit = []   # time‑series of CLE per unit
for u in range(N_UNITS):
    # generate raw features with some unit‑specific bias
    R_raw = np.random.lognormal(mean=0.0, sigma=0.5, size=N_CREDS_PER_UNIT)
    S_raw = np.random.beta(2, 5, size=N_CREDS_PER_UNIT)   # strength 0‑1
    E_raw = np.abs(np.random.normal(loc=0.0, scale=0.2, size=N_CREDS_PER_UNIT))
    M_raw = np.random.exponential(scale=0.3, size=N_CREDS_PER_UNIT)
    # stack and standardise per feature across all credentials of this unit
    raw = np.vstack([R_raw, S_raw, E_raw, M_raw]).T   # (N,4)
    std_feat = np.zeros_like(raw)
    zero_std_flags = []
    for f in range(4):
        z, _, _, zero_flag = standardise(raw[:, f])
        std_feat[:, f] = z
        zero_std_flags.append(zero_flag)
    feat_all.append((u, std_feat))
    # CLE per unit (time‑invariant for this demo)
    cle = (ALPHA * np.mean(std_feat[:,0]) +
           BETA * np.mean(std_feat[:,1]) +
           GAMMA * np.mean(std_feat[:,2]) +
           DELTA * np.mean(std_feat[:,3]))
    cle_per_unit.append([cle] * TIME_STEPS)   # repeat for simplicity

cle_per_unit = np.array(cle_per_unit)   # shape (U, T)

# ------------------- INVARIANT CHECKS -------------------
print("\n=== Omega Protocol Invariant Validation ===")
violations = []

for u in range(N_UNITS):
    for t in range(TIME_STEPS):
        cle_t = cle_per_unit[u, t]
        # ψ_CLE
        psi = safe_log_ratio(cle_t, CLE0_REF)
        # ξ_N^{(CLE)} – need unit features; we reuse the std_feat of unit u
        unit_feat = feat_all[u][1]   # (N,4)
        xi_N = radial_corr_len(cle_t, unit_feat)
        # ξ_Δ^{(CLE)} – variance across credentials of unit u
        xi_DELTA = poloidal_corr_len(unit_feat)
        # S_h^{(CLE)} – weight = R * (1‑S) * E (as in proposal)
        R = unit_feat[:,0]
        S = unit_feat[:,1]
        E = unit_feat[:,2]
        w = R * (1.0 - S) * E
        Sh = cred_entropy(w)

        # Map to Ω variables
        PhiN = 0.8 - ETA1 * psi   # assume PhiN0 = 0.8 (baseline)
        PhiD = 0.2 + ETA2 * xi_DELTA   # assume PhiDelta0 = 0.2

        # Constraint checks
        if cle_t > 2.0 + EPS:
            violations.append(f"U{u} T{t}: CLE={cle_t:.3f} > 2.0")
        if psi > DELTA_PSI:
            violations.append(f"U{u} T{t}: ψ_CLE={psi:.3f} > {DELTA_PSI}")
        if PhiN < 0.75 - EPS:
            violations.append(f"U{u} T{t}: Φ_N={PhiN:.3f} < 0.75")
        if PhiD > 0.6 + EPS:
            violations.append(f"U{u} T{t}: Φ_Δ={PhiD:.3f} > 0.6")
        # (Optional) Jerk stability stub – replace with real metric later
        # jerk = jerk_stability(...)
        # if jerk < 0 or jerk > 1: ...

if violations:
    print("VIOLATIONS DETECTED:")
    for v in violations[:10]:   # limit output
        print(" -", v)
    if len(violations) > 10:
        print(f" ... and {len(violations)-10} more")
else:
    print("All invariants satisfied for the synthetic dataset.")

# ------------------- ANOMALY DETECTION (GPD) -------------------
print("\n=== Extreme‑Value Anomaly Detection ===")
# Use the first unit's CLE time series
cle_series = cle_per_unit[0]
threshold = np.percentile(cle_series, GPD_THRESH_PERC)
shape, loc, scale = fit_gpd_exceedances(cle_series, threshold)
print(f"GPD threshold ({(GPD_THRESH_PERC)}th %ile) = {threshold:.3f}")
print(f"Fitted GPD: shape={shape:.3f}, loc={loc:.3f}, scale={scale:.3f}")

# Compute anomaly score at each time step
anomaly_flags = []
for t, val in enumerate(cle_series):
    a_tail = tail_prob_gpd(val, threshold, shape, loc, scale)
    # compute PhiD at time t‑TAU2 (simple shift)
    psi_tau = safe_log_ratio(cle_series[max(0, t-TAU2)], CLE0_REF)
    xi_DELTA_tau = poloidal_corr_len(feat_all[0][1])  # assume stationary for demo
    PhiD_tau = 0.2 + ETA2 * xi_DELTA_tau
    if a_tail < TAIL_PROB and PhiD_tau > 0.5:
        anomaly_flags.append(t)

if anomaly_flags:
    print(f"Anomaly flagged at steps: {anomaly_flags[:5]}"
          f"{'...' if len(anomaly_flags)>5 else ''}")
else:
    print("No anomalies detected under the (tail < 1% & Φ_Δ>0.5) rule.")

# ------------------- OPTIONAL: JERK STABILITY STUB -------------------
def jerk_stability(jerk_series):
    """
    Placeholder – replace with a sound definition.
    Returns a value in [0,1] where 1 = perfectly stable jerk.
    """
    # Example: variance‑regularised excess kurtosis
    if len(jerk_series) < 2:
        return 1.0
    mu = np.mean(jerk_series)
    sigma = np.std(jerk_series) + EPS
    excess_kurt = np.mean(((jerk_series - mu) / sigma) ** 4) - 3
    # map excess kurtosis ∈ [−2, ∞) to stability ∈ (0,1]
    return 1.0 / (1.0 + abs(excess_kurt))

# ------------------- END -------------------
if not violations:
    print("\n✔️  Synthetic data passes all Omega‑Protocol checks.")
else:
    print("\n❌  Invariant violations found – fix the model before deployment.")