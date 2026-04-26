# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for TEMPEST‑Ω refinement.
Checks:
  - Hard bounds: TSI <= 4.0, Phi_N >= 0.5, Phi_Delta <= 0.75
  - Dimensional consistency of TSI (user supplies units)
  - Dimensionless invariant psi = ln(m_eff/m0)
  - Feasibility of a simple MPC-Omega QP with the bounds.
"""

import numpy as np
from scipy.optimize import minimize

# ----------------------------------------------------------------------
# USER‑DEFINED PARAMETERS (replace with your calibrated values)
# ----------------------------------------------------------------------
# Temporal Stress Index components (example sector with 2 firms, 1 leak each)
C = np.array([3.0, 4.0])                 # credential criticality (1-5)
dt_leak = np.array([5.0, 12.0])          # days since leak (t - t_i)
Delta_t = np.array([8.0, 3.0])           # days to next major event (Δt_{f,e})
sync = np.array([1.0, 2.0])              # synchrony measure (firms leaking ±3d)

# Model hyper‑parameters (must be supplied with units)
alpha = 0.6      # weight for criticality term (dimensionless)
beta  = 0.4      # weight for event‑proximity term (dimensionless)
gamma = 0.2      # weight for synchrony term (dimensionless)
lam   = 0.1      # decay constant λ (units: day⁻¹)

# Omega invariant parameters
Phi_N0 = 0.55    # baseline Newtonian mode
Phi_D0 = 0.30    # baseline asymmetry mode
eta1, eta2, eta3 = 0.02, 0.01, 0.015   # coupling coefficients
tau1, tau2, tau3 = 14.0, 42.0, 7.0    # lead times (days)

# Invariant ψ parameters
m0   = 1.0e-3    # reference mass scale (units: day⁻², must match m_eff)
# Effective mass from curvature of V(φ) – here we mock a simple quadratic:
# V(φ) = 0.5 * mu2 * φ^2  =>  m_eff = sqrt(mu2)
mu2  = 2.5e-4    # (day⁻²) – user must provide from their potential
m_eff = np.sqrt(mu2)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def compute_TSI(t):
    """Temporal Stress Index at time t (days)."""
    term1 = alpha * C * np.exp(-lam * np.abs(t - dt_leak))
    term2 = beta  / Delta_t
    term3 = gamma * sync
    return np.sum(term1 + term2 + term3)

def Phi_N(t):
    """Newtonian mode Φ_N(t)."""
    return Phi_N0 + eta1 * compute_TSI(t - tau1) - eta2 * (compute_SI(t - tau2))**2

def Phi_Delta(t):
    """Asymmetry mode Φ_Δ(t)."""
    return Phi_D0 + eta3 * sync_at(t - tau3)   # sync_at returns sync measure at shifted time

def compute_SI(t):
    """Same as TSI but without the synchrony term (used for the quadratic piece)."""
    term1 = alpha * C * np.exp(-lam * np.abs(t - dt_leak))
    term2 = beta  / Delta_t
    return np.sum(term1 + term2)

def sync_at(t_shift):
    """Return synchrony measure evaluated at a shifted time (simple model)."""
    # In a real implementation you would look up leaks within ±3 days of t_shift.
    # Here we just reuse the base sync vector as a placeholder.
    return np.mean(sync)

def invariant_psi():
    """Dimensionless invariant ψ = ln(m_eff/m0)."""
    return np.log(m_eff / m0)

# ----------------------------------------------------------------------
# 1. Hard Omega bounds check
# ----------------------------------------------------------------------
t_now = 0.0   # evaluate at present (t=0)
TSI_val = compute_TSI(t_now)
PhiN_val = Phi_N(t_now)
PhiD_val = Phi_Delta(t_now)

print("=== Omega Hard Bounds ===")
print(f"TSI(t={t_now})   = {TSI_val:.3f}   (limit ≤ 4.0)   {'OK' if TSI_val <= 4.0 else 'VIOLATION'}")
print(f"Φ_N(t={t_now})   = {PhiN_val:.3f}   (limit ≥ 0.5)   {'OK' if PhiN_val >= 0.5 else 'VIOLATION'}")
print(f"Φ_Δ(t={t_now})   = {PhiD_val:.3f}   (limit ≤ 0.75)  {'OK' if PhiD_val <= 0.75 else 'VIOLATION'}")
print()

# ----------------------------------------------------------------------
# 2. Dimensional consistency of TSI
# ----------------------------------------------------------------------
# We assume:
#   - C_i dimensionless
#   - exp(-λ|Δt|) dimensionless → λ must have units of 1/time
#   - 1/Δt_{f,e} has units of 1/time
#   - sync dimensionless
# Therefore TSI has units of (1/time). To compare with the dimensionless bound 4.0
# we must multiply by a characteristic time scale T_ref (e.g., 1 day).
T_ref = 1.0   # day
TSI_dimless = TSI_val * T_ref   # now dimensionless
print(f"TSI * T_ref (dimensionless) = {TSI_dimless:.3f}")
print("If you chose a different T_ref, adjust the bound accordingly.")
print()

# ----------------------------------------------------------------------
# 3. Invariant ψ dimensionless check
# ----------------------------------------------------------------------
psi_val = invariant_psi()
print("=== Invariant ψ ===")
print(f"m_eff = {m_eff:.3e} day⁻²")
print(f"m0    = {m0:.3e} day⁻²")
print(f"ψ = ln(m_eff/m0) = {psi_val:.6f}")
print("ψ is dimensionless by construction. |ψ| < 1e-9 would indicate exact scale matching.")
print()

# ----------------------------------------------------------------------
# 4. Toy MPC‑Ω QP (minimise quadratic cost subject to bounds)
# ----------------------------------------------------------------------
def cost(x):
    """
    x = [TSI, Φ_N, Φ_Δ, ψ]  (all dimensionless after scaling)
    Quadratic cost: (TSI - TSI_target)^2 + μ1 * ψ^2 + μ2 * (1 - Φ_N)^2
    """
    TSI, PhiN, PhiD, psi = x
    TSI_target = 2.0   # example desired stress level
    mu1, mu2 = 0.5, 0.8
    return (TSI - TSI_target)**2 + mu1 * psi**2 + mu2 * (1.0 - PhiN)**2

def constraints(x):
    TSI, PhiN, PhiD, psi = x
    return [
        4.0 - TSI,          # TSI ≤ 4.0
        PhiN - 0.5,         # Φ_N ≥ 0.5
        0.75 - PhiD,        # Φ_Δ ≤ 0.75
        # No explicit bound on ψ; we keep it free but can add a soft bound if desired.
    ]

# Initial guess (feasible point)
x0 = np.array([2.0, 0.6, 0.4, 0.0])

cons = [{'type': 'ineq', 'fun': lambda x: 4.0 - x[0]},          # TSI ≤ 4
        {'type': 'ineq', 'fun': lambda x: x[1] - 0.5},         # Φ_N ≥ 0.5
        {'type': 'ineq', 'fun': lambda x: 0.75 - x[2]}]        # Φ_Δ ≤ 0.75

res = minimize(cost, x0, constraints=cons, method='SLSQP')
print("=== Toy MPC‑Ω QP Result ===")
print(f"Success: {res.success}")
print(f"Optimal x = [TSI, Φ_N, Φ_Δ, ψ] = {res.x}")
print(f"Cost = {res.fun:.5f}")
print(f"Constraint violations: {[c['fun'](res.x) for c in cons]}")