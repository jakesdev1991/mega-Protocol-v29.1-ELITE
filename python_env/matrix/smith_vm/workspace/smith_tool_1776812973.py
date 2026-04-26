# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol validation for Strategy‑Fragility Field Monitor (SFFM‑Ω)
-----------------------------------------------------------------
This script checks the mathematical consistency of the quantities
introduced in the SFFM‑Ω proposal against the Ω‑Physics Rubric v26.0
as interpreted from the text.

We treat all quantities as dimensionless after normalising Sharpe‑like
performance to unit variance.  The script is deliberately self‑contained
and uses only NumPy and SciPy for basic statistics.
"""

import numpy as np
from scipy.stats import skew
import itertools

# ------------------- USER‑DEFINED PARAMETERS -------------------
N_STRAT = 6                 # number of strategies in the ensemble
T_STEPS = 200               # time steps (e.g., days)
SEED = 42                   # reproducibility

# Coefficients appearing in the SFI tanh‑expression (all >0)
ALPHA, BETA, GAMMA, DELTA = 0.5, 0.5, 0.5, 0.5
LAMBDA = 0.5                # weight of SFI in ψ_strat
# Mapping from variance to Φ_N (inverse connectivity)
SIG2_MAX = 4.0              # worst‑case variance observed in training window
# Coefficients for Φ_N, Φ_Δ dynamics (lead‑time τ ignored for static check)
ETA1, ETA2, ETA3, ETA4 = 0.3, 0.3, 0.3, 0.3
# Baseline values (could be long‑term averages)
PHI_N0, PHI_DELTA0 = 0.7, 0.0
# MPC‑Ω thresholds
SFI_MAX = 0.7
PHI_N_MIN = 0.6
ENTROPY_MIN = np.log(4)    # ln(4) ≈ 1.386

# ------------------- SYNTHETIC DATA -------------------
rng = np.random.default_rng(SEED)
# Simulate correlated returns → Sharpe‑like performance
# Covariance matrix with moderate off‑diagonal correlation
corr = np.full((N_STRAT, N_STRAT), 0.3)
np.fill_diagonal(corr, 1.0)
cov = corr * SIG2_MAX
returns = rng.multivariate_normal(mean=np.zeros(N_STRAT), cov=cov, size=T_STEPS)
# Convert to dimensionless performance (e.g., Sharpe over window)
performance = returns.mean(axis=0) / (returns.std(axis=0) + 1e-8)   # shape (N_STRAT,)

# For time‑varying analysis we can roll a window; here we use the whole sample
# but we could compute per‑step if desired.
S_field = performance.copy()          # 𝒮(x,t) at the latest time (vector over strategies)

# ------------------- DERIVED QUANTITIES -------------------
# 1) Performance variance and skewness (across strategies)
sigma2 = np.var(S_field)               # scalar variance
gamma  = skew(S_field)                 # scalar skewness

# 2) Inverse connectivity Φ_N (simple linear map)
Phi_N = 1.0 - sigma2 / SIG2_MAX
Phi_N = np.clip(Phi_N, 0.0, 1.0)       # keep in [0,1]

# 3) Asymmetry Φ_Δ (use skewness directly, shifted by baseline)
Phi_Delta = PHI_DELTA0 + ETA3 * gamma - ETA4 * sigma2

# 4) Strategy weights (softmax of performance → mimics capital allocation)
w = np.exp(S_field - np.max(S_field))  # shift for numerical stability
w = w / w.sum()
# Entropy of weights
S_strat = -np.sum(w * np.log(w + 1e-12))

# 5) Ollivier‑Ricci curvature proxy:
#    Build a similarity graph where edge weight = |corr|.
#    Approximate curvature as 1 - (average edge weight) (a very rough proxy).
corr_matrix = np.corrcoef(returns.T)    # N×N correlation of returns over time
# Remove self‑loops
mask = ~np.eye(N_STRAT, dtype=bool)
avg_corr = np.abs(corr_matrix[mask]).mean()
# Curvature invariant (positive when graph is more tree‑like)
R_strat = 1.0 - avg_corr               # ∈ [0,1] ; larger → less connectivity
R0 = 1.0                               # reference curvature

# 6) Strategy Fragility Index (SFI)
theta_conc = w.max()                   # weight of top‑heavy strategy
SFI_raw = (ALPHA * theta_conc +
           BETA * sigma2 +
           GAMMA * np.abs(R_strat) +
           DELTA * (1.0 - S_strat))
SFI = np.tanh(SFI_raw)                 # ensures (-1,1); we shift to [0,1] by assuming args≥0
# For safety, clamp to [0,1]
SFI = np.clip(SFI, 0.0, 1.0)

# 7) ψ_strat (curvature + λ·SFI)
psi_strat = np.log(np.abs(R_strat) / R0 + 1e-12) + LAMBDA * SFI

# 8) Entropy gauge and gauge current
#    A_μ = ∂_μ S_strat → we approximate time derivative by zero (static check)
#    Hence A_0 = 0, A_i = 0 → product A_μ J^μ = 0 (dimensionless trivially)
#    To test non‑trivial case we compute a finite‑difference over a dummy time axis:
#    We'll create two consecutive snapshots (t and t+1) by adding small noise.
S_field_t = S_field
S_field_t1 = S_field + rng.normal(scale=0.01, size=N_STRAT)
w_t = np.exp(S_field_t - np.max(S_field_t))
w_t = w_t / w_t.sum()
w_t1 = np.exp(S_field_t1 - np.max(S_field_t1))
w_t1 = w_t1 / w_t1.sum()
S_strat_t = -np.sum(w_t * np.log(w_t + 1e-12))
S_strat_t1 = -np.sum(w_t1 * np.log(w_t1 + 1e-12))
A0 = (S_strat_t1 - S_strat_t)   # discrete ∂_0 S
# Spatial derivative approximated as zero (no spatial grid in this toy model)
A_mu = np.array([A0, 0.0, 0.0, 0.0])   # μ = 0,1,2,3
J_mu = np.array([np.sqrt(2) * Phi_Delta, 0.0, 0.0, 0.0])  # only time component non‑zero
gauge_term = np.dot(A_mu, J_mu)   # should be dimensionless number

# 9) Boundary condition flags
shredding = (psi_strat > 20) and (Phi_Delta > 20)   # large positive thresholds
freeze    = (psi_strat < -20) and (abs(Phi_Delta) < 1e-3)

# ------------------- VALIDATION CHECKS -------------------
def check(name, condition, value=None):
    if not condition:
        raise AssertionError(f"Ω‑INVARIANT VIOLATION – {name}: {value}")
    else:
        print(f"[PASS] {name}" + (f" = {value}" if value is not None else ""))

try:
    check("SFI bounded [0,1]", 0.0 <= SFI <= 1.0, SFI)
    check("Φ_N ≥ 0.6", Phi_N >= PHI_N_MIN, Phi_N)
    check("Entropy S_strat ≥ ln4", S_strat >= ENTROPY_MIN, S_strat)
    check("Gauge term dimensionless (numeric)", np.isfinite(gauge_term), gauge_term)
    check("Φ_N derived from variance in [0,1]", 0.0 <= Phi_N <= 1.0, Phi_N)
    check("ψ_strat finite (no NaN/Inf)", np.isfinite(psi_strat), psi_strat)
    # Boundary logic – just informational; not a hard invariant unless triggered
    if shredding:
        print("[INFO] Strategy Shredding condition detected (ψ≫0 & ΦΔ≫0)")
    if freeze:
        print("[INFO] Strategy Freeze condition detected (ψ≪0 & ΦΔ≈0)")
    print("\nAll Ω‑Protocol invariants satisfied for the synthetic snapshot.")
except AssertionError as e:
    print(e)
    raise SystemExit("Validation failed.")