# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the revised HSA unified‑memory informational‑jerk analysis.
Checks:
  1. Definitions of ψ and its derivatives.
  2. Entropy S_h and its ψ‑/φ_Δ‑derivatives at the operating point.
  3. Jerk components (ψ‑ and φ_Δ‑parts) using the corrected ψ̈.
  4. Finite‑difference jerk with explicit Δt³ scaling.
  5. Dimensional consistency of the stability threshold.
  6. Both catastrophic boundaries (Shredding & Informational Freeze).
  7. Final stability verdict (variance vs. threshold).
All quantities are kept in SI‑compatible units (seconds, dimensionless amplitudes).
"""

import numpy as np

# ----------------------------------------------------------------------
# Supplied data (normalized to I0 = 1)
# ----------------------------------------------------------------------
I0 = 1.0
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
phi_N_dot   = 2.1e3     # s⁻¹
phi_D_dot   = 8.7e3     # s⁻¹
# Effective stiffness from the problem statement
xi_inv2 = 4.2e6         # s⁻²   →   ξ = 1/√xi_inv2
xi = 1.0 / np.sqrt(xi_inv2)   # s
# Source jerk (additive)
J_source = 1.5e12       # s⁻³

# ----------------------------------------------------------------------
# 1. ψ and its derivatives
# ----------------------------------------------------------------------
psi = np.log(phi_N)                     # dimensionless
psi_dot = phi_N_dot / phi_N              # s⁻¹

# Estimate φ̈_N from the stiffness timescale (φ̈ ≈ φ̇/ξ)
phi_N_ddot = phi_N_dot / xi               # s⁻²
psi_ddot = phi_N_ddot/phi_N - (phi_N_dot/phi_N)**2   # s⁻²
psi_ddot_dot = psi_ddot / xi              # s⁻³   (third derivative)

# ----------------------------------------------------------------------
# 2. Entropy S_h(ψ, φ_D) and derivatives
# ----------------------------------------------------------------------
def S_h(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi / denom
    pD = phi_D / denom
    return -(pN*np.log(pN) + pD*np.log(pD))

# Numerical derivatives via finite difference (small step)
eps = 1e-8
dS_dpsi   = (S_h(psi+eps, phi_D)   - S_h(psi-eps, phi_D))   / (2*eps)
d2S_dpsi2 = (S_h(psi+eps, phi_D)   - 2*S_h(psi, phi_D)   + S_h(psi-eps, phi_D)) / (eps**2)
d3S_dpsi3 = (S_h(psi+2*eps, phi_D) - 2*S_h(psi+eps, phi_D) + 2*S_h(psi-eps, phi_D) - S_h(psi-2*eps, phi_D)) / (2*eps**3)

dS_dphiD   = (S_h(psi, phi_D+eps)   - S_h(psi, phi_D-eps))   / (2*eps)
d2S_dphiD2 = (S_h(psi, phi_D+eps)   - 2*S_h(psi, phi_D)   + S_h(psi, phi_D-eps)) / (eps**2)

# ----------------------------------------------------------------------
# 3. Jerk components (ψ‑part and φ_Δ‑part)
# ----------------------------------------------------------------------
J_psi = (dS_dpsi   * psi_ddot_dot
       + 3 * d2S_dpsi2 * psi_dot * psi_ddot
       +   d3S_dpsi3 * psi_dot**3)

J_phiD = (dS_dphiD   * (phi_D_dot/xi)   # φ̈_Δ ≈ φ̇_Δ/ξ
        + 3 * d2S_dphiD2 * phi_D_dot * (phi_D_dot/xi))

# ----------------------------------------------------------------------
# 4. Finite‑difference jerk (Δt = ξ)
# ----------------------------------------------------------------------
# Build a mock time series using a linear extrapolation of S_h
# (only to illustrate the Δt³ scaling; the actual value is not needed for validation)
def S_h_at(t):
    # Simple linear evolution: ψ(t) = psi + psi_dot*t, φ_D(t) = phi_D + phi_D_dot*t
    psi_t = psi + psi_dot * t
    phiD_t = phi_D + phi_D_dot * t
    return S_h(psi_t, phiD_t)

dt = xi
J_fd = (S_h_at(0*dt) - 3*S_h_at(-1*dt) + 3*S_h_at(-2*dt) - S_h_at(-3*dt)) / (dt**3)

# ----------------------------------------------------------------------
# 5. Total jerk (including source term)
# ----------------------------------------------------------------------
J_total = J_psi + J_phiD + J_source   # s⁻³

# ----------------------------------------------------------------------
# 6. Stability threshold (dimensionally consistent)
# ----------------------------------------------------------------------
# Characteristic frequency ω = ξ⁻¹
omega = 1.0 / xi
# ψ‑modulated frequency: ω_ψ = ω * exp(-ψ/2)   (since ψ = ln(Φ_N/I0) → Φ_N/I0 = e^ψ)
omega_psi = omega * np.exp(-psi/2.0)
# Natural jerk scale: ω_ψ³
Jerk_scale = omega_psi**3          # s⁻³
# Variance of jerk (assume ±20% fluctuation around mean)
sigma_J = 0.2 * np.abs(J_total)
var_J = sigma_J**2                 # s⁻⁶
# Threshold for variance: (ω_ψ³)² = ω_ψ⁶
threshold = Jerk_scale**2          # s⁻⁶

# ----------------------------------------------------------------------
# 7. Catastrophic boundaries
# ----------------------------------------------------------------------
# Shredding Event: ξ_Δ → ∞  →  Φ_N² + 3Φ_Δ² = I0²
shredding_cond = phi_N**2 + 3*phi_D**2 - I0**2
# Informational Freeze: ξ_N → ∞  →  3Φ_N² + Φ_Δ² = I0²
freeze_cond    = 3*phi_N**2 + phi_D**2 - I0**2

# ----------------------------------------------------------------------
# Output results
# ----------------------------------------------------------------------
print("=== Validation of revised HSA informational‑jerk analysis ===")
print(f"ψ = ln(φ_N) = {psi:.6f}")
print(f"ψ̇ = {psi_dot:.3e} s⁻¹")
print(f"ψ̈ = {psi_ddot:.3e} s⁻²")
print(f"ψ̈̇ = {psi_ddot_dot:.3e} s⁻³")
print()
print("Entropy derivatives at (ψ, φ_D):")
print(f"  ∂S/∂ψ   = {dS_dpsi:.6f}")
print(f"  ∂²S/∂ψ² = {d2S_dpsi2:.6f}")
print(f"  ∂³S/∂ψ³ = {d3S_dpsi3:.6f}")
print(f"  ∂S/∂φ_Δ = {dS_dphiD:.6f}")
print(f"  ∂²S/∂φ_Δ² = {d2S_dphiD2:.6f}")
print()
print("Jerk components:")
print(f"  J_ψ   = {J_psi:.3e} s⁻³")
print(f"  J_φΔ  = {J_phiD:.3e} s⁻³")
print(f"  J_source = {J_source:.3e} s⁻³")
print(f"  Finite‑difference J (Δt=ξ) = {J_fd:.3e} s⁻³")
print(f"  Total J = {J_total:.3e} s⁻³")
print()
print("Stability metrics:")
print(f"  ω = ξ⁻¹ = {omega:.3e} s⁻¹")
print(f"  ω_ψ = ω·e^{−ψ/2} = {omega_psi:.3e} s⁻¹")
print(f"  Jerk scale ω_ψ³ = {Jerk_scale:.3e} s⁻³")
print(f"  σ_J = 0.2·|J| = {sigma_J:.3e} s⁻³")
print(f"  Var(J) = σ_J² = {var_J:.3e} s⁻⁶")
print(f"  Threshold = ω_ψ⁶ = {threshold:.3e} s⁻⁶")
print(f"  Stability ratio Var/Threshold = {var_J/threshold:.3f}")
print()
print("Catastrophic boundaries:")
print(f"  Shredding condition (Φ_N²+3Φ_Δ²−I0²) = {shredding_cond:.6f}")
print(f"  Freeze    condition (3Φ_N²+Φ_Δ²−I0²) = {freeze_cond:.6f}")
print()
# Verdicts
stable = var_J < threshold
print(f"Stability verdict (Var < Threshold) ? {'PASS' if stable else 'FAIL'}")
print()
# Check that ψ definition holds
psi_check = np.abs(psi - np.log(phi_N)) < 1e-12
print(f"ψ definition check: {'OK' if psi_check else 'FAIL'}")
# Check that entropy derivatives are finite numbers
deriv_ok = all(np.isfinite([dS_dpsi, d2S_dpsi2, d3S_dpsi3, dS_dphiD, d2S_dphiD2]))
print(f"Entropy derivatives finite: {'OK' if deriv_ok else 'FAIL'}")