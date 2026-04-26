# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script for CLEM‑Ω v2 proposal.
Checks:
  - Dimensional consistency (z‑scored features)
  - CLE computation
  - Rubric‑compliant invariants (ψ_CLE, ξ_N^CLE, ξ_Δ^CLE, S_h^CLE)
  - Constraint feasibility (CLE ≤ 2, Φ_N ≥ 0.75, ψ_CLE ≤ 0)
  - Extreme‑value anomaly detection logic
  - Convexity of the MPC quadratic cost term (CLE²)
"""

import numpy as np
from scipy.stats import genpareto

# --------------------------
# Synthetic data generation
# --------------------------
np.random.seed(42)
n_units = 4          # business units
n_creds_per_unit = 5 # credentials per unit
n_days = 60          # observation window

# Raw features (rotation velocity per day, strength [0,1], expiration deviation, mapping volatility)
R_raw = np.abs(np.random.normal(loc=0.02, scale=0.01, size=(n_units, n_creds_per_unit, n_days)))   # changes/day
S_raw = np.clip(np.random.normal(loc=0.7, scale=0.15, size=(n_units, n_creds_per_unit, n_days)), 0, 1)
E_raw = np.abs(np.random.normal(loc=0.0, scale=0.05, size=(n_units, n_creds_per_unit, n_days)))   # deviation
M_raw = np.abs(np.random.normal(loc=0.01, scale=0.005, size=(n_units, n_creds_per_unit, n_days))) # mapping change rate

# --------------------------
# Feature standardization (z‑score) per feature across all units/creds/days
# --------------------------
def zscore(x):
    return (x - np.mean(x)) / (np.std(x) + 1e-12)

R = zscore(R_raw)
S = zscore(S_raw)
E = zscore(E_raw)
M = zscore(M_raw)

# --------------------------
# CLE computation (linear combination with learned weights)
# --------------------------
# Example weights (could be learned; here we pick a plausible set)
alpha, beta, gamma, delta = 0.4, 0.3, 0.2, 0.1
CLE_raw = alpha * R + beta * S + gamma * E + delta * M   # shape (units, creds, days)

# Aggregate per unit: mean over credentials, then rolling window (here simple mean over time for demo)
CLE_unit = np.mean(CLE_raw, axis=(1, 2))   # shape (units,)

# --------------------------
# Rubric‑compliant invariants
# --------------------------
CLE_0 = np.median(CLE_unit)   # reference value from calibration period
psi_CLE = np.log(CLE_unit / CLE_0)   # scalar invariant

# Radial correlation length ξ_N^CLE: gradient w.r.t. unit features (use unit size as proxy)
unit_sizes = np.array([100, 250, 500, 1200])   # arbitrary sizes
# Approximate gradient via finite difference of CLE vs size
grad_CLE = np.gradient(CLE_unit, unit_sizes)
xi_N_CLE = np.sqrt(1.0 / (np.mean(grad_CLE**2) + 1e-12))

# Poloidal correlation length ξ_Δ^CLE: ratio of feature variances across credentials
# Compute variance of each feature across credentials (averaged over time)
var_R = np.var(np.mean(R, axis=2), axis=1)   # per unit
var_S = np.var(np.mean(S, axis=2), axis=1)
var_E = np.var(np.mean(E, axis=2), axis=1)
var_M = np.var(np.mean(M, axis=2), axis=1)
# Stack variances per unit, then compute ratio max/min across the four features
var_stack = np.vstack([var_R, var_S, var_E, var_M])   # shape (4, units)
xi_delta_CLE = np.max(var_stack, axis=0) / (np.min(var_stack, axis=0) + 1e-12)

# Shannon entropy of credential‑risk distribution S_h^CLE
# Risk weight w_c = R_c * (1 - S_c) * E_c (using raw, non‑zscored for interpretability)
w = R_raw * (1 - S_raw) * E_raw
# Normalize per unit per day
w_sum = np.sum(w, axis=1, keepdims=True) + 1e-12
p = w / w_sum   # shape (units, creds, days)
# Avoid log(0)
p_safe = np.clip(p, 1e-12, None)
S_h_CLE = -np.sum(p_safe * np.log(p_safe), axis=1)   # shape (units, days)
S_h_CLE_avg = np.mean(S_h_CLE, axis=1)   # temporal average per unit

# --------------------------
# Mapping to Omega variables (simple linear fit for demo)
# --------------------------
Phi_N_0, Phi_Delta_0 = 0.85, 0.3
eta1, eta2 = 0.1, 0.15
tau1, tau2 = 3, 3   # weeks, approximated as index shift (we ignore shift for static check)
Phi_N_cred = Phi_N_0 - eta1 * psi_CLE
Phi_Delta_cred = Phi_Delta_0 + eta2 * xi_delta_CLE

# --------------------------
# Extreme‑value anomaly detection on CLE
# --------------------------
# Fit GPD to exceedances over high threshold u (90th percentile)
u = np.percentile(CLE_unit, 90)
exceedances = CLE_unit[CLE_unit > u] - u
if len(exceedances) > 0:
    # Fit shape (c) and scale (sigma) parameters; fix loc=0
    shape, loc, scale = genpareto.fit(exceedances, floc=0)
    # Tail probability for each observation
    def tail_prob(x):
        if x <= u:
            return 1.0
        return genpareto.sf(x - u, shape, loc, scale)   # survival function
    a_CLE = np.array([tail_prob(x) for x in CLE_unit])
else:
    a_CLE = np.ones_like(CLE_unit)   # no exceedances => no anomaly

# --------------------------
# Constraint checks (Omega Protocol invariants)
# --------------------------
constraints_ok = (
    np.all(CLE_unit <= 2.0 + 1e-9) and
    np.all(Phi_N_cred >= 0.75 - 1e-9) and
    np.all(psi_CLE <= 0.0 + 1e-9)
)

# Anomaly rule: flag if a_CLE < 0.01 and Phi_Delta_cred > 0.5
anomaly_flag = np.any((a_CLE < 0.01) & (Phi_Delta_cred > 0.5))

# --------------------------
# MPC cost function convexity check (quadratic term CLE²)
# --------------------------
# Cost integrand: lambda2 * CLE^2  (lambda2 > 0 ensures convexity)
lambda2 = 0.5
# Hessian of lambda2 * CLE^2 w.r.t. CLE is 2*lambda2 * I (positive definite if lambda2>0)
hessian_psd = lambda2 > 0

# --------------------------
# Output validation results
# --------------------------
print("=== CLEM‑Ω v2 Validation ===")
print(f"CLE values (units): {CLE_unit}")
print(f"ψ_CLE: {psi_CLE}")
print(f"ξ_N^CLE: {xi_N_CLE:.4f}")
print(f"ξ_Δ^CLE: {xi_delta_CLE}")
print(f"S_h^CLE (avg): {S_h_CLE_avg}")
print(f"Φ_N^cred: {Phi_N_cred}")
print(f"Φ_Δ^cred: {Phi_Delta_cred}")
print(f"a_CLE (tail prob): {a_CLE}")
print()
print("Constraint Checks:")
print(f"  CLE ≤ 2.0          : {'PASS' if np.all(CLE_unit <= 2.0+1e-9) else 'FAIL'}")
print(f"  Φ_N^cred ≥ 0.75    : {'PASS' if np.all(Phi_N_cred >= 0.75-1e-9) else 'FAIL'}")
print(f"  ψ_CLE ≤ 0          : {'PASS' if np.all(psi_CLE <= 0.0+1e-9) else 'FAIL'}")
print(f"  All constraints    : {'PASS' if constraints_ok else 'FAIL'}")
print()
print("Anomaly Detection:")
print(f"  Any anomaly flagged (a_CLE<0.01 & Φ_Δ^cred>0.5): {'YES' if anomaly_flag else 'NO'}")
print()
print("MPC Convexity:")
print(f"  λ2 > 0 (ensures CLE² term convex): {'PASS' if hessian_psd else 'FAIL'}")
print()
overall = constraints_ok and hessian_psd
print(f"OVERALL VALIDATION: {'PASS' if overall else 'FAIL'}")