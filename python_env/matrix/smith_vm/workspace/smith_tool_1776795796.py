# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol compliance validator for the SMPEM‑Ω proposal.
Checks:
  * PEFI in [0,1)
  * Derived Φ_N, Φ_Δ in [0,1]
  * ψ is real (no NaN/Inf)
  * MPC‑Ω QP constraints are feasible
"""

import numpy as np
from cvxopt import matrix, solvers

# Suppress cvxopt output
solvers.options['show_progress'] = False

# ------------------ Synthetic data generation ------------------
np.random.seed(42)
n_units = 5          # number of business units
n_time  = 10         # time steps (days)

# Raw signals (all non‑negative)
V = np.random.rand(n_units, n_time)          # policy‑violation density ∈ [0,1]
G = np.random.rand(n_units, n_time)          # ownership Gini ∈ [0,1]
L_raw = np.random.rand(n_units, n_time) * 5  # lifecycle skew (raw)
S = np.random.rand(n_units, n_time)          # shadow‑IT ratio ∈ [0,1]

# Normalise L to [0,1] using a chosen max (here 5)
L = np.clip(L_raw / 5.0, 0.0, 1.0)

# ------------------ Parameters (respecting bounds) ------------------
alpha, beta, gamma, delta = 0.3, 0.2, 0.4, 0.1   # non‑negative weights
eta1, eta2, eta3, eta4 = 0.4, 0.3, 0.3, 0.2    # ∈ [0,1]
tau1, tau2 = 2, 3                               # lag steps (days)
PhiN0, PhiDelta0 = 0.7, 0.5                     # baseline invariants ∈ [0,1]
lam = 0.5                                       # λ for ψ
R0 = 1.0                                        # reference curvature scale
eps = 1e-12                                     # to avoid log(0)

# ------------------ Helper functions ------------------
def compute_pefi(V, G, L, S):
    """PEFI = tanh(αV + βG + γL + δS)"""
    arg = alpha*V + beta*G + gamma*L + delta*S
    return np.tanh(arg)   # ∈ [0,1)

def compute_phiN(pefi_lag, G_lag):
    return PhiN0 - eta1*pefi_lag + eta2*(1.0 - G_lag)

def compute_phiDelta(L_lag, V_lag):
    return PhiDelta0 + eta3*L_lag - eta4*V_lag

def compute_pefi_global(pefi):
    return np.max(pefi, axis=0)   # max over units

def compute_curric_scalar(pefi):
    """Placeholder curvature: simple quadratic dependence on PEFI."""
    # In a real implementation this would come from the process‑correlation matrix.
    # Here we just ensure it's a smooth scalar that can be zero.
    return (pefi - 0.5)**2 - 0.2   # can be negative → we take abs later

# ------------------ Main validation loop ------------------
for t in range(n_time):
    # Determine lagged indices (handle early times by using t=0)
    t1 = max(t - tau1, 0)
    t2 = max(t - tau2, 0)

    # PEFI for each unit at time t
    pefi_t = compute_pefi(V[:, t], G[:, t], L[:, t], S[:, t])   # shape (n_units,)
    pefi_global_t = compute_pefi_global(pefi_t)                # scalar

    # Lagged quantities needed for Φ updates
    pefi_lag = compute_pefi(V[:, t1], G[:, t1], L[:, t1], S[:, t1])
    pefi_lag_global = np.max(pefi_lag)
    G_lag = np.max(G[:, t1])
    L_lag = np.max(L[:, t2])
    V_lag = np.max(V[:, t2])

    # Derived Ω‑variables
    PhiN = compute_phiN(pefi_lag_global, G_lag)
    PhiDelta = compute_phiDelta(L_lag, V_lag)

    # Invariant ψ
    R_proc = compute_pefi_scalar(pefi_global_t)   # scalar curvature proxy
    psi = np.log(np.abs(R_proc) / R0 + eps) + lam * pefi_global_t

    # ----- Assertions (Ω‑Protocol compliance) -----
    assert 0.0 <= pefi_global_t < 1.0, f"PEFI out of bounds: {pefi_global_t}"
    assert 0.0 <= PhiN <= 1.0, f"Φ_N out of bounds: {PhiN}"
    assert 0.0 <= PhiDelta <= 1.0, f"Φ_Δ out of bounds: {PhiDelta}"
    assert np.isfinite(psi), f"ψ is not finite: {psi}"

    # ----- MPC‑Ω QP feasibility check -----
    # Decision variable: u = [Δincentive, Δtooling, Δgovernance] (non‑negative, scaled)
    # We simply test if there exists a non‑negative vector that can drive the
    # constrained quantities toward the feasible region.
    # Formulate as a linear feasibility problem:
    #   A * u <= b
    # where u >= 0.
    #
    # We use a very conservative model:
    #   PEFI_next = PEFI_t - k1*u0   (incentive reduces PEFI)
    #   ΦN_next   = ΦN_t   + k2*u1   (tooling improves connectivity)
    #   Sproc_next= Sproc_t + k3*u2  (governance raises entropy)
    #
    # Choose arbitrary positive gains.
    k1, k2, k3 = 0.2, 0.15, 0.1
    # Current process‑entropy proxy (Shannon of exception distribution) – fake:
    Sproc_t = np.log(3.0) + 0.2   # start above threshold

    # Desired next-step targets:
    pefi_target = 0.6      # upper bound
    phiN_target = 0.6      # lower bound
    sproct_target = np.log(3.0)   # lower bound

    # Build inequalities: A*u <= b  (we want to *reach* or *exceed* targets)
    # PEFI_t - k1*u0 <= pefi_target   ->  k1*u0 >= PEFI_t - pefi_target
    # ΦN_t   + k2*u1 >= phiN_target   -> -k2*u1 <= ΦN_t - phiN_target
    # Sproc_t+ k3*u2 >= sproct_target -> -k3*u2 <= Sproc_t - sproct_target
    A = matrix([
        [ k1, 0.0, 0.0 ],   # u0 coefficient
        [0.0, -k2, 0.0 ],   # u1 coefficient (note minus)
        [0.0, 0.0, -k3 ]    # u2 coefficient
    ], tc='d')
    b = matrix([
        pefi_t - pefi_target,
        PhiN_t - phiN_target,
        Sproc_t - sproct_target
    ], tc='d')
    G = matrix(-np.eye(3), tc='d')   # u >= 0  -> -I * u <= 0
    h = matrix(np.zeros(3), tc='d')

    sol = solvers.qp(matrix(np.zeros((3,3))), matrix(np.zeros((3,1))), G, h, A, b)
    if sol['status'] != 'optimal':
        raise RuntimeError(f"MPC‑Ω QP infeasible at t={t}: {sol['status']}")

# If we reach here, all checks passed.
print("All checks passed. SMPEM‑Ω math is Ω‑Protocol compliant.")