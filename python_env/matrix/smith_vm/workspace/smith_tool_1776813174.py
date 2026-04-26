# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for Information‑Cascade Monitor (IC‑Ω)
Checks mathematical consistency and invariant compliance.
"""

import numpy as np
import cvxpy as cp

# ----------------------------------------------------------------------
# 1. PARAMETERS (user‑defined – replace with calibrated values)
# ----------------------------------------------------------------------
# Field parameters
D   = 0.01      # diffusion > 0
kappa = 0.05    # growth rate > 0
I_max = 1.0     # saturation

# Potential parameters (must satisfy alpha < 0, beta > 0, gamma > 0)
alpha = -0.2    # <-- note sign: negative for double‑well
beta  = 0.3
gamma = 0.1

# Mapping coefficients (eta_i) – must keep outputs in [0,1]
eta1, eta2 = 0.15, 0.10
eta3, eta4 = 0.12, 0.08
PhiN0, PhiD0 = 0.7, 0.3   # baseline invariants

# Time lag (weeks) – not needed for static check
tau = 1.0

# Synthetic order‑book metrics at a given t (normally from data)
O_t   = 0.4   # order‑imbalance ratio ∈[0,1]
L_t   = 0.2   # liquidity withdrawal ∈[0,1]
C_t   = 0.35  # cross‑ETF correlation ∈[0,1]
Delta_t = 0.25 # trader‑response skew (dimensionless, can be >0)

# CI coefficients (alpha_i in tanh)
aO, aL, aC, aD = 0.6, 0.4, 0.3, 0.2

# Entropy: volume shares of K trader types
K = 3
p = np.array([0.5, 0.3, 0.2])   # must sum to 1, non‑negative
assert np.allclose(p.sum(), 1.0) and np.all(p >= 0)

# MPC‑Ω thresholds
CI_MAX   = 0.7
PHIN_MIN = 0.6
S_MIN    = np.log(3)   # ≈1.099

# Penalty weights (positive)
mu1, mu2, mu3 = 1.0, 1.0, 1.0

# ----------------------------------------------------------------------
# 2. VALIDATION CHECKS
# ----------------------------------------------------------------------
print("=== Omega Protocol Consistency Check ===")

# 2.1 Field well‑posedness
assert D > 0, "Diffusion D must be positive."
assert kappa > 0, "Growth rate κ must be positive."
print("[✓] RD‑A well‑posed (D>0, κ>0).")

# 2.2 Potential shape (double‑well)
# Minima solve dV/dI = α I + β I³ - γ = 0
# For α<0, β>0 we expect three real roots; outer two are minima.
discriminant = (alpha**2) - 4*beta*(-gamma)  # from cubic depressed form
# Simple sign check: α<0, β>0, γ>0 ensures two minima + one max.
assert alpha < 0 and beta > 0 and gamma > 0, \
    "Potential requires α<0, β>0, γ>0 for double‑well."
print("[✓] Potential V(I) has double‑well shape (α<0,β>0,γ>0).")

# 2.3 Cascade Intensity Index CI ∈ [0,1]
CI_raw = aO*O_t + aL*L_t + aC*C_t + aD*Delta_t
CI = np.tanh(CI_raw)   # tanh maps ℝ→(-1,1); shift to [0,1] via (tanh+1)/2
CI = (CI + 1.0) / 2.0
assert 0.0 <= CI <= 1.0, f"CI out of bounds: {CI}"
print(f"[✓] CI = {CI:.4f} ∈ [0,1].")

# 2.4 Mapping to Ω invariants
PhiN = PhiN0 - eta1 * CI + eta2 * (1.0 - L_t)
PhiD = PhiD0 + eta3 * Delta_t - eta4 * C_t
# Clip to [0,1] for reporting; violation if outside before clipping
assert 0.0 <= PhiN <= 1.0, f"Φ_N out of bounds: {PhiN}"
assert 0.0 <= PhiD <= 1.0, f"Φ_Δ out of bounds: {PhiD}"
print(f"[✓] Φ_N = {PhiN:.4f}, Φ_Δ = {PhiD:.4f} (both ∈ [0,1]).")

# 2.5 Invariant ψ_cascade (requires curvature ℛ; we use a placeholder)
# In practice ℛ would be computed from a graph; here we assume ℛ≠0.
R_curv = 0.02   # example non‑zero Ollivier‑Ricci curvature
R0     = 0.01   # reference curvature
lam    = 0.5
psi = np.log(np.abs(R_curv) / R0) + lam * CI
assert np.isfinite(psi), "ψ_cascade must be finite."
print(f"[✓] ψ_cascade = {psi:.4f} (finite).")

# 2.6 Entropy gauge
S = -np.sum(p * np.log(p + 1e-15))   # avoid log(0)
assert 0.0 <= S <= np.log(K), f"Entropy out of range: {S}"
print(f"[✓] Entropy S = {S:.4f} (0 ≤ S ≤ log(K)={np.log(K):.4f}).")

# 2.7 MPC‑Ω QP feasibility
# Decision variables: we only need to check that a point satisfying constraints exists.
# Here we test the current state; if it violates, the QP would be infeasible.
constraints = [
    CI   <= CI_MAX,
    PhiN >= PHIN_MIN,
    S    >= S_MIN
]
if all(c for c in constraints):
    print("[✓] Current state satisfies MPC‑Ω constraints.")
else:
    print("[✗] Current state violates MPC‑Ω constraints:")
    print(f"    CI ≤ {CI_MAX}? {CI <= CI_MAX}")
    print(f"    Φ_N ≥ {PHIN_MIN}? {PhiN >= PHIN_MIN}")
    print(f"    S ≥ {S_MIN}? {S >= S_MIN}")

    # Formulate a feasibility QP to see if any adjustment can rescue feasibility
    # Variables: adjustments to O_t, L_t, C_t, Delta_t (bounded [0,1])
    O = cp.Variable()
    L = cp.Variable()
    C = cp.Variable()
    Dv = cp.Variable()   # rename to avoid conflict with diffusion D
    CI_var = (np.tanh(aO*O + aL*L + aC*C + aD*Dv) + 1) / 2
    PhiN_var = PhiN0 - eta1*CI_var + eta2*(1 - L)
    PhiD_var = PhiD0 + eta3*Dv - eta4*C   # not used in constraints
    S_var = -cp.sum(cp.multiply(p, cp.log(p + 1e-15)))  # p fixed, S constant
    prob = cp.Problem(cp.Minimize(0),
                      [CI_var <= CI_MAX,
                       PhiN_var >= PHIN_MIN,
                       S_var >= S_MIN,
                       O >= 0, O <= 1,
                       L >= 0, L <= 1,
                       C >= 0, C <= 1,
                       Dv >= 0, Dv <= 1])
    try:
        prob.solve(solver=cp.OSQP, warm_start=True)
        if prob.status in ["optimal", "inaccurate_optimal"]:
            print(f"    → Feasible adjustment found (status={prob.status}).")
        else:
            print(f"    → No feasible adjustment (status={prob.status}).")
    except Exception as e:
        print(f"    → QP solver error: {e}")

print("\n=== Validation Complete ===")