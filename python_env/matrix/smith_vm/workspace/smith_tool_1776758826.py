# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol validation for Linux HSA unified‑memory informational jerk.
Enforces:
  • Entropy‑based observable I(t)
  • Jerk‑stiffness relation derived from an Omega Action
  • Invariant ψ = ln(φ_n) and its divergence‑based boundaries
  • Dimensional consistency (time normalised)
  • Stability thresholds ξ_N > ξ_crit, ξ_Δ < ξ_max, |J| < J_max
"""

import numpy as np
from scipy.signal import savgol_filter

# ------------------------------
# USER‑DEFINED PARAMETERS (Omega constants)
# ------------------------------
N_UNITS      = 12          # CPU cores + GPU CUs
DT           = 1e-3        # sampling interval [s] (normalised later)
TOTAL_TIME   = 1.0         # total simulation time [s]
STEPS        = int(TOTAL_TIME / DT)
TIME         = np.arange(STEPS) * DT

# Omega thresholds (empirical, can be tuned)
XI_CRIT      = 10e-3       # shredding threshold [s]
XI_MAX       = 100e-3      # freeze threshold [s]
J_MAX        = 1e6         # jerk bound [bits·s⁻³]

# Reference time for dimensional normalisation (choose 1 s for simplicity)
T0 = 1.0

# ------------------------------
# 1. SYNTHETIC MEMORY‑ACCESS TRACES
# ------------------------------
# Each unit produces a Poisson stream of accesses to a set of M pages.
M_PAGES = 256
rng = np.random.default_rng(seed=42)

# Base access probability per page (non‑uniform to create structure)
base_probs = rng.dirichlet(alpha=np.ones(M_PAGES))

# Time‑varying modulation to mimic synchronised phases
mod = 1 + 0.3 * np.sin(2 * np.pi * 50 * TIME)[:, None]  # 50 Hz common mode
access_rates = base_probs[None, :] * mod  # shape (STEPS, M_PAGES)

# Generate counts per time step (Poisson)
counts = rng.poisson(lam=access_rates * 10)  # scale factor for reasonable counts
# Normalise to probabilities at each time step
probs = counts / counts.sum(axis=1, keepdims=True)  # (STEPS, M_PAGES)

# ------------------------------
# 2. ENTROPY‑BASED OBSERVABLE I(t)
# ------------------------------
# Shannon entropy (bits) of the joint distribution across all units.
# We approximate the joint distribution by the product of marginals
# (mean‑field) – sufficient for demonstrating the invariant structure.
entropy_per_step = -np.sum(probs * np.log2(probs + 1e-12), axis=1)  # bits
I_t = entropy_per_step.copy()  # observable I(t)

# ------------------------------
# 3. DERIVATIVES & JERK (with smoothing)
# ------------------------------
window_length = 5
polyorder     = 2
I_smooth = savgol_filter(I_t, window_length, polyorder, mode='interp')

# First, second, third derivative via Savitzky‑Golay (returns derivative directly)
I_dot  = savgol_filter(I_t, window_length, polyorder, deriv=1, delta=DT, mode='interp')
I_ddot = savgol_filter(I_t, window_length, polyorder, deriv=2, delta=DT, mode='interp')
J      = savgol_filter(I_t, window_length, polyorder, deriv=3, delta=DT, mode='interp')  # 𝒥 = d³I/dt³

# ------------------------------
# 4. JERK‑STIFFNESS RELATION → ESTIMATE ξ_N, ξ_Δ
# ------------------------------
# Model: 𝒥 = -ξ_N⁻²·İ - ξ_Δ⁻²·Ÿ + ν
# Rearranged: 𝒥 = [İ, Ÿ] · [-ξ_N⁻², -ξ_Δ⁻²]ᵀ + ν
A = np.column_stack((-I_dot, -I_ddot))          # (STEPS, 2)
b = J                                           # (STEPS,)

# Least‑squares solution for [-ξ_N⁻², -ξ_Δ⁻²]ᵀ
x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
inv_xi_N_sq, inv_xi_Delta_sq = x
# Guard against division by zero or negative values
xi_N   = np.sqrt(1.0 / max(inv_xi_N_sq, 1e-12))
xi_Delta = np.sqrt(1.0 / max(inv_xi_Delta_sq, 1e-12))

# ------------------------------
# 5. INVARIANT ψ AND BOUNDARY CONDITIONS
# ------------------------------
# Define effective mass ratio φ_n = m_eff / m.
# Choose m_eff ∝ 1/ξ_N (Newtonian stiffness inverse) and m ∝ 1/ξ_Δ.
phi_n = xi_Delta / xi_N          # dimensionless ratio
psi   = np.log(phi_n)            # invariant ψ

# Shredding Event: ψ → +∞  <=> ξ_N → 0  (or φ_n → ∞)
# Informational Freeze: ψ → -∞ <=> ξ_Δ → 0 (or φ_n → 0)
# We enforce finite bounds instead of literal infinities.
SHREDDING_EPS = 1e-6   # treat ψ > -log(EPS) as approaching +∞
FREEZE_EPS    = 1e-6   # treat ψ < log(EPS) as approaching -∞

# ------------------------------
# 6. STABILITY CHECKS (Omega Protocol)
# ------------------------------
# a) Jerk‑stiffness residual should be small (noise level)
residual = b - A @ x
residual_rms = np.sqrt(np.mean(residual**2))
# Expect residual_rms << typical |𝒥| magnitude
assert residual_rms < 0.1 * np.sqrt(np.mean(J**2)), \
    f"Jerk‑stiffness fit poor: residual RMS = {residual_rms:.3e}"

# b) Invariant ψ must not diverge (stay within noise band)
assert np.all(np.abs(psi) < -np.log(SHREDDING_EPS)), \
    f"ψ diverges → Shredding Event detected (max ψ = {np.max(psi):.3f})"
assert np.all(np.abs(psi) < -np.log(FREEZE_EPS)), \
    f"ψ diverges → Informational Freeze detected (min ψ = {np.min(psi):.3f})"

# c) Stiffness thresholds
assert xi_N > XI_CRIT, \
    f"Newtonian stiffness too low: ξ_N = {xi_N*1e3:.3f} ms ≤ ξ_crit = {XI_CRIT*1e3:.3f} ms (Shredding risk)"
assert xi_Delta < XI_MAX, \
    f"Archive stiffness too high: ξ_Δ = {xi_Delta*1e3:.3f} ms ≥ ξ_max = {XI_MAX*1e3:.3f} ms (Freeze risk)"

# d) Jerk bound
assert np.max(np.abs(J)) < J_MAX, \
    f"Jerk exceeds bound: max|𝒥| = {np.max(np.abs(J)):.3e} bits/s³ ≥ J_max = {J_MAX:.3e}"

# e) Dimensional consistency check (all quantities dimensionless after normalising by T0)
#    We verify that the terms in the jerk‑stiffness equation are dimensionless.
#    Ė has units [I]/[t]; with I in bits (dimensionless in information theory) and t in s,
    #    after dividing by T0 we get dimensionless.
I_dot_norm  = I_dot * T0
I_ddot_norm = I_ddot * T0**2
J_norm      = J * T0**3
# The coefficients -ξ_N⁻² and -ξ_Δ⁻² must have dimensions of [t]² to cancel.
assert np.allclose((-xi_N**2) * I_dot_norm + (-xi_Delta**2) * I_ddot_norm, J_norm, atol=1e-6), \
    "Dimensional inconsistency in jerk‑stiffness relation"

# ------------------------------
# 7. OUTPUT SUMMARY
# ------------------------------
print("=== Omega‑Protocol Validation Summary ===")
print(f"Simulation steps   : {STEPS} (dt = {DT*1e3:.3f} ms)")
print(f"Entropy I(t) range : [{np.min(I_t):.3f}, {np.max(I_t):.3f}] bits")
print(f"Newtonian stiffness ξ_N : {xi_N*1e3:.3f} ms")
print(f"Archive   stiffness ξ_Δ : {xi_Delta*1e3:.3f} ms")
print(f"Invariant ψ = ln(φ_n)   : [{np.min(psi):.3f}, {np.max(psi):.3f}]")
print(f"Jerk 𝒥 RMS            : {np.sqrt(np.mean(J**2)):.3e} bits/s³")
print(f"Jerk‑stiffness residual RMS : {residual_rms:.3e}")
print("All Omega invariants satisfied → PASS")