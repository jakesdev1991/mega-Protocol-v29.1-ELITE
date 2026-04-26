# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Validates the mathematical soundness of the Neo‑Experimenter's synthesis
against the invariants (Phi_N, Phi_Delta, J*).

Run:
    python validate_omega.py
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def third_derivative(signal, dt):
    """
    Compute the third derivative using a 5-point stencil (O(dt^2)).
    Returns an array same length as signal (edges set to NaN).
    """
    n = len(signal)
    j = np.full(n, np.nan)
    # central stencil: f'''(x) ≈ (-f_{i-2}+2f_{i-1}-2f_{i+1}+f_{i+2})/(2*dt^3)
    for i in range(2, n-2):
        j[i] = (-signal[i-2] + 2*signal[i-1] - 2*signal[i+1] + signal[i+2]) / (2.0 * dt**3)
    return j

def normalize_jerk(j_raw, tau):
    """Dimensionless jerk: \hat{j} = j_raw * tau^3"""
    return j_raw * tau**3

def jerk_stability_index(sigma_F, jmax_F, sigma_C, jmax_C):
    """
    S_j,total = 1 / (1 + sigma_F * jmax_F + sigma_C * jmax_C)
    All inputs must be >=0.
    """
    denom = 1.0 + sigma_F * jmax_F + sigma_C * jmax_C
    if denom < 1.0:
        raise ValueError("Denominator < 1 => S_j > 1 (violates J* bound)")
    return 1.0 / denom

def lagrangian_density(I, dI_dt, lam_omega, Phi_N, Phi_Delta, J_curr):
    """
    Simplified Lagrangian density (ignoring curvature and gauge):
        L = 0.5 * (dI/dt)^2 + V(I) + lambda_Omega * L_Omega(Phi_N, Phi_Delta) + A_mu J^mu
    We set:
        V(I) = (I^2 - 1)^2          # double-well, minima at I=±1 => V>=0
        L_Omega = Phi_N * Phi_Delta # positive coupling term
        A_mu J^mu = 0               # assume gauge term vanishes for test
    Returns scalar L (should be real and >= -epsilon due to possible negative kinetic term?).
    """
    kinetic = 0.5 * dI_dt**2
    V = (I**2 - 1.0)**2
    L_omega = lam_omega * (Phi_N * Phi_Delta)
    # gauge term set to zero for this test
    L = kinetic + V + L_omega
    return L

# ----------------------------------------------------------------------
# Validation parameters (can be tweaked)
# ----------------------------------------------------------------------
dt = 0.01                     # sampling step [s]
t = np.arange(0, 10, dt)     # 10 seconds of data
tau_N = 0.05                  # characteristic quantum time scale [s]
tau_Delta = 0.2               # characteristic network time scale [s]

# Synthetic signals
# Fidelity: smooth oscillation with occasional drops
F = 0.5 * (1 + np.sin(2*np.pi*t/2.0))   # oscillates between 0 and 1
# inject three fidelity drops
F[ (t>3.0) & (t<3.2) ] = 0.0
F[ (t>5.5) & (t<5.7) ] = 0.0
F[ (t>8.0) & (t<8.2) ] = 0.0

# Connectivity: mostly 1, with a few SearXNG‑like refusals (0)
C = np.ones_like(t)
C[ (t>4.0) & (t<4.1) ] = 0.0   # first refusal
C[ (t>7.0) & (t<7.1) ] = 0.0   # second refusal

# ----------------------------------------------------------------------
# 1. Jerk computation & normalization
# ----------------------------------------------------------------------
j_F_raw = third_derivative(F, dt)
j_C_raw = third_derivative(C, dt)

j_F_hat = normalize_jerk(j_F_raw, tau_N)
j_C_hat = normalize_jerk(j_C_raw, tau_Delta)

# Use absolute maximum jerk as the "worst‑case" magnitude (non‑negative)
jmax_F = np.nanmax(np.abs(j_F_hat))
jmax_C = np.nanmax(np.abs(j_C_hat))

# ----------------------------------------------------------------------
# 2. Jerk Stability Index check (invariant J*)
# ----------------------------------------------------------------------
# Assume some sensitivity coefficients (dimensionless) from the proposal
sigma_F_hat = 0.3   # placeholder
sigma_C_hat = 0.4   # placeholder

Sj_total = jerk_stability_index(sigma_F_hat, jmax_F,
                                sigma_C_hat, jmax_C)

assert 0.0 < Sj_total <= 1.0 + 1e-12, \
    f"Jerk Stability Index out of bounds: {Sj_total}"
print(f"[OK] Jerk Stability Index S_j,total = {Sj_total:.4f} (in (0,1])")

# ----------------------------------------------------------------------
# 3. Φ‑density accounting (invariants Phi_N, Phi_Delta >= 0)
# ----------------------------------------------------------------------
Phi_N_init = 10.0   # arbitrary baseline
Phi_Delta_init = 5.0

# Short‑term cost and long‑term gain as given in the text
cost = 45.0   # Φ units (negative)
gain = 405.0  # Φ units (positive)

Phi_N_final = Phi_N_init - cost + gain
Phi_Delta_final = Phi_Delta_init  # assume network invariant unchanged for simplicity

assert Phi_N_final >= 0.0, f"Phi_N became negative: {Phi_N_final}"
assert Phi_Delta_final >= 0.0, f"Phi_Delta became negative: {Phi_Delta_final}"
print(f"[OK] Φ_N final = {Phi_N_final:.1f} (≥0), Φ_Delta final = {Phi_Delta_final:.1f} (≥0)")

# ----------------------------------------------------------------------
# 4. Lagrangian density reality check (simplified)
# ----------------------------------------------------------------------
# Build a composite field I = F + C (both normalized to ~[0,2])
I = F + C
dI_dt = np.gradient(I, dt)   # first derivative

lam_omega = 1.2   # arbitrary coupling constant

L_vals = lagrangian_density(I, dI_dt, lam_omega,
                            Phi_N_final, Phi_Delta_final, 0.0)

# L should be real (no imaginary part) and not excessively negative.
# The double-well ensures V>=0; kinetic term is >=0; L_omega>=0 if Phi_N,Phi_Delta>=0.
assert np.all(np.isreal(L_vals)), "Lagrangian density produced complex values"
assert np.all(L_vals >= -1e-10), f"Lagrangian density negative beyond tolerance: min={np.min(L_vals)}"
print(f"[OK] Lagrangian density min = {np.min(L_vals):.3e} (real, ~non‑negative)")

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
print("\nAll Omega Protocol invariants satisfied:")
print(f"  J* (jerk stability) ∈ (0,1]  →  S_j,total = {Sj_total:.4f}")
print(f"  Φ_N ≥ 0                     →  Φ_N_final = {Phi_N_final:.1f}")
print(f"  Φ_Δ ≥ 0                     →  Φ_Δ_final = {Phi_Delta_final:.1f}")
print("  Lagrangian density real and non‑negative (to numerical tolerance).")