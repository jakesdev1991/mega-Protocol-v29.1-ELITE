# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Smith – Omega Protocol Validation for Information‑Cascade Monitor (IC‑Ω)

This script checks:
  * double‑well potential sign (α < 0)
  * CI bounds [0,1]
  * mapped Φ_N, Φ_Δ stay inside Omega‑allowed ranges
  * entropy gauge S_cascade ≥ log(3)
  * MPC‑Ω QP constraints (CI ≤ 0.7, Φ_N ≥ 0.6, S ≥ log(3))
  * Quadratic cost J is non‑negative
  * (Optional) Symbolic verification that δS/δ𝕀 yields the reaction‑diffusion‑advection PDE.
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# 1. USER‑DEFINED PARAMETERS (these would be calibrated in practice)
# ----------------------------------------------------------------------
# Double‑well coefficients (must satisfy α < 0 for bistability)
alpha = -0.5   # <-- MUST BE NEGATIVE
beta  = 2.0
gamma = 1.0    # linear tilt, can be any real

# CI weighting (should be non‑negative and sum to 1 for interpretability)
w_O, w_L, w_C, w_Delta = 0.25, 0.25, 0.25, 0.25
assert np.isclose(w_O + w_L + w_C + w_Delta, 1.0), "Weights must sum to 1"

# Linear mapping coefficients from CI & raw metrics to Omega invariants
#   Φ_N = Φ_N0 - η1*CI + η2*(1-L)
#   Φ_Δ = Φ_Δ0 + η3*Δ - η4*C
Phi_N0, Phi_Delta0 = 0.8, 0.2   # baseline Omega values (chosen within safe region)
eta1, eta2, eta3, eta4 = 0.3, 0.1, 0.25, 0.15

# MPC‑Ω constraint thresholds
CI_MAX   = 0.7
PHI_N_MIN = 0.6
ENTROPY_MIN = np.log(3)   # ≈1.0986

# Cost‑function weights (must be >0)
mu1, mu2, mu3 = 1.0, 1.0, 1.0

# ----------------------------------------------------------------------
# 2. SYNTHETIC DATA GENERATOR (for demonstration)
# ----------------------------------------------------------------------
def generate_synthetic_data(n_samples=1000, seed=42):
    rng = np.random.default_rng(seed)
    # Order‑imbalance O ∈ [0,1]
    O = rng.beta(2, 5, size=n_samples)          # skewed towards low imbalance
    # Liquidity withdrawal L ∈ [0,1] (fractional depth loss)
    L = rng.beta(1, 4, size=n_samples)
    # Cross‑ETF correlation C ∈ [-1,1] → shift to [0,1] for CI
    C_raw = rng.normal(0, 0.3, size=n_samples)
    C = np.clip((C_raw + 1) / 2, 0, 1)          # now in [0,1]
    # Trader‑response skew Δ ∈ [-2,2] → shift to [0,1]
    Delta_raw = rng.laplace(0, 0.5, size=n_samples)
    Delta = np.clip((Delta_raw + 2) / 4, 0, 1)  # now in [0,1]
    return O, L, C, Delta

O, L, C, Delta = generate_synthetic_data()

# ----------------------------------------------------------------------
# 3. CASCADE INTENSITY INDEX (CI)
# ----------------------------------------------------------------------
def compute_CI(O, L, C, Delta):
    arg = w_O*O + w_L*L + w_C*C + w_Delta*Delta
    # tanh maps ℝ → (-1,1); shift+scale to [0,1]
    CI = (np.tanh(arg) + 1) / 2
    return CI

CI = compute_CI(O, L, C, Delta)

# ----------------------------------------------------------------------
# 4. MAP CI & RAW METRICS → OMEGA INVARIANTS
# ----------------------------------------------------------------------
Phi_N_casc = Phi_N0 - eta1*CI + eta2*(1 - L)
Phi_Delta_casc = Phi_Delta0 + eta3*Delta - eta4*C

# ----------------------------------------------------------------------
# 5. ENTROPY GAUGE (participant‑type volume shares)
# ----------------------------------------------------------------------
def entropy_from_shares(shares):
    # shares: array-like, sums to 1
    p = np.asarray(shares, dtype=float)
    p = p[p > 0]               # avoid log(0)
    return -np.sum(p * np.log(p))

# Example: three trader types (HFT, Inst, Retail) with volume fractions
# We'll derive them from CI as a toy model: higher CI → more HFT activity
p_HFT = 0.2 + 0.4*CI          # baseline 0.2, up to 0.6
p_Inst = 0.5 - 0.2*CI         # baseline 0.5, down to 0.3
p_Retail = 1.0 - p_HFT - p_Inst
shares = np.vstack([p_HFT, p_Inst, p_Retail]).T   # shape (n_samples,3)

S_cascade = np.apply_along_axis(entropy_from_shares, 1, shares)

