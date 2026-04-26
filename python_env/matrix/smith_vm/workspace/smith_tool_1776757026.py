# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script
--------------------------------
Validates the mathematical steps and invariants presented in the
Linux HSA unified memory informational jerk stability analysis.
All quantities are checked against the values reported in the
Engine's output using a relative tolerance of 1e-2 (1 %).
"""

import math
import numpy as np

# ----------------------------------------------------------------------
# 1. INPUT DATA (as given in the Engine's output)
# ----------------------------------------------------------------------
phi_N   = 0.78          # Φ_N / I_0
phi_D   = 0.35          # Φ_Δ / I_0
dot_phi_N = 2.1e3       # s⁻¹
dot_phi_D = 8.7e3       # s⁻¹
xi_inv2 = 4.2e6         # s⁻²   → ξ = ξ_inv2⁻⁰·⁵
J_source = 1.5e12       # s⁻³   (source jerk)

# ----------------------------------------------------------------------
# 2. DERIVED BASE QUANTITIES
# ----------------------------------------------------------------------
psi = math.log(phi_N)                     # ψ = ln(Φ_N/I_0)
xi  = xi_inv2**-0.5                       # relaxation time (s)

# First derivatives of ψ
dot_psi = dot_phi_N / phi_N                # dψ/dt = (dot Φ_N)/Φ_N

# Approximate second derivatives via relaxation‑time scaling
ddot_phi_N = dot_phi_N / xi
ddot_phi_D = dot_phi_D / xi

# Second and third derivatives of ψ
ddot_psi  = ddot_phi_N / phi_N - dot_psi**2
dddot_psi = ddot_psi / xi

# Third derivative of Φ_Δ (same scaling)
dddot_phi_D = ddot_phi_D / xi

# ----------------------------------------------------------------------
# 3. PROBABILITIES AND ENTROPY DERIVATIVES
# ----------------------------------------------------------------------
# Normalised probabilities (proportional to the modes)
Z = math.exp(psi) + phi_D          # e^ψ + Φ_Δ/I_0
p_N = math.exp(psi) / Z
p_D = phi_D / Z

def entropy_derivatives(pN, pD):
    """Return ∂S/∂ψ, ∂²S/∂ψ², ∂³S/∂ψ³ and ∂S/∂φΔ, ∂²S/∂φΔ²."""
    # S = -[pN ln pN + pD ln pD]; pN = e^ψ / Z, pD = φΔ / Z
    # Analytic derivatives (derived by chain rule)
    dpsi_pN = pN          # ∂pN/∂ψ = pN (since pN ∝ e^ψ)
    dpsi_pD = 0.0         # pD independent of ψ
    # First derivative
    dS_dpsi = -(dpsi_pN * (math.log(pN) + 1) + dpsi_pD * (math.log(pD) + 1))
    # Second derivative
    d2psi_pN = pN         # ∂²pN/∂ψ² = pN
    d2psi_pD = 0.0
    d2S_dpsi2 = -(d2psi_pN * (math.log(pN) + 2) +
                  d2psi_pD * (math.log(pD) + 2) +
                  dpsi_pN**2 / pN + dpsi_pD**2 / pD)
    # Third derivative
    d3psi_pN = pN
    d3psi_pD = 0.0
    d3S_dpsi3 = -(d3psi_pN * (math.log(pN) + 3) +
                  d3psi_pD * (math.log(pD) + 3) +
                  3 * d2psi_pN * dpsi_pN / pN +
                  3 * d2psi_pD * dpsi_pD / pD -
                  dpsi_pN**3 / (pN**2) -
                  dpsi_pD**3 / (pD**2))
    # Derivatives w.r.t. φΔ (treat ψ constant)
    dphi_pN = 0.0
    dphi_pD = 1.0 / Z - phi_D / (Z**2)   # ∂pD/∂φΔ
    # First derivative
    dS_dphi = -(dphi_pN * (math.log(pN) + 1) + dphi_pD * (math.log(pD) + 1))
    # Second derivative
    d2phi_pN = 0.0
    d2phi_pD = -2.0 / (Z**2) + 2.0 * phi_D / (Z**3)
    d2S_dphi2 = -(d2phi_pN * (math.log(pN) + 2) +
                  d2phi_pD * (math.log(pD) + 2) +
                  dphi_pN**2 / pN +
                  dphi_pD**2 / pD)
    return (dS_dpsi, d2S_dpsi2, d3S_dpsi3,
            dS_dphi, d2S_dphi2)

(dS_dpsi, d2S_dpsi2, d3S_dpsi3,
 dS_dphi, d2S_dphi2) = entropy_derivatives(p_N, p_D)

# ----------------------------------------------------------------------
# 4. JERK COMPONENTS (as per the Engine's formula)
# ----------------------------------------------------------------------
J_psi = (dS_dpsi * dddot_psi +
         3 * d2S_dpsi2 * dot_psi * ddot_psi +
         d3S_dpsi3 * dot_psi**3)

J_Delta = (dS_dphi * dddot_phi_D +
           3 * d2S_dphi2 * dot_phi_D * ddot_phi_D)

J_total = J_psi + J_Delta + J_source

# ----------------------------------------------------------------------
# 5. BOUNDARY CONDITIONS
# ----------------------------------------------------------------------
shredding_cond = phi_N**2 + 3 * phi_D**2   # should be < 1 for no shredding
freeze_cond    = 3 * phi_N**2 + phi_D**2   # should be < 1 for no freeze

# ----------------------------------------------------------------------
# 6. STABILITY METRIC (dimensionless jerk variance)
# ----------------------------------------------------------------------
omega = 1.0 / xi                           # characteristic frequency (s⁻¹)
omega_psi = omega * math.exp(-psi/2.0)     # ψ‑modulated frequency
natural_jerk = omega_psi**3                # ω_ψ³ (s⁻³)

# Jerk variance (using the total jerk as a single‑sample estimate)
jerk_var = J_total**2                      # σ_J² (s⁻⁶)
dimless_var = jerk_var / (omega_psi**6)    # σ_J² / ω_ψ⁶

# ----------------------------------------------------------------------
# 7. VALIDATION (compare with Engine's reported numbers)
# ----------------------------------------------------------------------
tolerance = 1e-2   # 1 % relative tolerance

def approx_equal(a, b, rel=tolerance):
    return math.isclose(a, b, rel_tol=rel, abs_tol=0.0)

# Expected values from the Engine's output
expected = {
    "psi": math.log(0.78),
    "dot_psi": 2.69e3,
    "ddot_phi_N": 4.29e6,
    "ddot_phi_D": 1.78e7,
    "ddot_psi": -1.74e6,
    "dddot_psi": -3.55e9,
    "dddot_phi_D": 3.63e10,
    "p_N": 0.690,
    "p_D": 0.310,
    "dS_dpsi": 0.553,
    "d2S_dpsi2": -0.519,
    "d3S_dpsi3": 0.089,
    "dS_dphi": 0.802,
    "d2S_dphi2": -2.857,
    "J_psi": 7.07e9,
    "J_Delta": -1.30e12,
    "J_total": 2.07e11,
    "shredding_cond": 0.9759,
    "freeze_cond": 1.9477,
    "omega": 2040.8,
    "omega_psi": 2305.0,
    "natural_jerk": 1.22e10,
    "jerk_var": 4.28e22,
    "dimless_var": 287.0,
}

computed = {
    "psi": psi,
    "dot_psi": dot_psi,
    "ddot_phi_N": ddot_phi_N,
    "ddot_phi_D": ddot_phi_D,
    "ddot_psi": ddot_psi,
    "dddot_psi": dddot_psi,
    "dddot_phi_D": dddot_phi_D,
    "p_N": p_N,
    "p_D": p_D,
    "dS_dpsi": dS_dpsi,
    "d2S_dpsi2": d2S_dpsi2,
    "d3S_dpsi3": d3S_dpsi3,
    "dS_dphi": dS_dphi,
    "d2S_dphi2": d2S_dphi2,
    "J_psi": J_psi,
    "J_Delta": J_Delta,
    "J_total": J_total,
    "shredding_cond": shredding_cond,
    "freeze_cond": freeze_cond,
    "omega": omega,
    "omega_psi": omega_psi,
    "natural_jerk": natural_jerk,
    "jerk_var": jerk_var,
    "dimless_var": dimless_var,
}

all_ok = True
for key in expected:
    if not approx_equal(computed[key], expected[key]):
        print(f"❌ MISMATCH: {key}")
        print(f"   Expected: {expected[key]:.6e}")
        print(f"   Computed: {computed[key]:.6e}")
        all_ok = False

if all_ok:
    print("✅ All numerical checks passed within 1 % tolerance.")
else:
    print("⚠️  Some checks failed – see above.")

# ----------------------------------------------------------------------
# 8. INVARIANT CHECKS (Omega Protocol)
# ----------------------------------------------------------------------
print("\n--- Omega Protocol Invariant Checks ---")
print(f"Shredding condition (Φ_N² + 3Φ_Δ²) = {shredding_cond:.5f}  {'OK' if shredding_cond < 1.0 else 'VIOLATION'}")
print(f"Freeze    condition (3Φ_N² + Φ_Δ²) = {freeze_cond:.5f}    {'OK' if freeze_cond < 1.0 else 'VIOLATION'}")
print(f"Dimensionless jerk variance = {dimless_var:.2f}  {'STABLE' if dimless_var < 1.0 else 'UNSTABLE'}")

# ----------------------------------------------------------------------
# 9. CONCLUSION
# ----------------------------------------------------------------------
if all_ok and shredding_cond < 1.0 and freeze_cond < 1.0 and dimless_var < 1.0:
    print("\n🟢 Overall: Mathematically sound and compliant with Omega Protocol invariants.")
else:
    print("\n🔴 Overall: Deviations detected – review required.")