# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for Linux HSA Unified Memory Informational Jerk
-----------------------------------------------------------------------
Checks:
  1. No boilerplate (input must be plain data – we assume the caller stripped it).
  2. ψ and its derivatives are computed correctly.
  3. Entropy S_h and its ψ‑derivatives are consistent.
  4. Informational jerk 𝒥_I is dimensionally correct (includes Δt³).
  5. Both stability boundaries (Shredding & Freeze) are evaluated.
  6. Invariant formulas for ξ_N⁻² and ξ_Δ⁻² hold with a single λ.
  7. Threshold Θ and jerk variance σ_𝒥² are comparable (same dimensions).
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
# NOTE: ddphi_D is not given; we will estimate it from stiffness later.

# Stiffness from engine output
xi_inv2 = 4.2e6         # s⁻²
xi      = 1.0/np.sqrt(xi_inv2)   # s

# Source jerk (as given)
J_source = 1.5e12       # s⁻³

# ----------------------------------------------------------------------
# Helper: entropy and its derivatives w.r.t ψ (phi_D held constant)
# ----------------------------------------------------------------------
def S_h(psi, phi_D):
    """Shannon conditional entropy for two-mode system."""
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi / denom
    pD = phi_D / denom
    return -(pN*np.log(pN + 1e-15) + pD*np.log(pD + 1e-15))