# ----------------------------------------------------------------------
# 6. INVARIANT & CONSTRAINT CHECKS
# ----------------------------------------------------------------------
def check_double_well():
    """α must be < 0 for a true double‑well."""
    return alpha < 0

def check_CI_bounds():
    return np.all(CI >= 0) and np.all(CI <= 1)

def check_Phi_N_range():
    return np.all(Phi_N_casc >= PHI_N_MIN)

def check_Phi_Delta_range():   # Omega does not prescribe a hard bound, but we keep it reasonable
    return np.all(Phi_Delta_casc >= 0) and np.all(Phi_Delta_casc <= 1)

def check_entropy_bound():
    return np.all(S_cascade >= ENTROPY_MIN)

def check_MPC_constraints():
    cond1 = np.all(CI <= CI_MAX)
    cond2 = np.all(Phi_N_casc >= PHI_N_MIN)
    cond3 = np.all(S_cascade >= ENTROPY_MIN)
    return cond1 and cond2 and cond3

def compute_cost():
    """Quadratic penalty J (integral approximated by mean over samples)."""
    term1 = np.mean(np.maximum(CI - 0.6, 0.0)**2)
    term2 = mu1 * np.mean(np.maximum(0.6 - Phi_N_casc, 0.0)**2)
    term3 = mu2 * np.mean(Phi_Delta_casc**2)
    term4 = mu3 * np.mean(np.maximum(ENTROPY_MIN - S_cascade, 0.0)**2)
    return term1 + term2 + term3 + term4

# ----------------------------------------------------------------------
# 7. (Optional) Symbolic verification of Euler‑Lagrange → PDE
# ----------------------------------------------------------------------
def symbolic_EulerLagrange():
    """Return the Euler‑Lagrange equation for the scalar field 𝕀."""
    # Define symbols
    t, x, y, z = sp.symbols('t x y z', real=True)
    I = sp.Function('I')(t, x, y, z)
    D, vx, vy, vz, kappa, Imax = sp.symbols('D vx vy vz kappa Imax', real=True)
    rho, zeta = sp.symbols('rho zeta', real=True)

    # Lagrangian density L = 0.5*g^{μν}∂_μ I ∂_ν I - V(I)  (note sign convention)
    # For flat Minkowski with metric signature (+,-,-,-): g^{00}=1, g^{ii}=-1
    L = 0.5*(sp.diff(I, t)**2 - sp.diff(I, x)**2 - sp.diff(I, y)**2 - sp.diff(I, z)**2) \
        - (alpha/2)*I**2 - (beta/4)*I**4 + gamma*I

    # Euler‑Lagrange: ∂L/∂I - ∂_μ(∂L/∂(∂_μ I)) = 0
    EL = sp.diff(L, I) - sp.diff(sp.diff(L, sp.diff(I, t)), t) \
                     + sp.diff(sp.diff(L, sp.diff(I, x)), x) \
                     + sp.diff(sp.diff(L, sp.diff(I, y)), y) \
                     + sp.diff(sp.diff(L, sp.diff(I, z)), z)

    # Substitute source terms ρ + ζ and diffusion/advection:
    # We manually rewrite EL to match the PDE:
    #   ∂_t I = D∇² I - v·∇ I + κ I (1 - I/Imax) + ρ + ζ
    # Here we set D=1, v=(vx,vy,vz) for illustration.
    PDE = sp.Eq(sp.diff(I, t),
                D*(sp.diff(I, x, x) + sp.diff(I, y, y) + sp.diff(I, z, z))
                - (vx*sp.diff(I, x) + vy*sp.diff(I, y) + vz*sp.diff(I, z))
                + kappa*I*(1 - I/Imax) + rho + zeta)
    return sp.simplify(EL - PDE.lhs + PDE.rhs)  # should be zero if identities hold

# ----------------------------------------------------------------------
# 8. REPORT
# ----------------------------------------------------------------------
report = []
report.append("=== Ω‑Protocol Validation Report ===")
report.append(f"Double‑well sign (α < 0):          {check_double_well()}")
report.append(f"CI ∈ [0,1] :                       {check_CI_bounds()}")
report.append(f"Φ_N^{casc} ≥ {PHI_N_MIN} :          {check_Phi_N_range()}")
report.append(f"Φ_Δ^{casc} ∈ [0,1] :               {check_Phi_Delta_range()}")
report.append(f"Entropy S ≥ log(3) :               {check_entropy_bound()}")
report.append(f"MPC‑Ω QP constraints satisfied:    {check_MPC_constraints()}")
report.append(f"Quadratic cost J (mean over samples): {compute_cost():.6f}")
report.append("")
report.append("Symbolic EL‑PDE residual (should be 0):")
report.append(str(symbolic_EulerLagrange()))
report.append("")
report.append("=== End of Report ===")

print("\n".join(report))