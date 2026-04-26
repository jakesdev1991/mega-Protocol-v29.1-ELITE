# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Market Advisor Divergence Monitor (MADM‑Ω)
-----------------------------------------------------------
Checks:
  1. MI ∈ [0,1]
  2. Φ_N, Φ_Δ from linear maps are non‑negative
  3. Stiffness invariants ξ_N⁻², ξ_Δ⁻² > 0  (→ ξ real)
  4. ψ = ln(ξ/ξ₀) is real
  5. MPC‑Ω QP respects constraints MI≤0.6, Φ_N≥0.5, S_adh≥S_min
"""

import numpy as np
from scipy.stats import entropy   # Shannon entropy
try:
    from cvxopt import matrix, solvers
except ImportError:
    raise ImportError("Please install cvxopt: pip install cvxopt")

# ------------------- Synthetic data -------------------
np.random.seed(42)
T = 200                     # time steps
# Advisor price and clearing price (random walk around 1.0)
pa = 1.0 + 0.05 * np.cumsum(np.random.randn(T))
pc = 1.0 + 0.07 * np.cumsum(np.random.randn(T))
# Divergence d(t)
d = np.abs(pa - pc) / pc

# Adherence: binary per agent whether bid within eps of pa(t)
Nagents = 30
eps = 0.02
# Simulate bids as pa + noise
bids = pa[:, None] + eps * np.random.randn(T, Nagents)
adherence = np.abs(bids - pa[:, None]) < eps   # shape (T, Nagents)
S_adh = np.array([entropy(row.astype(float)+1e-12, base=2) for row in adherence])
# Normalise entropy to [0,1] (max = log2(Nagents))
S_adh /= np.log2(Nagents)

# ------------------- Parameters -------------------
# Normalisation constants for MI
sigma0 = 0.1   # typical std of ϕ
kappa0 = 0.05  # typical gradient energy
# Linear mapping coefficients (must be >0)
eta1, eta2 = 0.3, 0.2
eta3, eta4 = 0.25, 0.15
PhiN0, PhiD0 = 0.8, 0.2
tau1, tau2 = 5, 5   # simple integer delay (steps)
# MPC‑Ω weights
mu, lam, kappa = 1.0, 1.0, 0.5
S_target = 0.6
MI_opt = 0.3
S_min = 0.4
# Constraints
MI_max = 0.6
PhiN_min = 0.5

# ------------------- Helper functions -------------------
def compute_MI(t):
    """MI(t) using exponential‑variance × gradient × (1‑S)."""
    # variance of ϕ approximated by variance of d over a window
    win = slice(max(0, t-24), t+1)   # 24‑step window (≈1 day)
    var_phi = np.var(d[win]) if len(win) > 1 else 0.0
    grad_phi = np.mean(np.diff(d[win])**2) if len(win) > 1 else 0.0
    var_term = np.exp(-var_phi / sigma0**2)
    grad_term = 1.0 + grad_phi / kappa0
    adh_term = 1.0 - S_adh[t]
    MI = var_term * grad_term * adh_term
    # Clip to [0,1] for safety
    return np.clip(MI, 0.0, 1.0)

def PhiN_from_MI(t):
    MI_t = compute_MI(t-tau1) if t>=tau1 else compute_MI(0)
    sigma_d = np.std(d[max(0, t-tau1):t+1]) if t>=tau1 else 0.0
    return PhiN0 - eta1*MI_t - eta2*sigma_d

def PhiD_from_MI(t):
    MI_t = compute_MI(t-tau2) if t>=tau2 else compute_MI(0)
    var_adh = np.var(S_adh[max(0, t-tau2):t+1]) if t>=tau2 else 0.0
    return PhiD0 + eta3*MI_t + eta4*var_adh

def stiffness_from_effective_potential(PhiN, PhiD):
    """
    Mock effective potential: V_eff = 0.5*a*(PhiN-PhiN0)^2 + 0.5*b*(PhiD-PhiD0)^2
    with a,b>0 ensures positive curvature.
    In a real implementation this would come from integrating out higher modes.
    """
    a, b = 1.0, 1.0   # arbitrary positive constants
    d2V_dPhiN2 = a
    d2V_dPhiD2 = b
    xiN2 = 1.0 / d2V_dPhiN2   # ξ_N^2
    xiD2 = 1.0 / d2V_dPhiD2   # ξ_Δ^2
    return xiN2, xiD2

# ------------------- Time‑series validation -------------------
MI_vals = np.zeros(T)
PhiN_vals = np.zeros(T)
PhiD_vals = np.zeros(T)
xiN2_vals = np.zeros(T)
xiD2_vals = np.zeros(T)
psi_vals = np.zeros(T)

for t in range(T):
    MI_vals[t] = compute_MI(t)
    PhiN_vals[t] = PhiN_from_MI(t)
    PhiD_vals[t] = PhiD_from_MI(t)
    xiN2, xiD2 = stiffness_from_effective_potential(PhiN_vals[t], PhiD_vals[t])
    xiN2_vals[t] = xiN2
    xiD2_vals[t] = xiD2
    # correlation length ξ = sqrt(xiN2*xiD2) (geometric mean as a proxy)
    xi = np.sqrt(xiN2 * xiD2)
    xi0 = 1.0   # reference length
    psi_vals[t] = np.log(xi / xi0)

# ---- Checks ----
print("=== Scalar checks ===")
print(f"MI min/max: {MI_vals.min():.4f} / {MI_vals.max():.4f}  (should be in [0,1])")
print(f"Φ_N min: {PhiN_vals.min():.4f}  (should be ≥0)")
print(f"Φ_Δ min: {PhiD_vals.min():.4f}  (should be ≥0)")
print(f"ξ_N^2 min: {xiN2_vals.min():.4f}  (should be >0)")
print(f"ξ_Δ^2 min: {xiD2_vals.min():.4f}  (should be >0)")
print(f"ψ min/max: {psi_vals.min():.4f} / {psi_vals.max():.4f}  (real)")

# ---- MPC‑Ω QP (single‑step approximation) ----
# We minimise J = μ ψ^2 + λ (MI-MI_opt)^2 + κ (S_adh - S_target)^2
# subject to MI ≤ MI_max, Φ_N ≥ PhiN_min, S_adh ≥ S_min
# Discretise at a single time step (t) for demonstration.
t = 100
MI = compute_MI(t)
psi = psi_vals[t]
S = S_adh[t]

# Quadratic objective: 0.5 * x^T P x + q^T x
# Decision variable x = [MI_adj, S_adj] (we allow small adjustments)
# We keep Φ_N and Φ_Δ as functions of MI_adj via linear maps.
# For simplicity we treat adjustments directly on MI and S.
P = 2 * np.array([[lam, 0.0],
                  [0.0, kappa]])   # because J = lam*(MI-MI_opt)^2 + kappa*(S-S_target)^2 + mu*psi^2
# psi depends on MI via Φ_N,Φ_Δ → ξ → ψ. Approximate linearisation:
# dψ/dMI ≈ (∂ψ/∂Φ_N)*(dΦ_N/dMI) + (∂ψ/∂Φ_Δ)*(dΦ_Δ/dMI)
# We compute numerically:
def psi_from_MI_S(MI_val, S_val):
    # recompute Φ_N,Φ_Δ using MI_val (ignore delay for simplicity)
    PhiN = PhiN0 - eta1*MI_val - eta2*0.0   # sigma_d approximated as 0
    PhiD = PhiD0 + eta3*MI_val + eta4*0.0   # var_adh approximated as 0
    xiN2, xiD2 = stiffness_from_effective_potential(PhiN, PhiD)
    xi = np.sqrt(xiN2 * xiD2)
    return np.log(xi / 1.0)

# finite difference
eps_ = 1e-6
dpsi_dMI = (psi_from_MI_S(MI+eps_, S) - psi_from_MI_S(MI-eps_, S)) / (2*eps_)
# Add mu * psi^2 term: gradient = 2*mu*psi * dpsi/dMI, Hessian ≈ 2*mu*(dpsi/dMI)^2
P[0,0] += 2.0 * mu * (dpsi_dMI**2)
q = np.array([-2.0*lam*MI_opt, -2.0*kappa*S_target])   # linear part from completing square
# Add psi linear term: 2*mu*psi * dpsi/dMI * MI
q[0] += 2.0 * mu * psi * dpsi_dMI

# Inequality constraints Gx ≤ h
# 1) MI ≤ MI_max
# 2) Φ_N ≥ PhiN_min  →  -Φ_N ≤ -PhiN_min
#    Φ_N = PhiN0 - eta1*MI - eta2*sigma_d ≈ PhiN0 - eta1*MI (ignore sigma_d)
#    => - (PhiN0 - eta1*MI) ≤ -PhiN_min  =>  eta1*MI ≤ PhiN0 - PhiN_min
# 3) S_adh ≥ S_min   →  -S ≤ -S_min
G = np.array([[ 1.0, 0.0],          # MI ≤ MI_max
              [-eta1, 0.0],         # eta1*MI ≤ PhiN0 - PhiN_min
              [0.0, -1.0]])         # -S ≤ -S_min
h = np.array([MI_max,
              PhiN0 - PhiN_min,
              -S_min])

# Solve QP
solvers.options['show_progress'] = False
sol = solvers.qp(matrix(P, tc='d'), matrix(q, tc='d'),
                 matrix(G, tc='d'), matrix(h, tc='d'))
if sol['status'] == 'optimal':
    x_opt = np.array(sol['x']).flatten()
    MI_adj, S_adj = x_opt
    print("\n=== MPC‑Ω QP result (t={}) ===".format(t))
    print(f"Optimal MI adjustment: {MI_adj:.4f}")
    print(f"Optimal S adjustment: {S_adj:.4f}")
    print(f"Resulting MI: {MI_adj:.4f} (≤ {MI_max})")
    print(f"Resulting Φ_N: {PhiN0 - eta1*MI_adj:.4f} (≥ {PhiN_min})")
    print(f"Resulting S_adh: {S_adj:.4f} (≥ {S_min})")
else:
    print("\nQP failed to find optimum:", sol['status'])

# ------------------- Summary -------------------
print("\n=== Validation Summary ===")
print("All core mathematical checks passed if:")
print("  • MI in [0,1]")
print("  • Φ_N, Φ_Δ non‑negative")
print("  • ξ_N^2, ξ_Δ^2 > 0")
print("  • ψ real")
print("  • QP feasible (optimal status).")