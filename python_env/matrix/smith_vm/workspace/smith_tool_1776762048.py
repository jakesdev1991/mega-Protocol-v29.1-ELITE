# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation Script – Agent Smith (Matrix Guardian)
# --------------------------------------------------------------
# Purpose:  Verify the mathematical soundness of the Engine's
#           Informational Jerk stability analysis and check
#           compliance with the Omega Physics Rubric invariants.
#           The script does **not** check for boilerplate formatting
#           (that is a textual rule); it focuses on the covariant
#           structure, dimensional consistency, and invariant usage.
# --------------------------------------------------------------

import numpy as np

# ------------------------------------------------------------------
# 1. INPUT DATA (as supplied in the Engine output)
# ------------------------------------------------------------------
I0 = 1.0                         # normalization
phi_N = 0.78                     # Φ_N / I0
phi_D = 0.35                     # Φ_Δ / I0
phi_N_dot = 2.1e3                # s⁻¹
phi_D_dot = 8.7e3                # s⁻¹
phi_N_ddot = 4.3e6               # s⁻²   (approximate second derivative)
# source jerk (given)
J_source = 1.5e12                # s⁻³

# stiffness inverse squared (from Engine)
xi_inv2 = 4.2e6                  # s⁻²
xi = 1.0 / np.sqrt(xi_inv2)      # s

# parameters for threshold (Engine values)
lam = 1.0e10                     # s⁻²
g_D = 0.1                        # dimensionless coupling

# ------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# ------------------------------------------------------------------
def S_h(psi, phi_D):
    """Shannon conditional entropy for two-mode system.
    psi = ln(Φ_N/I0)  →  Φ_N/I0 = exp(psi)
    phi_D = Φ_Δ/I0
    """
    pN = np.exp(psi) / (np.exp(psi) + phi_D)
    pD = phi_D / (np.exp(psi) + phi_D)
    # avoid log(0)
    eps = 1e-15
    return - (pN * np.log(pN + eps) + pD * np.log(pD + eps))

def dS_dpsi(psi, phi_D, h=1e-6):
    return (S_h(psi + h, phi_D) - S_h(psi - h, phi_D)) / (2*h)

def d2S_dpsi2(psi, phi_D, h=1e-6):
    return (S_h(psi + h, phi_D) - 2*S_h(psi, phi_D) + S_h(psi - h, phi_D)) / (h**2)

def d3S_dpsi3(psi, phi_D, h=1e-6):
    return (S_h(psi + 2*h, phi_D) - 2*S_h(psi + h, phi_D) +
            2*S_h(psi - h, phi_D) - S_h(psi - 2*h, phi_D)) / (2*h**3)

def dS_dphiD(psi, phi_D, h=1e-6):
    return (S_h(psi, phi_D + h) - S_h(psi, phi_D - h)) / (2*h)

def d2S_dphiD2(psi, phi_D, h=1e-6):
    return (S_h(psi, phi_D + h) - 2*S_h(psi, phi_D) + S_h(psi, phi_D - h)) / (h**2)

# ------------------------------------------------------------------
# 3. COMPUTE ψ AND ITS DERIVATIVES
# ------------------------------------------------------------------
psi = np.log(phi_N)                     # ln(Φ_N/I0)
psi_dot = phi_N_dot / phi_N             # dψ/dt
# Correct ψ̈ = φ̈_N/φ_N - (φ̇_N/φ_N)²
psi_ddot = phi_N_ddot / phi_N - (phi_N_dot / phi_N)**2
# ψ⃛ approximated by ψ̈/ξ (as in Engine)
psi_triple = psi_ddot / xi

print("ψ           =", psi)
print("ψ̇          =", psi_dot, "s⁻¹")
print("ψ̈          =", psi_ddot, "s⁻²")
print("ψ⃛          =", psi_triple, "s⁻³")
print()

# ------------------------------------------------------------------
# 4. ENTROPY DERIVATIVES AT THE OPERATING POINT
# ------------------------------------------------------------------
dS_dpsi_val   = dS_dpsi(psi, phi_D)
d2S_dpsi2_val = d2S_dpsi2(psi, phi_D)
d3S_dpsi3_val = d3S_dpsi3(psi, phi_D)
dS_dphiD_val  = dS_dphiD(psi, phi_D)
d2S_dphiD2_val= d2S_dphiD2(psi, phi_D)

print("∂S/∂ψ       =", dS_dpsi_val)
print("∂²S/∂ψ²     =", d2S_dpsi2_val)
print("∂³S/∂ψ³     =", d3S_dpsi3_val)
print("∂S/∂φ_Δ     =", dS_dphiD_val)
print("∂²S/∂φ_Δ²   =", d2S_dphiD2_val)
print()

# ------------------------------------------------------------------
# 5. INFORMATIONAL JERK COMPONENTS (ψ‑part and φ_Δ‑part)
# ------------------------------------------------------------------
# ψ‑component (as per Engine)
J_psi = (dS_dpsi_val   * psi_triple +
         3 * d2S_dpsi2_val * psi_dot * psi_ddot +
         d3S_dpsi3_val * psi_dot**3)

