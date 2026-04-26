# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for Linux HSA Unified Memory
-----------------------------------------------------
Checks mathematical consistency of the supplied analysis
and enforces the invariant‑based Shredding condition:
    Phi_N^2 + 3*Phi_Delta^2 < I0^2   (stable)
    Phi_N^2 + 3*Phi_Delta^2 == I0^2  (shredding threshold)
"""

import numpy as np

# ----------------------------------------------------------------------
# Supplied data (normalized to I0 = 1)
# ----------------------------------------------------------------------
I0 = 1.0
phi_N = 0.78          # Phi_N / I0
phi_D = 0.35          # Phi_Delta / I0

# Time derivatives (s^-1, s^-2, s^-3 as given)
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3

# Stiffness (from xi^{-2} = 4.2e6 s^-2)
xi_inv_sq = 4.2e6          # s^-2
xi = np.sqrt(1.0 / xi_inv_sq)   # s

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def psi_from_phi_N(phi):
    """Metric coupling invariant ψ = ln(Phi_N / I0)"""
    return np.log(phi)

def dpsi(phi, dot_phi):
    """First derivative of ψ"""
    return dot_phi / phi

def d2psi(phi, dot_phi, ddot_phi):
    """Second derivative of ψ (exact)"""
    return ddot_phi / phi - (dot_phi / phi)**2

def d3psi(phi, dot_phi, ddot_phi, ddotdot_phi):
    """Third derivative of ψ (exact)"""
    # d/dt[ ddot_phi/phi - (dot_phi/phi)^2 ]
    term1 = (ddotdot_phi * phi - ddot_phi * dot_phi) / phi**2
    term2 = -2 * (dot_phi / phi) * (ddot_phi * phi - dot_phi**2) / phi**2
    return term1 + term2

def entropy_derivatives(psi, phi_D):
    """Analytic derivatives of S_h w.r.t ψ and φ_Δ (I0=1)"""
    e_psi = np.exp(psi)
    denom = e_psi + phi_D
    p_N = e_psi / denom
    p_D = phi_D / denom

    # First derivative w.r.t ψ
    dS_dpsi = -p_N * p_D * np.log(p_N / p_D)

    # Second derivative
    # d/dψ [ -p_N p_D ln(p_N/p_D) ] = -p_N p_D [1 + (ln(p_N/p_D))**2]
    d2S_dpsi2 = -p_N * p_D * (1.0 + (np.log(p_N / p_D))**2)

    # Third derivative
    # d/dψ of the above = -2 p_N p_D ln(p_N/p_D) [1 + (ln(p_N/p_D))**2]
    d3S_dpsi3 = -2.0 * p_N * p_D * np.log(p_N / p_D) * (1.0 + (np.log(p_N / p_D))**2)

    # Derivatives w.r.t φ_Δ (keeping ψ constant)
    # p_N = e^ψ/(e^ψ+φ_Δ), p_Δ = φ_Δ/(e^ψ+φ_Δ)
    dpN_dphiD = -e_psi / denom**2          # = -p_N * p_D / phi_D
    dpD_dphiD =  e_psi / denom**2          # =  p_N * p_D / phi_D
    # First derivative
    dS_dphiD = -(dpN_dphiD * (np.log(p_N) + 1.0) +
                dpD_dphiD * (np.log(p_D) + 1.0))
    # Second derivative (analytic but we compute numeric for clarity)
    # Use finite difference on dS_dphiD w.r.t phi_D
    eps = 1e-8
    phiD_plus = phi_D + eps
    denom_p = e_psi + phiD_plus
    pN_p = e_psi / denom_p
    pD_p = phiD_plus / denom_p
    dS_dphiD_p = -( -e_psi/denom_p**2 * (np.log(pN_p)+1.0) +
                    e_psi/denom_p**2 * (np.log(pD_p)+1.0) )
    d2S_dphiD2 = (dS_dphiD_p - dS_dphiD) / eps
    return dS_dpsi, d2S_dpsi2, d3S_dpsi3, dS_dphiD, d2S_dphiD2

def informational_jerk(psi, dpsi, d2psi, d3psi,
                       dS_dpsi, d2S_dpsi2, d3S_dpsi3,
                       phi_D, dot_phi_D, ddot_phi_D, ddotdot_phi_D,
                       dS_dphiD, d2S_dphiD2):
    """Third covariant derivative of S_h via chain rule."""
    # ψ part
    J_psi = (dS_dpsi * d3psi +
             3.0 * d2S_dpsi2 * dpsi * d2psi +
             d3S_dpsi3 * dpsi**3)

    # φ_Δ part (same structure, treat φ_Δ as independent variable)
    J_phiD = (dS_dphiD * ddotdot_phi_D +
              3.0 * d2S_dphiD2 * dot_phi_D * ddot_phi_D)

    return J_psi + J_phiD

# ----------------------------------------------------------------------
# 1. Compute ψ and its derivatives using the supplied data
# ----------------------------------------------------------------------
psi = psi_from_phi_N(phi_N)
print(f"ψ = ln(Φ_N/I0) = {psi:.6f}")

# We need Φ_N'' and Φ_N''' to get ψ'' and ψ'''.
# The analysis approximated Φ_N'' ≈ ξ^{-2} (a guess). We'll compute both
# the *given* approximation and the *exact* one if we had the values.
# For validation we will use the *given* approximation to see the impact.
# (If the user supplies actual Φ_N'' and Φ_N''' they can replace the placeholders.)

# Approximate second derivative of Φ_N from stiffness (as in the text)
ddot_phi_N_approx = xi_inv_sq   # 4.2e6 s^-2  (they used 4.3e6, close enough)
# Third derivative approximation: ddotdot_phi_N ≈ ddot_phi_N / xi
ddotdot_phi_N_approx = ddot_phi_N_approx / xi

# Compute ψ derivatives using the *approximate* Φ_N'' and Φ_N'''
dpsi_val = dpsi(phi_N, dot_phi_N)
d2psi_val = d2psi(phi_N, dot_phi_N, ddot_phi_N_approx)
d3psi_val = d3psi(phi_N, dot_phi_N, ddot_phi_N_approx, ddotdot_phi_N_approx)

print(f"ψ'  = {dpsi_val:.3e} s⁻¹")
print(f"ψ'' = {d2psi_val:.3e} s⁻²")
print(f"ψ'''= {d3psi_val:.3e} s⁻³")

# ----------------------------------------------------------------------
# 2. Entropy derivatives
# ----------------------------------------------------------------------
(dS_dpsi, d2S_dpsi2, d3S_dpsi3,
 dS_dphiD, d2S_dphiD2) = entropy_derivatives(psi, phi_D)

print(f"∂S/∂ψ   = {dS_dpsi:.6f}")
print(f"∂²S/∂ψ² = {d2S_dpsi2:.6f}")
print(f"∂³S/∂ψ³ = {d3S_dpsi3:.6f}")
print(f"∂S/∂φΔ  = {dS_dphiD:.6f}")
print(f"∂²S/∂φΔ²= {d2S_dphiD2:.6f}")

# ----------------------------------------------------------------------
# 3. Approximate Φ_Δ'' and Φ_Δ''' (as in the analysis)
# ----------------------------------------------------------------------
ddot_phi_D_approx = dot_phi_D / xi          # ≈ 1.78e7 s^-2
ddotdot_phi_D_approx = ddot_phi_D_approx / xi   # ≈ 3.63e10 s^-3

# ----------------------------------------------------------------------
# 4. Compute informational jerk
# ----------------------------------------------------------------------
J_total = informational_jerk(psi, dpsi_val, d2psi_val, d3psi_val,
                             dS_dpsi, d2S_dpsi2, d3S_dpsi3,
                             phi_D, dot_phi_D, ddot_phi_D_approx, ddotdot_phi_D_approx,
                             dS_dphiD, d2S_dphiD2)

print(f"Informational jerk 𝒥_I = {J_total:.3e} s⁻³")

# ----------------------------------------------------------------------
# 5. Source jerk (external)
# ----------------------------------------------------------------------
J_source = 1.5e12
J_total_with_source = J_total + J_source
print(f"𝒥_I (with source) = {J_total_with_source:.3e} s⁻³")

# ----------------------------------------------------------------------
# 6. Mode‑space Shredding invariant (the only Omega‑Protocol invariant)
# ----------------------------------------------------------------------
shredding_lhs = phi_N**2 + 3.0 * phi_D**2
print(f"Φ_N² + 3Φ_Δ² = {shredding_lhs:.6f}  (I0² = 1.0)")
if np.isclose(shredding_lhs, 1.0, atol=1e-12):
    print("→ System at the Shredding threshold (invariant borderline).")
elif shredding_lhs < 1.0:
    print("→ System is SHRED‑SAFE (invariant satisfied).")
else:
    print("→ System has SHREDDED (invariant violated).")
    raise AssertionError("Omega Protocol invariant violated: Φ_N²+3Φ_Δ² > I0²")

# ----------------------------------------------------------------------
# 7. Optional variance‑based jerk test (NOT an invariant)
# ----------------------------------------------------------------------
sigma_J = 0.2 * abs(J_total_with_source)   # 20% fluctuation assumption
Theta = (1e10 / (4.0*np.pi)) * (1.0 + 3*0.1**2/(4.0*np.pi)) * np.exp(-psi)
print(f"\nVariance‑based check (non‑invariant):")
print(f"  σ_𝒥 = {sigma_J:.3e} s⁻³")
print(f"  σ_𝒥² = {sigma_J**2:.3e} s⁻⁶")
print(f"  Θ   = {Theta:.3e} s⁻⁶")
if sigma_J**2 > Theta:
    print("  → σ_𝒥² > Θ  (would flag instability under the variance model).")
else:
    print("  → σ_𝒥² ≤ Θ  (stable under variance model).")

# ----------------------------------------------------------------------
# End of validation
# ----------------------------------------------------------------------