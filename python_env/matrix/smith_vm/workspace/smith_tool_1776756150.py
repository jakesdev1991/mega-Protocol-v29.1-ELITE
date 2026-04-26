# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
import math

# ----------------------------------------------------------------------
# Supplied audit data (normalized to I0 = 1)
# ----------------------------------------------------------------------
I0 = 1.0
phi_N = 0.78          # Φ_N / I0
phi_D = 0.35          # Φ_Δ / I0

# Time derivatives (s^-1)
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3

# Stiffness invariant
xi_inv2 = 4.2e6               # ξ⁻²  [s^-2]
xi = 1.0 / math.sqrt(xi_inv2) # ξ  [s]

# Source jerk (s^-3)
J_source = 1.5e12

# Fluctuation assumption
fluctuation_frac = 0.20   # ±20%

# Archive‑saturation constant for Informational Freeze (example)
lambda_Delta = 0.5        # Φ_Δ,crit / I0

# ----------------------------------------------------------------------
# Helper: two‑state Shannon entropy and its derivatives
# ----------------------------------------------------------------------
def entropy(p):
    """Shannon entropy in bits for probability p (0<p<1)."""
    return -p * math.log(p) - (1.0 - p) * math.log(1.0 - p)

def p_N(phiN, phiD):
    return phiN / (phiN + phiD)

def p_D(phiN, phiD):
    return 1.0 - p_N(phiN, phiD)

def S_h(phiN, phiD):
    pn = p_N(phiN, phiD)
    return entropy(pn)

# First derivatives of S_h w.r.t. phi_N and phi_D
def dS_dphiN(phiN, phiD):
    pn = p_N(phiN, phiD)
    pd = p_D(phiN, phiD)
    # dS/dp = ln((1-p)/p)
    dS_dp = math.log(pd / pn)
    # dp/dphiN = phiD / (phiN+phiD)^2
    dp_dphiN = phiD / ((phiN + phiD) ** 2)
    return dS_dp * dp_dphiN

def dS_dphiD(phiN, phiD):
    pn = p_N(phiN, phiD)
    pd = p_D(phiN, phiD)
    dS_dp = math.log(pd / pn)
    # dp/dphiD = -phiN / (phiN+phiD)^2
    dp_dphiD = -phiN / ((phiN + phiD) ** 2)
    return dS_dp * dp_dphiD

# Second derivatives (needed for ψ‑terms)
def d2S_dphiN2(phiN, phiD):
    # Derivative of dS/dphiN w.r.t phiN (analytic, but we can use sympy or finite diff)
    # For brevity we use a small finite difference.
    eps = 1e-8
    return (dS_dphiN(phiN + eps, phiD) - dS_dphiN(phiN - eps, phiD)) / (2 * eps)

def d2S_dphiD2(phiN, phiD):
    eps = 1e-8
    return (dS_dphiD(phiN, phiD + eps) - dS_dphiD(phiN, phiD - eps)) / (2 * eps)

def d2S_dphiNphiD(phiN, phiD):
    eps = 1e-8
    return (dS_dphiN(phiN, phiD + eps) - dS_dphiN(phiN, phiD - eps)) / (2 * eps)

# ----------------------------------------------------------------------
# Compute ψ and its time derivatives
# ----------------------------------------------------------------------
psi = math.log(phi_N / I0)               # ln(Φ_N/I0)
dot_psi = dot_phi_N / phi_N              # dψ/dt = \dotΦ_N/Φ_N
# Approximate \ddotψ using ξ as characteristic time:
# \ddotψ ≈ \dotψ/ξ - \dotψ^2   (as in the engine output)
ddot_psi = dot_psi / xi - dot_psi ** 2

# ----------------------------------------------------------------------
# Entropy and its derivatives at the operating point
# ----------------------------------------------------------------------
S = S_h(phi_N, phi_D)
dS_dpsi = dS_dphiN(phi_N, phi_D) * phi_N   # chain rule: dS/dψ = (dS/dΦ_N)*(dΦ_N/dψ) = (dS/dΦ_N)*Φ_N
d2S_dpsi2 = (d2S_dphiN2(phi_N, phi_D) * phi_N ** 2
             + dS_dphiN(phi_N, phi_D) * phi_N)   # ∂²S/∂ψ² = Φ_N² ∂²S/∂Φ_N² + Φ_N ∂S/∂Φ_N
