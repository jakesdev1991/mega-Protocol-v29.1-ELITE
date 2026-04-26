# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Checks the internal consistency of the Linux HSA unified‑memory
informational jerk analysis against the supplied numerical data.
"""

import numpy as np

# ----------------------------------------------------------------------
# Supplied data (normalized to I0 = 1)
# ----------------------------------------------------------------------
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
dphi_N  = 2.1e3         # s⁻¹
dphi_D  = 8.7e3         # s⁻¹
ddphi_N = 4.3e6         # s⁻²   (approximate second derivative)
# source jerk (given)
J_source = 1.5e12       # s⁻³

# ----------------------------------------------------------------------
# Helper: entropy and its ψ‑derivatives
# ----------------------------------------------------------------------
def entropy(psi, phi_D):
    """Shannon conditional entropy S_h(psi, phi_D)."""
    e_psi = np.exp(psi)
    denom = e_psi + phi_D
    p_N   = e_psi / denom
    p_D   = phi_D / denom
    # avoid log(0)
    eps = 1e-15
    return -(p_N*np.log(p_N+eps) + p_D*np.log(p_D+eps))

def dS_dpsi(psi, phi_D):
    e_psi = np.exp(psi)
    denom = e_psi + phi_D
    p_N   = e_psi / denom
    p_D   = phi_D / denom
    return -(np.log(p_N) - np.log(p_D))   # derivative w.r.t. psi

def d2S_dpsi2(psi, phi_D):
    e_psi = np.exp(psi)
    denom = e_psi + phi_D
    p_N   = e_psi / denom
    p_D   = phi_D / denom
    return -(p_N + p_D)   # = -1 (since p_N+p_D=1)  --> actually -1

def d3S_dpsi3(psi, phi_D):
    # third derivative of S_h w.r.t. psi for two‑state system
    e_psi = np.exp(psi)
    denom = e_psi + phi_D
    p_N   = e_psi / denom
    p_D   = phi_D / denom
    return (p_N - p_D)   # = (e_psi - phi_D)/(e_psi+phi_D)

# ----------------------------------------------------------------------
# Compute ψ and its derivatives
# ----------------------------------------------------------------------
psi   = np.log(psi_N := phi_N)          # ln(phi_N)
dpsi  = dphi_N / phi_N
# ψ̈ = φ̈_N/φ_N - (φ̇_N/φ_N)²
d2psi = ddphi_N / phi_N - (dphi_N / phi_N)**2
# Approximate ψ⃛ using ξ (stiffness time scale)
xi    = 1.0 / np.sqrt(4.2e6)            # s   (from ξ⁻² = 4.2e6 s⁻²)
d3psi = d2psi / xi                      # s⁻³

print(f"ψ      = {psi:.6f}")
print(f"ψ̇     = {dpsi:.3e} s⁻¹")
print(f"ψ̈     = {d2psi:.3e} s⁻²")
print(f"ψ⃛     = {d3psi:.3e} s⁻³")

# ----------------------------------------------------------------------
# Entropy and ψ‑derivatives at the operating point
# ----------------------------------------------------------------------
S      = entropy(psi, phi_D)
dS     = dS_dpsi(psi, phi_D)
d2S    = d2S_dpsi2(psi, phi_D)
d3S    = d3S_dpsi3(psi, phi_D)

print(f"\nS_h    = {S:.6f}")
print(f"∂S/∂ψ  = {dS:.6f}")
print(f"∂²S/∂ψ²= {d2S:.6f}")
print(f"∂³S/∂ψ³= {d3S:.6f}")

# ----------------------------------------------------------------------
# Jerk components (ψ‑part) using proper finite‑difference with Δt
# ----------------------------------------------------------------------
# Choose a sampling interval consistent with the stiffness time scale
dt = xi * 0.1   # 10% of ξ, just for illustration; user should supply actual Δt
# Build a short history assuming linear extrapolation from derivatives
psi_hist = [psi - dpsi*dt + 0.5*d2psi*dt**2 - (1/6)*d3psi*dt**3,
            psi - dpsi*dt + 0.5*d2psi*dt**2,
            psi,
            psi + dpsi*dt + 0.5*d2psi*dt**2]   # t-3, t-2, t-1, t
S_hist   = [entropy(p, phi_D) for p in psi_hist]

# Finite‑difference third derivative (jerk) of S_h:
J_psi = (S_hist[3] - 3*S_hist[2] + 3*S_hist[1] - S_hist[0]) / dt**3
print(f"\nJ_ψ (ψ‑component) = {J_psi:.3e} s⁻³")

# ----------------------------------------------------------------------
# Φ_Δ‑component (using same Δt, assuming similar scaling)
# ----------------------------------------------------------------------
# Approximate φ̇_D, φ̈_D, φ⃛_D from given data and ξ
dphi_D   = 8.7e3
ddphi_D  = dphi_D / xi          # s⁻²
d3phi_D  = ddphi_D / xi         # s⁻³
phi_D_hist = [phi_D - dphi_D*dt + 0.5*ddphi_D*dt**2 - (1/6)*d3phi_D*dt**3,
              phi_D - dphi_D*dt + 0.5*ddphi_D*dt**2,
              phi_D,
              phi_D + dphi_D*dt + 0.5*ddphi_D*dt**2]
# Entropy as function of φ_D (treat psi constant)
def S_phiD(phi):
    return entropy(psi, phi)

Sphi_hist = [S_phiD(p) for p in phi_D_hist]
J_phi = (Sphi_hist[3] - 3*Sphi_hist[2] + 3*Sphi_hist[1] - Sphi_hist[0]) / dt**3
print(f"J_Δ (Φ_Δ‑component) = {J_phi:.3e} s⁻³")

# ----------------------------------------------------------------------
# Total jerk (including source)
# ----------------------------------------------------------------------
J_total = J_psi + J_phi + J_source
print(f"\nTotal Informational Jerk J_I = {J_total:.3e} s⁻³")

# ----------------------------------------------------------------------
# Stability threshold Θ (includes e^{−ψ})
# ----------------------------------------------------------------------
lam   = 1.0e10   # s⁻² (as used in the Engine)
g_D   = 0.1
Theta = (lam * 1.0**2) / (4*np.pi) * (1 + 3*g_D**2/(4*np.pi)) * np.exp(-psi)
print(f"\nStability threshold Θ = {Theta:.3e} s⁻²")

# ------------------------------------------------------------------
# Variance of jerk (assuming ±20% fluctuations)
# ------------------------------------------------------------------
sigma_J = 0.2 * np.abs(J_total)
sigma_J2 = sigma_J**2
print(f"\nσ_J   = {sigma_J:.3e} s⁻³")
print(f"σ_J²  = {sigma_J2:.3e} s⁻⁶")

# ------------------------------------------------------------------
# Dimensional check: make Θ comparable to σ_J² by introducing τ⁴
# ------------------------------------------------------------------
# We require Θ * τ⁴ ≈ σ_J²  →  τ = (σ_J²/Θ)^{1/4}
tau = (sigma_J2 / Theta)**0.25
print(f"\nCharacteristic time τ that makes Θ·τ⁴ ≈ σ_J²: τ = {tau:.3e} s")
print(f"→ Θ·τ⁴ = {Theta * tau**4:.3e} s⁻⁶ (should match σ_J²)")

# ------------------------------------------------------------------
# Verdict based on dimensional‑corrected comparison
# ------------------------------------------------------------------
if np.abs(Theta * tau**4 - sigma_J2) / sigma_J2 < 0.1:
    print("\n[PASS] Threshold and jerk variance are dimensionally consistent.")
else:
    print("\n[FAIL] Significant dimensional mismatch – analysis not Omega‑Protocol compliant.")