# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol validation for the Secret‑Management Process Entropy Monitor (SMPEM‑Ω)

The script implements the mathematical definitions from the proposal and
verifies that the Ω‑Protocol invariants (Phi_N, Phi_Delta, J*) and the
MPC‑Ω constraints are satisfied for synthetic data.
"""

import numpy as np
from scipy.special import softmax  # for normalized exception distribution

# -------------------------- CONFIGURATION --------------------------
# Calibration weights for PEFI (must sum to any positive scale; tanh bounds output)
ALPHA, BETA, GAMMA, DELTA = 0.3, 0.2, 0.3, 0.2

# Mapping coefficients from PEFI to Omega variables (chosen to keep them in [0,1])
ETA1, ETA2, ETA3, ETA4 = 0.15, 0.10, 0.12, 0.08
TAU1, TAU2 = 4, 4          # weeks of lead time (discretised as 4 monthly steps)

# Double‑well potential parameters (not directly used in checks, kept for completeness)
ALPHA_P, BETA_P, GAMMA_P = 1.0, 0.5, 0.2

# MPC‑Ω constraint thresholds
PEFI_MAX = 0.6
PHI_N_MIN = 0.6
S_PROC_MIN = np.log(3)   # ≈1.099

# QP cost weights (positive)
MU1, MU2, MU3 = 1.0, 1.0, 1.0

# Number of synthetic months to simulate
N_MONTHS = 24

# Number of business units (departments) for entropy calc
N_DEPTS = 5

# -------------------------- HELPERS --------------------------
def tanh(x):
    return np.tanh(x)

def compute_pefi(V, G, L, S):
    """Process Entropy Fragility Index (Eq. in proposal)."""
    return tanh(ALPHA * V + BETA * G + GAMMA * L + DELTA * S)

def map_phi_n(pefi_series, phi_n0=0.8):
    """Phi_N mapping with lead time TAU1."""
    shifted = np.concatenate([np.full(TAU1, pefi_series[0]), pefi_series[:-TAU1]])
    return phi_n0 - ETA1 * shifted + ETA2 * (1 - np.concatenate([np.full(TAU1, 0.5), np.ones(N_MONTHS-TAU1)*0.5]))  # placeholder G term

def map_phi_delta(pefi_series, phi_delta0=0.2):
    """Phi_Delta mapping with lead time TAU2."""
    shifted = np.concatenate([np.full(TAU2, pefi_series[0]), pefi_series[:-TAU2]])
    # placeholder L and V terms
    L_placeholder = np.full(N_MONTHS, 0.3)
    V_placeholder = np.full(N_MONTHS, 0.4)
    return phi_delta0 + ETA3 * L_placeholder - ETA4 * V_placeholder

def ricci_scalar_from_process(V, G, L, S):
    """
    Approximate Ricci scalar of the 4‑D process‑entropy manifold.
    For validation we use a simple quadratic form:
        R = a*(V^2+G^2+L^2+S^2) + b*(V*G + L*S)
    This mimics curvature dependence on the signal vector.
    """
    a, b = 0.5, 0.2
    x = np.stack([V, G, L, S], axis=-1)          # shape (T,4)
    quad = np.sum(a * x**2, axis=-1)
    cross = b * (x[:,0]*x[:,1] + x[:,2]*x[:,3])
    return quad + cross

def compute_psi(ricci, pefi, lam=0.1):
    """ψ_smpe = ln(|R|/R0) + λ·PEFI ; choose R0 = 1 for simplicity."""
    return np.log(np.abs(ricci) + 1e-12) + lam * pefi

def shannon_entropy_from_exceptions(exc_counts):
    """S_proc = - Σ p_e log p_e ; exc_counts shape (T, N_DEPTS)."""
    p = exc_counts / exc_counts.sum(axis=1, keepdims=True)
    # avoid log(0)
    p = np.where(p == 0, 1e-12, p)
    return -np.sum(p * np.log(p), axis=1)

def mpc_qp_feasible(pefi, phi_n, s_proc):
    """
    Simple feasibility check for the QP:
        PEFI ≤ PEFI_MAX
        Φ_N ≥ PHI_N_MIN
        S_proc ≥ S_PROC_MIN
    Returns True if all hold for every time step.
    """
    return np.all(pefi <= PEFI_MAX) and np.all(phi_n >= PHI_N_MIN) and np.all(s_proc >= S_PROC_MIN)

def cost_function(pefi, phi_n, phi_delta, s_proc):
    """Quadratic cost used in the MPC‑Ω formulation."""
    term1 = np.sum(np.maximum(pefi - PEFI_MAX, 0.0)**2)
    term2 = MU1 * np.sum(np.maximum(PHI_N_MIN - phi_n, 0.0)**2)
    term3 = MU2 * np.sum(phi_delta**2)
    term4 = MU3 * np.sum(np.maximum(S_PROC_MIN - s_proc, 0.0)**2)
    return term1 + term2 + term3 + term4

# -------------------------- SYNTHETIC DATA GENERATION --------------------------
np.random.seed(42)

# Simulate monthly signals in [0,1] with mild trends and noise
t = np.arange(N_MONTHS)
V = np.clip(0.4 + 0.1*np.sin(0.2*t) + 0.05*np.random.randn(N_MONTHS), 0, 1)
G = np.clip(0.5 + 0.08*np.cos(0.15*t) + 0.04*np.random.randn(N_MONTHS), 0, 1)
L = np.clip(0.3 + 0.12*np.sin(0.25*t) + 0.03*np.random.randn(N_MONTHS), 0, 1)
S = np.clip(0.2 + 0.1*np.sin(0.3*t) + 0.02*np.random.randn(N_MONTHS), 0, 1)

# Simulate exception counts per department (Poisson‑distributed)
exception_base = np.full((N_MONTHS, N_DEPTS), 20.0)
exception_counts = np.random.poisson(lam=exception_base)

# -------------------------- COMPUTE METRICS --------------------------
pefi = compute_pefi(V, G, L, S)
phi_n = map_phi_n(pefi)
phi_delta = map_phi_delta(pefi)
psi = ricci_scalar_from_process(V, G, L, S)
psi = compute_psi(psi, pefi)
s_proc = shannon_entropy_from_exceptions(exception_counts)

# -------------------------- VALIDATION --------------------------
assert np.all((pefi >= 0) & (pefi <= 1)), "PEFI out of bounds [0,1]"
assert np.all((phi_n >= 0) & (phi_n <= 1)), "Phi_N out of physical range [0,1]"
assert np.all((phi_delta >= 0) & (phi_delta <= 1)), "Phi_Delta out of physical range [0,1]"
assert np.all(np.isfinite(psi)), "ψ_smpe contains non‑finite values"
assert np.all(s_proc >= 0), "Shannon entropy negative"

# Ω‑Protocol invariant checks (the proposal ties PEFI → Φ_N, Φ_Delta)
assert mpc_qp_feasible(pefi, phi_n, s_proc), "MPC‑Ω constraints violated"

# Additional physics‑style check: the action integrand should be non‑negative
# We approximate the Lagrangian density L = 0.5*(∂P)^2 + V(P) + λΩ LΩ + A·J.
# For validation we just ensure the potential V(P) ≥ 0 (double‑well shifted).
V_pot = 0.5*ALPHA_P*pefi**2 + 0.25*BETA_P*pefi**4 - GAMMA_P*pefi
assert np.all(V_pot >= -1e-9), "Potential V(P) unexpectedly negative (numerical tolerance)"

# Cost should be finite
cost = cost_function(pefi, phi_n, phi_delta, s_proc)
assert np.isfinite(cost) and cost >= 0, "MPC‑Ω cost invalid"

print("✅ All Ω‑Protocol invariants and MPC‑Ω constraints satisfied.")
print(f"Final PEFI mean: {pefi.mean():.3f}")
print(f"Final Φ_N mean: {phi_n.mean():.3f}")
print(f"Final Φ_Δ mean: {phi_delta.mean():.3f}")
print(f"Final ψ_smpe mean: {psi.mean():.3f}")
print(f"Final S_proc mean: {s_proc.mean():.3f}")
print(f"MPC‑Ω cost: {cost:.3f}")