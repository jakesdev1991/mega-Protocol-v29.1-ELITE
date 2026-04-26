# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IC‑Ω Mathematical Soundness Validator
-------------------------------------
Checks that the proposed cascade model respects:
  * CI ∈ [0,1]
  * Φ_N^{casc} ∈ [0,1]   (Omega connectivity invariant)
  * Φ_Δ^{casc} ∈ [-1,1]  (Omega asymmetry invariant)
  * CI ≤ 0.7, Φ_N^{casc} ≥ 0.6, S ≥ log(3)
  * Cost function formulation
"""

import numpy as np

# ----------------------------------------------------------------------
# User‑definable parameters (tune these to match your Omega spec)
# ----------------------------------------------------------------------
ALPHA, BETA, GAMMA, DELTA = 0.4, 0.3, 0.2, 0.1   # weights in CI (must sum ≤1 for safety)
ETA_N1, ETA_N2 = 0.25, 0.15                     # Φ_N mapping
ETA_D3, ETA_D4 = 0.2, 0.1                       # Φ_Δ mapping
PHI_N0, PHI_D0 = 0.8, 0.0                       # baseline Omega variables
TAU = 10                                          # lead‑time steps (discrete)
LAMBDA = 0.5                                      # curvature‑CI coupling
R0 = 1.0                                          # reference curvature scale
# ----------------------------------------------------------------------


def ci_from_signals(O, L, C, Delta):
    """
    Raw CI = tanh(αO+βL+γC+δΔ).  Then shift/scale to [0,1].
    """
    raw = np.tanh(ALPHA * O + BETA * L + GAMMA * C + DELTA * Delta)
    # map (-1,1) -> (0,1)
    return (raw + 1.0) / 2.0


def map_phi_n(ci_hist, L_hist):
    """
    Φ_N^{casc}(t) = Φ_N0 - η_N1 * CI(t-τ) + η_N2 * (1 - L(t-τ))
    """
    ci_delayed = np.roll(ci_hist, TAU)
    L_delayed = np.roll(L_hist, TAU)
    phi = PHI_N0 - ETA_N1 * ci_delayed + ETA_N2 * (1.0 - L_delayed)
    # enforce first TAU steps as baseline (no info yet)
    phi[:TAU] = PHI_N0
    return np.clip(phi, 0.0, 1.0)   # Omega connectivity ∈ [0,1]


def map_phi_delta(ci_hist, Delta_hist, C_hist):
    """
    Φ_Δ^{casc}(t) = Φ_Δ0 + η_D3 * Δ(t-τ) - η_D4 * C(t-τ)
    """
    Delta_delayed = np.roll(Delta_hist, TAU)
    C_delayed = np.roll(C_hist, TAU)
    phi = PHI_D0 + ETA_D3 * Delta_delayed - ETA_D4 * C_delayed
    phi[:TAU] = PHI_D0
    return np.clip(phi, -1.0, 1.0)  # Omega asymmetry ∈ [-1,1]


def invariant_psi(curvature, ci_val):
    """
    ψ = ln(|ℛ|/ℛ₀) + λ·CI
    """
    if curvature == 0.0:
        raise ValueError("Curvature ℛ must be non‑zero for log.")
    return np.log(np.abs(curvature) / R0) + LAMBDA * ci_val


def entropy_from_shares(shares):
    """
    S = -∑ p_k log p_k   (natural log)
    """
    # guard against zeros
    p = np.asarray(shares, dtype=float)
    p = p[p > 0]
    return -np.sum(p * np.log(p))


def mpc_constraints_violated(ci, phi_n, S):
    """
    Returns a dict of booleans: True => violation.
    """
    violations = {
        "CI_le_0p7": np.any(ci > 0.7),
        "PhiN_ge_0p6": np.any(phi_n < 0.6),
        "Entropy_ge_log3": np.any(S < np.log(3))
    }
    return violations


def quadratic_cost(ci, phi_n, phi_delta, S,
                   mu1=1.0, mu2=1.0, mu3=1.0):
    """
    J = ∫ [ (CI-0.6)_+² + μ1(0.6-Φ_N)_+² + μ2 Φ_Δ² + μ3(log(3)-S)_+² ] dt
    Here we approximate the integral by a simple sum over discrete time.
    """
    term1 = np.sum(np.maximum(ci - 0.6, 0.0) ** 2)
    term2 = mu1 * np.sum(np.maximum(0.6 - phi_n, 0.0) ** 2)
    term3 = mu2 * np.sum(phi_delta ** 2)
    term4 = mu3 * np.sum(np.maximum(np.log(3) - S, 0.0) ** 2)
    return term1 + term2 + term3 + term4


# ----------------------------------------------------------------------
# Example synthetic data (replace with real feeds in production)
# ----------------------------------------------------------------------
np.random.seed(42)
T = 100                     # time steps
O = np.random.uniform(0, 1, T)               # order‑imbalance
L = np.random.uniform(0, 1, T)               # liquidity‑withdrawal proxy
C = np.random.uniform(0, 1, T)               # max absolute correlation
Delta = np.random.uniform(-2, 2, T)          # skewness (can be negative/positive)

# Trader‑type volume shares (3 types for simplicity)
shares = np.random.dirichlet(alpha=[1.0, 1.0, 1.0], size=T)  # shape (T,3)

# ----------------------------------------------------------------------
# Run validation
# ----------------------------------------------------------------------
CI = ci_from_signals(O, L, C, Delta)
PhiN = map_phi_n(CI, L)
PhiD = map_phi_delta(CI, Delta, C)

# Example curvature (use a dummy time‑varying scalar; in practice compute from graph)
curvature = np.random.uniform(0.5, 2.0, T)   # never zero
PSI = invariant_psi(curvature, CI)

S = np.array([entropy_from_shares(shares[t]) for t in range(T)])

violations = mpc_constraints_violated(CI, PhiN, S)
cost = quadratic_cost(CI, PhiN, PhiD, S)

print("=== IC‑Ω Validation Report ===")
print(f"Time steps: {T}")
print(f"CI range: [{CI.min():.3f}, {CI.max():.3f}]")
print(f"Φ_N range: [{PhiN.min():.3f}, {PhiN.max():.3f}]")
print(f"Φ_Δ range: [{PhiD.min():.3f}, {PhiD.max():.3f}]")
print(f"S range: [{S.min():.3f}, {S.max():.3f}]")
print(f"ψ range: [{PSI.min():.3f}, {PSI.max():.3f}]")
print("\nConstraint violations:")
for k, v in violations.items():
    print(f"  {k}: {'VIOLATION' if v else 'OK'}")
print(f"\nQuadratic cost J ≈ {cost:.3f}")

# ----------------------------------------------------------------------
# Optional: auto‑fix suggestions
# ----------------------------------------------------------------------
if violations["CI_le_0p7"]:
    print("\nNote: CI exceeded 0.7 – consider clipping CI or reducing Δ weight.")
if violations["PhiN_ge_0p6"]:
    print("Note: Φ_N dropped below 0.6 – increase η_N2 or raise baseline Φ_N0.")
if violations["Entropy_ge_log3"]:
    print("Note: Trader‑type entropy too low – promote more balanced volume shares.")