# φ_Δ‑component: need φ̈_Δ and φ⃛_Δ
# Approximate φ̈_Δ ≈ φ̇_Δ / ξ   (Engine assumption)
phi_D_ddot = phi_D_dot / xi
phi_D_triple = phi_D_ddot / xi   # same approximation

J_phiD = (dS_dphiD_val * phi_D_triple +
          3 * d2S_dphiD2_val * phi_D_dot * phi_D_ddot)

# total jerk from internal dynamics
J_internal = J_psi + J_phiD
J_total    = J_internal + J_source

print("J_ψ         =", J_psi, "s⁻³")
print("J_φΔ        =", J_phiD, "s⁻³")
print("J_internal  =", J_internal, "s⁻³")
print("J_source    =", J_source, "s⁻³")
print("J_total     =", J_total, "s⁻³")
print()

# ------------------------------------------------------------------
# 6. STABILITY THRESHOLD Θ (ψ‑modulated)
# ------------------------------------------------------------------
# Θ = (λ I0² / 4π) * (1 + 3g_Δ²/(4π)) * e^{-psi}
Theta = (lam * I0**2) / (4*np.pi) * (1 + 3*g_D**2/(4*np.pi)) * np.exp(-psi)
print("Threshold Θ =", Theta, "s⁻²")   # note units: λ [s⁻²] → Θ [s⁻²]

# ------------------------------------------------------------------
# 7. VARIANCE OF JERK (assuming ±20% fluctuation)
# ------------------------------------------------------------------
sigma_J = 0.2 * np.abs(J_total)          # s⁻³
sigma_J2 = sigma_J**2                    # s⁻⁶
print("σ_J         =", sigma_J, "s⁻³")
print("σ_J²        =", sigma_J2, "s⁻⁶")
print()

# ------------------------------------------------------------------
# 8. DIMENSIONAL CHECKS
# ------------------------------------------------------------------
# Jerk finite‑difference formula missing Δt³:
#   J_FD = (S[n] - 3S[n-1] + 3S[n-2] - S[n-3]) / Δt**3
# If we set Δt = 1 (implicit), the Engine's expression is missing the divisor.
# We flag this as a dimensional inconsistency.
print("=== DIMENSIONAL CONSISTENCY CHECK ===")
print("Finite‑difference jerk as written lacks Δt⁻³ factor.")
print("If Δt ≠ 1 s, the numerical value is off by a factor of Δt⁻³.")
print("Threshold Θ has units [s⁻²] while σ_J² has [s⁻⁶]; direct comparison is invalid.")
print()

# ------------------------------------------------------------------
# 9. BOUNDARY CONDITION CHECK (Informational Freeze)
# ------------------------------------------------------------------
# Informational Freeze occurs when ξ_N → ∞  →  Φ_N² + Φ_Δ² = I0²
# Shredding Event: ξ_Δ → ∞  →  Φ_N² + 3Φ_Δ² = I0²
phi_N_sq = phi_N**2
phi_D_sq = phi_D**2
cond_shred = np.isclose(phi_N_sq + 3*phi_D_sq, I0**2, atol=1e-3)
cond_freeze = np.isclose(phi_N_sq + phi_D_sq, I0**2, atol=1e-3)

print("=== BOUNDARY CONDITIONS ===")
print("Φ_N² + 3Φ_Δ² =", phi_N_sq + 3*phi_D_sq, "(should be 1 for Shredding)")
print("Φ_N² +   Φ_Δ² =", phi_N_sq +   phi_D_sq, "(should be 1 for Freeze)")
print("Shredding condition satisfied? ", cond_shred)
print("Freeze    condition satisfied? ", cond_freeze)
print()

# ------------------------------------------------------------------
# 10. SUMMARY OF VIOLATIONS
# ------------------------------------------------------------------
violations = []

# Boilerplate: not checked here (textual)
# Boundaries:
if not cond_freeze:
    violations.append("Missing Informational Freeze (ξ_N → ∞) analysis.")
# Dimensional consistency:
violations.append("Finite‑difference jerk missing Δt⁻³ divisor.")
violations.append("Threshold Θ ([s⁻²]) compared to σ_J² ([s⁻⁶]) – unit mismatch.")
# Sign error in ψ̈ (we already used correct formula; Engine had sign error)
# (we note it but not a violation if we correct)
if psi_ddot > 0:   # Engine's sign was positive; ours is negative
    violations.append("ψ̈ sign error (should be negative).")

print("=== VALIDATION RESULT ===")
if violations:
    print("FAIL – the following Omega Protocol invariants are violated:")
    for v in violations:
        print(" -", v)
else:
    print("PASS – all checked invariants are satisfied.")

# ------------------------------------------------------------------
# END OF SCRIPT
# ------------------------------------------------------------------