# Mixed term ∂²S/∂ψ∂Φ_Δ = Φ_N ∂²S/∂Φ_N∂Φ_Δ
d2S_dpsi_phiD = phi_N * d2S_dphiNphiD(phi_N, phi_D)

# ----------------------------------------------------------------------
# Informational Jerk (third time derivative of S_h)
# Keep terms up to \ddotψ and \dotψ^2; higher orders are negligible for the given scale.
# J_I = d/dt[ (∂²S/∂ψ²) \dotψ² + 2 (∂²S/∂ψ∂Φ_Δ) \dotψ\dotΦ_Δ + (∂S/∂ψ) \ddotψ ]   (cross Φ_Δ¨ omitted)
term1 = d2S_dpsi2 * dot_psi ** 2
term2 = 2 * d2S_dpsi_phiD * dot_psi * dot_phi_D
term3 = dS_dpsi * ddot_psi
J_I_internal = (2 * d2S_dpsi2 * dot_psi * ddot_psi   # d/dt of term1
                + 2 * d2S_dpsi_phiD * (dot_psi * 0.0   # we assume \ddotΦ_Δ negligible
                                        + ddot_psi * dot_phi_D)  # derivative of term2
                + dS_dpsi * 0.0)                      # derivative of term3 (neglect \dddotψ)
# Add source jerk
J_I_total = J_I_internal + J_source

# ----------------------------------------------------------------------
# Fluctuation variance (±20%)
# ----------------------------------------------------------------------
sigma_J = fluctuation_frac * abs(J_I_total)
sigma_J2 = sigma_J ** 2

# ----------------------------------------------------------------------
# Shredding threshold Θ(ψ)
# ----------------------------------------------------------------------
lam = 1.0e10          # λ [s^-2] as used in the engine output
g_D = 0.1             # Archive coupling constant

# Shredding condition: Φ_N^2 + 3 Φ_Δ^2 = I0^2
# Solve for Φ_Δ^2 at the boundary given ψ:
phi_N_at_shred = I0 * math.exp(psi)   # = Φ_N at shredding (by definition)
phi_D_sq_shred = (I0**2 - phi_N_at_shred**2) / 3.0
# Potential at the boundary:
V_shred = (lam / 4.0) * ((phi_N_at_shred**2 + phi_D_sq_shred - I0**2) ** 2)
# The engine’s expression simplifies to:
# V_shred = (lam * I0**4 / 9) * (exp(2ψ) - 1)^2
V_shred_check = (lam * I0**4 / 9.0) * (math.exp(2 * psi) - 1.0) ** 2
assert math.isclose(V_shred, V_shred_check, rel_tol=1e-10)

# Threshold with metric scaling factor e^{-2ψ}
Theta = V_shred * (1.0 + (3.0 * g_D**2) / (4.0 * math.pi) * math.exp(-2.0 * psi))

# ----------------------------------------------------------------------
# Informational Freeze condition (optional check)
# ----------------------------------------------------------------------
# Freeze occurs when Φ_Δ reaches λ_Δ I0
freeze_phi_D = lambda_Delta * I0
freeze_condition = phi_D >= freeze_phi_D   # True if already saturated

# ----------------------------------------------------------------------
# Output results
# ----------------------------------------------------------------------
print(f"ψ = {psi:.6f}")
print(f"dot_ψ = {dot_psi:.3e} s⁻¹")
print(f"ddot_ψ = {ddot_psi:.3e} s⁻²")
print(f"S_h = {S:.6f} bits")
print(f"∂S/∂ψ = {dS_dpsi:.6f}")
print(f"∂²S/∂ψ² = {d2S_dpsi2:.6f}")
print(f"∂²S/∂ψ∂Φ_Δ = {d2S_dpsi_phiD:.6e}")
print(f"Internal jerk (no source) = {J_I_internal:.3e} s⁻³")
print(f"Total jerk (with source) = {J_I_total:.3e} s⁻³")
print(f"σ_J (±20%) = {sigma_J:.3e} s⁻³")
print(f"σ_J² = {sigma_J2:.3e} s⁻⁶")
print(f"Shredding threshold Θ(ψ) = {Theta:.3e} s⁻⁶")
print(f"Stability check σ_J² < Θ?  {sigma_J2 < Theta}")
print(f"Informational Freeze (Φ_Δ ≥ {freeze_phi_D:.3f})? {freeze_condition}")