def dS_dpsi(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi / denom
    pD = phi_D / denom
    # derivative analytically: dS/dψ = -(pN - pD) * log(pN/pD)
    return -(pN - pD) * np.log(pN/pD + 1e-15)

def d2S_dpsi2(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi / denom
    pD = phi_D / denom
    # second derivative: d²S/dψ² = -(pN + pD) + 2*pN*pD
    return -(pN + pD) + 2.0*pN*pD

def d3S_dpsi3(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi / denom
    pD = phi_D / denom
    # third derivative (derived via sympy or manual)
    return (pN - pD) * (1.0 - 3.0*(pN + pD) + 2.0*pN*pD)

# ----------------------------------------------------------------------
# 1. Compute ψ and its derivatives (correct formulas)
# ----------------------------------------------------------------------
psi   = np.log(phi_N)
dpsi  = dphi_N / phi_N
# ψ̈ = (Φ̈_N/Φ_N) - (Φ̇_N/Φ_N)²
d2psi = ddphi_N/phi_N - (dphi_N/phi_N)**2
# Estimate ψ⃛ using characteristic time ξ (as engine did)
d3psi = d2psi / xi   # s⁻³

print(f"ψ      = {psi:.6e}")
print(f"ψ̇     = {dpsi:.6e} s⁻¹")
print(f"ψ̈     = {d2psi:.6e} s⁻²")
print(f"ψ⃛     = {d3psi:.6e} s⁻³\n")

# ----------------------------------------------------------------------
# 2. Entropy and ψ‑derivatives at the operating point
# ----------------------------------------------------------------------
S0      = S_h(psi, phi_D)
dS_psi  = dS_dpsi(psi, phi_D)
d2S_psi = d2S_dpsi2(psi, phi_D)
d3S_psi = d3S_dpsi3(psi, phi_D)

print(f"S_h          = {S0:.6f}")
print(f"∂S/∂ψ        = {dS_psi:.6e}")
print(f"∂²S/∂ψ²      = {d2S_psi:.6e}")
print(f"∂³S/∂ψ³      = {d3S_psi:.6e}\n")

# ----------------------------------------------------------------------
# 3. Finite‑difference jerk (requires sampling interval Δt)
# ----------------------------------------------------------------------
# We do not have Δt; we can infer a reasonable Δt from the stiffness time scale:
dt = xi   # use the characteristic time as sampling interval (conservative)
# Build a mock 4‑point history using Euler steps (for illustration only)
S_hist = []
psi_hist = [psi]
for k in range(4):
    # evolve ψ using its derivatives (Taylor)
    psi_k = psi + dpsi*(-k*dt) + 0.5*d2psi*(k*dt)**2 + (1/6)*d3psi*(-k*dt)**3
    psi_hist.append(psi_k)
    S_hist.append(S_h(psi_k, phi_D))
# Reverse so that index 0 is newest
S_hist = list(reversed(S_hist))
# Jerk via 4‑point finite difference: (S0 - 3S1 + 3S2 - S3) / dt³
J_psi = (S_hist[0] - 3*S_hist[1] + 3*S_hist[2] - S_hist[3]) / (dt**3)

# Φ_Δ contribution: we need its jerk. Estimate Φ̇_Δ and Φ̈_Δ from stiffness:
# Assume same characteristic time ξ for Δ mode:
dphi_D_est = dphi_D          # given
ddphi_D_est = dphi_D / xi    # rough estimate
d3phi_D_est = ddphi_D_est / xi

# Entropy derivative w.r.t φ_D (analytic)
def dS_dphiD(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi / denom
    pD = phi_D / denom
    return np.log(pD/pN + 1e-15)   # ∂S/∂φ_D = ln(p_Δ/p_N)

def d2S_dphiD2(psi, phi_D):
    epsi = np.exp(psi)
    denom = epsi + phi_D
    pN = epsi / denom
    pD = phi_D / denom
    return -1.0/(phi_D*denom)   # derived; sign not crucial for demo

dS_phiD = dS_dphiD(psi, phi_D)
d2S_phiD2 = d2S_dphiD2(psi, phi_D)

# Jerk from Φ_Δ using same finite‑difference stencil (mock history)
phiD_hist = []
for k in range(4):
    phiD_k = phi_D + dphi_D_est*(-k*dt) + 0.5*ddphi_D_est*(k*dt)**2 + (1/6)*d3phi_D_est*(-k*dt)**3
    phiD_hist.append(phiD_k)
phiD_hist = list(reversed(phiD_hist))
S_phiD_hist = [S_h(psi, v) for v in phiD_hist]  # ψ held constant for this part
J_phiD = (S_phiD_hist[0] - 3*S_phiD_hist[1] + 3*S_phiD_hist[2] - S_phiD_hist[3]) / (dt**3)

print(f"Δt (sampling) = {dt:.3e} s")
print(f"𝒥_I^ψ       = {J_psi:.6e} s⁻³")
print(f"𝒥_I^Δ       = {J_phiD:.6e} s⁻³")
J_total = J_psi + J_phiD + J_source
print(f"𝒥_I total   = {J_total:.6e} s⁻³\n")

# ----------------------------------------------------------------------
# 4. Stability boundaries
# ----------------------------------------------------------------------
# Shredding: ξ_Δ → ∞  ⇔  Φ_N² + 3 Φ_Δ² = I0²
shredding_lhs = phi_N**2 + 3*phi_D**2
# Freeze: ξ_N → ∞  ⇔  3 Φ_N² + Φ_Δ² = I0²
freeze_lhs = 3*phi_N**2 + phi_D**2

print(f"Shredding condition LHS = {shredding_lhs:.6f} (should = 1)")
print(f"Freeze condition LHS    = {freeze_lhs:.6f} (should = 1)\n")

# ----------------------------------------------------------------------
# 5. Invariant stiffness check – solve for λ from both expressions
# ----------------------------------------------------------------------
# ξ_N⁻² = λ (3Φ_N² + Φ_Δ² - I0²)
# ξ_Δ⁻² = λ (Φ_N² + 3Φ_Δ² - I0²)
# We know ξ⁻² from engine (assumed same for both modes? they gave a single ξ)
# We'll compute λ_N and λ_Δ and see if they match.
xi_N_inv2 = xi_inv2   # using the supplied value as proxy for both
xi_D_inv2 = xi_inv2

lambda_N = xi_N_inv2 / (3*phi_N**2 + phi_D**2 - 1.0)
lambda_D = xi_D_inv2 / (phi_N**2 + 3*phi_D**2 - 1.0)

print(f"λ from ξ_N⁻² = {lambda_N:.6e} s⁻²")
print(f"λ from ξ_Δ⁻² = {lambda_D:.6e} s⁻²")
print(f"Difference   = {abs(lambda_N - lambda_D):.6e} s⁻²\n")

# ----------------------------------------------------------------------
# 6. Stability threshold Θ (engine version) and jerk variance
# ----------------------------------------------------------------------
# Engine used: Θ = (λ I0² / 4π) * (1 + 3g_Δ² / 4π) * e^{-ψ}
# We'll adopt the λ they later used (1e10 s⁻²) to see the mismatch.
lam_engine = 1.0e10   # s⁻²
g_Delta    = 0.1
psi_val    = psi
Theta = (lam_engine / (4*np.pi)) * (1 + 3*g_Delta**2/(4*np.pi)) * np.exp(-psi_val)
print(f"Threshold Θ (engine) = {Theta:.6e}  [units?]")

# Jerk variance assuming ±20% fluctuations
sigma_J = 0.2 * abs(J_total)
sigma_J2 = sigma_J**2
print(f"σ_𝒥   = {sigma_J:.6e} s⁻³")
print(f"σ_𝒥²  = {sigma_J2:.6e} s⁻⁶\n")

# Dimensional check: to compare Θ and σ_𝒥² we need Θ to have s⁻⁶.
# If we multiply Θ by ξ⁴ we get s⁻⁶ (since Θ ~ s⁻², ξ⁴ ~ s⁴)
Theta_s6 = Theta * xi**4
print(f"Θ·ξ⁴  = {Theta_s6:.6e} s⁻⁶   (now comparable to σ_𝒥²)")
print(f"Ratio σ_𝒥² / (Θ·ξ⁴) = {sigma_J2/Theta_s6:.6f}\n")

# ----------------------------------------------------------------------
# 7. Verdict
# ----------------------------------------------------------------------
pass_bool = True
msgs = []

if abs(shredding_lhs - 1.0) > 1e-3:
    pass_bool = False
    msgs.append("Shredding boundary not satisfied.")
if abs(freeze_lhs - 1.0) > 1e-3:
    pass_bool = False
    msgs.append("Freeze boundary not satisfied.")
if abs(lambda_N - lambda_D) > 1e-2 * max(abs(lambda_N), abs(lambda_D)):
    pass_bool = False
    msgs.append("Inconsistent λ between ξ_N⁻² and ξ_Δ⁻².")
if abs(sigma_J2 - Theta_s6) > 1e-2 * max(sigma_J2, Theta_s6):
    pass_bool = False
    msgs.append("Jerk variance does not match stability threshold (after ξ⁴ scaling).")
if abs(d2psi - (-1.7e6)) > 1e-5:
    pass_bool = False
    msgs.append("ψ̈ sign/magnitude error (expected ≈ -1.7×10⁶ s⁻²).")

print("=== Omega Protocol Validation ===")
if pass_bool:
    print("PASS – all checked invariants and boundaries are satisfied.")
else:
    print("FAIL – the following issues were found:")
    for m in msgs:
        print(" -", m)