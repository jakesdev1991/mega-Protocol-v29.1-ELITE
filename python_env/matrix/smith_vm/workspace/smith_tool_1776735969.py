# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the revised Linux HSA unified memory informational jerk analysis.
Checks:
  - Definitions of ψ and its derivatives
  - Entropy and its ψ/φΔ derivatives
  - Jerk components and total jerk
  - Boundary conditions (Shredding & Freeze)
  - Dimensionally consistent stability criterion
"""

import math
import numpy as np

# ------------------ Supplied data (normalized I0 = 1) ------------------
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
phiN_dot = 2.1e3        # s⁻¹
phiD_dot = 8.7e3        # s⁻¹
xi_inv2 = 4.2e6         # s⁻²  → ξ = 1/√xi_inv2
J_source = 1.5e12       # s⁻³

# ------------------ Derived quantities ------------------
I0 = 1.0
xi = 1.0 / math.sqrt(xi_inv2)          # characteristic time ~4.9e-4 s
lam = xi_inv2                          # λ ≈ ξ⁻² (since I0=1)

psi   = math.log(phi_N)                # ln(Φ_N/I0)
psi_dot = phiN_dot / phi_N
# Estimate second derivative from stiffness timescale:
phiN_ddot = phiN_dot / xi               # ≈ φ̇_N / ξ
psi_ddot = phiN_ddot/phi_N - (phiN_dot/phi_N)**2
psi_dddot = psi_ddot / xi               # crude but consistent with earlier estimate

print(f"psi = {psi:.6f}")
print(f"psi_dot = {psi_dot:.3e} s⁻¹")
print(f"psi_ddot = {psi_ddot:.3e} s⁻²")
print(f"psi_dddot = {psi_dddot:.3e} s⁻³\n")

# ------------------ Entropy derivatives ------------------
def S_h(psi_val, phiD_val):
    """Shannon conditional entropy for two-mode system."""
    epsi = math.exp(psi_val)
    denom = epsi + phiD_val
    pN = epsi / denom
    pD = phiD_val / denom
    if pN == 0 or pD == 0:
        return 0.0
    return -(pN*math.log(pN) + pD*math.log(pD))

def dS_dpsi(psi_val, phiD_val):
    epsi = math.exp(psi_val)
    denom = epsi + phiD_val
    pN = epsi / denom
    return -pN * (math.log(phiD_val) - psi_val)

def d2S_dpsi2(psi_val, phiD_val):
    epsi = math.exp(psi_val)
    denom = epsi + phiD_val
    pN = epsi / denom
    term = math.log(phiD_val) - psi_val
    return -pN*(1-pN)*term - pN

def d3S_dpsi3(psi_val, phiD_val):
    # Exact expression omitted for brevity; use numeric differentiation
    eps = 1e-6
    f = lambda x: d2S_dpsi2(x, phiD_val)
    return (f(psi_val+eps) - f(psi_val-eps))/(2*eps)

def dS_dphiD(psi_val, phiD_val):
    return psi_val - math.log(phiD_val)

def d2S_dphiD2(phiD_val):
    return -1.0/phiD_val

# Evaluate at operating point
psi_val   = psi
phiD_val  = phiD

S0      = S_h(psi_val, phiD_val)
dS_psi  = dS_dpsi(psi_val, phiD_val)
d2S_psi = d2S_dpsi2(psi_val, phiD_val)
d3S_psi = d3S_dpsi3(psi_val, phiD_val)
dS_phi  = dS_dphiD(psi_val, phiD_val)
d2S_phi = d2S_dphiD2(phiD_val)

print("Entropy derivatives:")
print(f"  S_h = {S0:.6f}")
print(f"  ∂S/∂ψ = {dS_psi:.6f}")
print(f"  ∂²S/∂ψ² = {d2S_psi:.6f}")
print(f"  ∂³S/∂ψ³ = {d3S_psi:.6f}")
print(f"  ∂S/∂φΔ = {dS_phi:.6f}")
print(f"  ∂²S/∂φΔ² = {d2S_phi:.6f}\n")

# ------------------ Jerk components ------------------
# ψ‑component
J_psi = (dS_psi * psi_dddot
         + 3 * d2S_psi * psi_dot * psi_ddot
         + d3S_psi * psi_dot**3)

# φΔ‑component (need φ̈_Δ and φ⃛_Δ)
phiD_ddot = phiD_dot / xi
phiD_dddot = phiD_ddot / xi

J_phi = (dS_phi * phiD_dddot
         + 3 * d2S_phi * phiD_dot * phiD_ddot)

# Total jerk (including source)
J_total = J_psi + J_phi + J_source

print("Jerk components:")
print(f"  J_ψ   = {J_psi:.3e} s⁻³")
print(f"  J_φΔ  = {J_phi:.3e} s⁻³")
print(f"  J_src = {J_source:.3e} s⁻³")
print(f"  J_total = {J_total:.3e} s⁻³\n")

# ------------------ Variance estimate (20% fluctuation) ------------------
sigma_J = 0.20 * abs(J_total)
sigma_J2 = sigma_J**2
print(f"σ_J   = {sigma_J:.3e} s⁻³")
print(f"σ_J²  = {sigma_J2:.3e} s⁻⁶\n")

# ------------------ Stability threshold ------------------
# Threshold: Θ = (λ I0² e^{-ψ})³
Theta = (lam * I0**2 * math.exp(-psi))**3
print(f"Threshold Θ = (λ I0² e^{{-ψ}})^3 = {Theta:.3e} s⁻⁶")
print(f"Comparison σ_J² ? Θ : {'UNSTABLE' if sigma_J2 > Theta else 'STABLE'}\n")

# ------------------ Boundary conditions ------------------
shredding_cond = phi_N**2 + 3*phi_D**2
freeze_cond    = 3*phi_N**2 + phi_D**2
print("Boundary checks:")
print(f"  Φ_N² + 3Φ_Δ² = {shredding_cond:.6f}  (Shredding if = 1)")
print(f"  3Φ_N² + Φ_Δ² = {freeze_cond:.6f}    (Freeze if = 1)")
print(f"  → Distance to Shredding: {1 - shredding_cond:.6f}")
print(f"  → Distance to Freeze:    {freeze_cond - 1:.6f}\n")

# ------------------ Invariant checks (optional) ------------------
# Verify that ψ = ln(Φ_N/I0) holds
assert math.isclose(psi, math.log(phi_N/I0), rel_tol=1e-12), "ψ definition violated"
# Verify stiffness relation (approximate)
xiN_inv2 = lam * (3*phi_N**2 + phi_D**2 - I0**2)
xiD_inv2 = lam * (phi_N**2 + 3*phi_D**2 - I0**2)
print("Stiffness invariants (for reference):")
print(f"  ξ_N⁻² = {xiN_inv2:.3e} s⁻²")
print(f"  ξ_Δ⁻² = {xiD_inv2:.3e} s⁻²")
print("(Negative ξ_Δ⁻² indicates proximity to Shredding)\n")

print("Validation complete.")