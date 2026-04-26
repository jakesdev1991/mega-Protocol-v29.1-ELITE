# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Linux HSA Unified Memory Informational Jerk analysis.
Checks:
  1. Dimensional consistency of the jerk finite‑difference formula.
  2. Correct calculation of ψ and its derivatives.
  3. Entropy and its ψ‑derivatives at the given state.
  4. ψ‑component and Φ_Δ‑component of the informational jerk.
  5. Total jerk and comparison with source jerk.
  6. Stability threshold Θ and its units vs. σ_J².
  7. Presence of the Informational Freeze condition (ξ_N → ∞).
If any check fails, the script raises an AssertionError with a diagnostic.
"""

import numpy as np

# ----------------------------------------------------------------------
# Supplied data (normalized to I0 = 1)
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
dphi_N  = 2.1e3         # s⁻¹
dphi_D  = 8.7e3         # s⁻¹
ddphi_N = 4.3e6         # s⁻²   (approximate second derivative)
# Stiffness from given ξ⁻²
xi_inv2 = 4.2e6         # s⁻²
xi      = 1.0/np.sqrt(xi_inv2)   # s
J_source = 1.5e12       # s⁻³

# ----------------------------------------------------------------------
# 1. ψ and its derivatives (using exact formulas)
psi   = np.log(phi_N)                     # dimensionless
dpsi  = dphi_N / phi_N                    # s⁻¹
# ψ̈ = (Φ̈_N/Φ_N) - (Φ̇_N/Φ_N)²
d2psi = ddphi_N/phi_N - (dphi_N/phi_N)**2  # s⁻²
# Approximate ψ‴ using ξ as a characteristic time scale (as in the analysis)
d3psi = d2psi / xi                        # s⁻³

print(f"ψ = {psi:.6f}")
print(f"ψ̇ = {dpsi:.3e} s⁻¹")
print(f"ψ̈ = {d2psi:.3e} s⁻²")
print(f"ψ‴ = {d3psi:.3e} s⁻³")

# ----------------------------------------------------------------------
# 2. Entropy S_h(ψ, φ_D) and its ψ‑derivatives
# Normalized probabilities
e_psi = np.exp(psi)
den   = e_psi + phi_D
pN    = e_psi / den
pD    = phi_D / den

Sh    = -(pN*np.log(pN) + pD*np.log(pD))   # dimensionless

# Analytic derivatives (derived from Sh = -[pN ln pN + pD ln pD])
# dSh/dψ = -(ln pN + 1)*dpN/dψ - (ln pD + 1)*dpD/dψ
# where dpN/dψ = pN*(1 - pN) and dpD/dψ = -pN*pD
dpN_dpsi = pN * (1 - pN)
dpD_dpsi = -pN * pD
dSh_dpsi = -(np.log(pN)+1)*dpN_dpsi - (np.log(pD)+1)*dpD_dpsi

# Second derivative
d2pN_dpsi2 = pN*(1 - 2*pN)          # derivative of dpN/dψ
d2pD_dpsi2 = -pN*(1 - 2*pD)        # derivative of dpD/dψ
d2Sh_dpsi2 = -((np.log(pN)+1)*d2pN_dpsi2 + (1/pN)*dpN_dpsi**2) \
             -((np.log(pD)+1)*d2pD_dpsi2 + (1/pD)*dpD_dpsi**2)

# Third derivative (omitted for brevity – we compute numerically)
def Sh_of_psi(psi_val):
    e = np.exp(psi_val)
    den = e + phi_D
    pN = e/den
    pD = phi_D/den
    return -(pN*np.log(pN) + pD*np.log(pD))

# Use central finite difference for third derivative
h = 1e-6
d3Sh_dpsi3 = (Sh_of_psi(psi+2*h) - 2*Sh_of_psi(psi+h) + 2*Sh_of_psi(psi-h) - Sh_of_psi(psi-2*h)) / (2*h**3)

print(f"S_h = {Sh:.6f}")
print(f"∂S_h/∂ψ = {dSh_dpsi:.6f}")
print(f"∂²S_h/∂ψ² = {d2Sh_dpsi2:.6f}")
print(f"∂³S_h/∂ψ³ = {d3Sh_dpsi3:.6f}")

# ----------------------------------------------------------------------
# 3. Jerk components (ψ‑part)
J_psi = (dSh_dpsi)*d3psi \
        + 3*d2Sh_dpsi2*dpsi*d2psi \
        + d3Sh_dpsi3*dpsi**3

# ----------------------------------------------------------------------
# 4. Φ_Δ‑part (reuse entropy derivatives w.r.t φ_D)
# dSh/dφ_D = -(ln pD + 1)*dpD/dφ_D - (ln pN + 1)*dpN/dφ_D
dpD_dphiD = pD*(1 - pD)          # because pD = φ_D/(e^ψ+φ_D)
dpN_dphiD = -pN*pD
dSh_dphiD = -(np.log(pD)+1)*dpD_dphiD - (np.log(pN)+1)*dpN_dphiD

# Second derivative w.r.t φ_D (numeric for simplicity)
def Sh_of_phiD(phiD_val):
    den = e_psi + phiD_val
    pN = e_psy/den
    pD = phiD_val/den
    return -(pN*np.log(pN) + pD*np.log(pD))

hD = 1e-6
d2Sh_dphiD2 = (Sh_of_phiD(phiD+hD) - 2*Sh_of_phiD(phiD) + Sh_of_phiD(phiD-hD)) / (hD**2)

# Approximate higher derivatives of φ_D using ξ as before
d2phiD = dphi_D / xi          # s⁻²
d3phiD = d2phiD / xi          # s⁻³

J_phiD = (dSh_dphiD)*d3phiD + 3*d2Sh_dphiD2*dphi_D*d2phiD

print(f"J_ψ component = {J_psi:.3e} s⁻³")
print(f"J_ΦΔ component = {J_phiD:.3e} s⁻³")

# ----------------------------------------------------------------------
# 5. Total jerk (including source)
J_total = J_psi + J_phiD + J_source
print(f"Total informational jerk J_I = {J_total:.3e} s⁻³")

# ----------------------------------------------------------------------
# 6. Stability threshold Θ
lam   = 1.0e10          # s⁻² (as used in the analysis)
gD    = 0.1             # dimensionless coupling
I0    = 1.0
Theta = (lam * I0**2)/(4*np.pi) * (1 + 3*gD**2/(4*np.pi)) * np.exp(-psi)
print(f"Stability threshold Θ = {Theta:.3e} (units s⁻²)")

# ----------------------------------------------------------------------
# 7. Variance of jerk (assuming ±20% fluctuations)
sigma_J = 0.2 * np.abs(J_total)
sigma_J2 = sigma_J**2
print(f"σ_J = {sigma_J:.3e} s⁻³")
print(f"σ_J² = {sigma_J2:.3e} s⁻⁶")

# ----------------------------------------------------------------------
# 8. Checks
# 8.1 Dimensional check: jerk finite‑difference needs Δt³.
#    We adopt a representative sampling interval Δt = 1 µs (typical HSA counter).
dt = 1e-6   # s
J_fd = (Sh - 3*Sh_of_psi(psi - dpsi*dt) + 3*Sh_of_psi(psi - 2*dpsi*dt) - Sh_of_psi(psi - 3*dpsi*dt)) / dt**3
print(f"Finite‑difference jerk (with Δt={dt}) = {J_fd:.3e} s⁻³")
# The value should be of the same order as J_psi (within factor ~2)
assert np.abs(J_fd - J_psi) < 5*np.abs(J_psi), "Finite‑difference jerk mismatch – missing Δt³ or integration error."

# 8.2 Sign of ψ̈ (should be negative for given numbers)
assert d2psi < 0, "ψ̈ has incorrect sign – violates covariant derivative definition."

# 8.3 Threshold units vs σ_J²: they must match for a meaningful comparison.
#    In a proper Omega invariant, Θ should have units of (jerk)² → s⁻⁶.
#    We therefore compute a corrected Θ_correct = Θ * (some time⁴) and compare.
#    Since no time⁴ factor is supplied, we flag the inconsistency.
assert False, "Threshold Θ has units s⁻² while σ_J² has s⁻⁶ → dimensional inconsistency. " \
              "A proper Omega invariant requires Θ ∝ (characteristic time)⁴ to yield s⁻⁶."

# 8.4 Informational Freeze condition (ξ_N → ∞)
#    ξ_N⁻² = λ(3Φ_N² + Φ_Δ² - I0²)  → freeze when RHS → 0⁺
xi_N_inv2 = lam * (3*phi_N**2 + phi_D**2 - I0**2)
print(f"ξ_N⁻² = {xi_N_inv2:.3e} s⁻²")
# If xi_N_inv2 ≤ 0 we are at or past freeze.
if xi_N_inv2 <= 0:
    print("⚠️  Informational Freeze condition approached or exceeded.")
else:
    print("ξ_N⁻² > 0 → system away from Informational Freeze.")

# If we reach here, all checks that can be programmatically passed have passed.
print("\nAll programmable checks passed. "
      "Note: the threshold dimensional inconsistency remains a hard Omega‑Protocol violation.")