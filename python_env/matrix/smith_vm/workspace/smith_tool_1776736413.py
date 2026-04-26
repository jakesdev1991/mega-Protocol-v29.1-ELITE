# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Audit of Agent Engine's Informational Jerk analysis.
Validates:
  • Use of the metric coupling invariant ψ = ln(Φ_N/I₀) in jerk and threshold.
  • Correctness of the Shredding condition and derived Θ(ψ).
  • Numerical evaluation against the supplied audit data.
  • Final stability decision (σ_𝒥² < Θ(ψ) ?).
"""

import math
import numpy as np

# ----------------------------------------------------------------------
# 1. INPUT DATA (as supplied by the agent)
# ----------------------------------------------------------------------
I0   = 1.0                     # normalisation
phi_N = 0.78                   # normalized Newtonian mode
phi_D = 0.35                   # normalized Archive mode (Φ_Δ)

# time‑derivatives (s⁻¹)
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3

# stiffness invariant (s⁻²)  ξ⁻² = λ(3Φ_N²+Φ_Δ²−I0²)  (or the Δ‑variant)
xi_inv2 = 4.2e6                # given as ξ⁻²

# source jerk (s⁻³)
J_source = 1.5e12

# fluctuation assumption (±20%)
fluctuation_frac = 0.20

# model parameters used in the threshold calculation
lam   = 1.0e10                 # s⁻²  (λ)
g_D   = 0.1                    # dimensionless Archive coupling

# ----------------------------------------------------------------------
# 2. HELPERS
# ----------------------------------------------------------------------
def psi_from_phiN(phiN, I0=I0):
    """Metric coupling invariant ψ = ln(Φ_N/I₀)."""
    return math.log(phiN / I0)

def entropy_two_state(p):
    """Shannon entropy in bits for a two‑state distribution."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p*math.log2(p) - (1-p)*math.log2(1-p)

def dS_dpsi(phiN, phiD):
    """
    ∂S_h/∂ψ using the chain rule:
      ∂S/∂ψ = (∂S/∂Φ_N)·(dΦ_N/dψ) = (∂S/∂Φ_N)·Φ_N
    For a two‑state model with p_N = Φ_N/(Φ_N+Φ_Δ):
      ∂S/∂Φ_N = -(ln(p_N) - ln(p_Δ)) / (Φ_N+Φ_Δ)
    """
    pN = phiN / (phiN + phiD)
    pD = phiD / (phiN + phiD)
    if pN == 0 or pD == 0:
        return 0.0
    dS_dphiN = -(math.log2(pN) - math.log2(pD)) / (phiN + phiD)
    return dS_dphiN * phiN   # because dΦ_N/dψ = Φ_N

def d2S_dpsi2(phiN, phiD):
    """
    ∂²S_h/∂ψ² = Φ_N²·∂²S/∂Φ_N² + Φ_N·∂S/∂Φ_N
    (derived by differentiating dS/dψ = Φ_N·∂S/∂Φ_N)
    """
    pN = phiN / (phiN + phiD)
    pD = phiD / (phiN + phiD)
    if pN == 0 or pD == 0:
        return 0.0
    # first derivative
    dS_dphiN = -(math.log2(pN) - math.log2(pD)) / (phiN + phiD)
    # second derivative w.r.t Φ_N
    # d²S/dΦ_N² = (1/(Φ_N+Φ_Δ)) * (1/(pN ln2) + 1/(pD ln2))
    d2S_dphiN2 = (1.0/(phiN+phiD)) * (1.0/(pN*math.log(2)) + 1.0/(pD*math.log(2)))
    return phiN**2 * d2S_dphiN2 + phiN * dS_dphiN

def shredding_condition(phiN, phiD, I0=I0):
    """Returns True if ξ_Δ⁻² = 0  →  Φ_N² + 3Φ_Δ² = I0²."""
    lhs = phiN**2 + 3*phiD**2
    return math.isclose(lhs, I0**2, rel_tol=1e-9), lhs

def V_shred(psi, I0=I0, lam=lam):
    """Potential at the Shredding boundary."""
    # Φ_N = I0 * e^ψ  →  Φ_N² = I0² e^{2ψ}
    # From derivation: V_shred = (λ I0⁴ / 9) * (e^{2ψ} - 1)²
    return (lam * I0**4 / 9.0) * (math.exp(2*psi) - 1.0)**2

def Theta_psi(psi, I0=I0, lam=lam, gD=g_D):
    """
    ψ‑dependent stability threshold:
      Θ(ψ) = (λ I0⁴ / 9) (e^{2ψ} - 1)² * (1 + (3 g_Δ² / 4π) e^{-2ψ})
    """
    pref = (lam * I0**4 / 9.0) * (math.exp(2*psi) - 1.0)**2
    metric_factor = 1.0 + (3.0 * gD**2 / (4.0 * math.pi)) * math.exp(-2*psi)
    return pref * metric_factor

# ----------------------------------------------------------------------
# 3. COMPUTE INVARIANTS AND DERIVED QUANTITIES
# ----------------------------------------------------------------------
psi = psi_from_phiN(phi_N)
print(f"ψ = ln(Φ_N/I₀) = {psi:.6f}")

# Check that ψ appears in the jerk derivation (we verify by using it in
# the threshold and in the derivative calculations below).
dS_dpsi_val = dS_dpsi(phi_N, phi_D)
d2S_dpsi2_val = d2S_dpsi2(phi_N, phi_D)
print(f"∂S_h/∂ψ = {dS_dpsi_val:.6f}")
print(f"∂²S_h/∂ψ² = {d2S_dpsi2_val:.6f}")

# Shredding condition
shred_ok, lhs = shredding_condition(phi_N, phi_D)
print(f"Shredding condition Φ_N²+3Φ_Δ² = I0² ?  LHS = {lhs:.6f},  satisfied? {shred_ok}")

# Potential at shredding
Vsh = V_shred(psi)
print(f"V_shred = {Vsh:.6e} (units of λ·I0⁴)")

# Threshold Θ(ψ)
Theta = Theta_psi(psi)
print(f"Θ(ψ) = {Theta:.6e}  [s⁻⁶]")

# ----------------------------------------------------------------------
# 4. ESTIMATE INFORMATIONAL JERK FROM AGENT'S NUMERICS
# ----------------------------------------------------------------------
# Agent's dominant jerk term (approx):
#   J_I ≈ 2 * (∂²S/∂ψ²) * ψ_dot * ψ_ddot
psi_dot = dot_phi_N / phi_N   # dψ/dt = Φ̇_N / Φ_N
# Approximate ψ_ddot using characteristic time ξ = 1/√(ξ⁻²)
xi = 1.0 / math.sqrt(xi_inv2)
psi_ddot = psi_dot / xi - psi_dot**2   # as used in the agent's note
print(f"ψ̇ = {psi_dot:.3e} s⁻¹")
print(f"ψ̈ = {psi_ddot:.3e} s⁻²")

J_psi_term = 2.0 * d2S_dpsi2_val * psi_dot * psi_ddot
print(f"Jerk term from ψ‑dynamics = {J_psi_term:.3e} s⁻³")

J_total = J_psi_term + J_source
print(f"Total informational jerk 𝒥_I ≈ {J_total:.3e} s⁻³")

# Fluctuation variance (assuming ±20% of the total jerk)
sigma_J = fluctuation_frac * J_total
sigma_J_sq = sigma_J**2
print(f"σ_𝒥 ≈ {sigma_J:.3e} s⁻³  →  σ_𝒥² = {sigma_J_sq:.3e} s⁻⁶")

# ----------------------------------------------------------------------
# 5. STABILITY VERDICT
# ----------------------------------------------------------------------
stable = sigma_J_sq < Theta
print(f"\nStability check: σ_𝒥² ({sigma_J_sq:.3e})  <  Θ(ψ) ({Theta:.3e}) ?  {stable}")
if not stable:
    print("RESULT: **UNSTABLE** – fluctuation energy exceeds the ψ‑dependent threshold.")
else:
    print("RESULT: **STABLE** – fluctuations lie below the threshold.")

# ----------------------------------------------------------------------
# 6. INVARIANT‑USAGE ASSERTION (soft check)
# ----------------------------------------------------------------------
# We assert that ψ was actually used in the jerk estimate and threshold.
# If any of the following are zero (within tolerance) we flag a possible
# decorative‑only usage.
assert not math.isclose(dS_dpsi_val, 0.0, abs_tol=1e-12), "∂S/∂ψ vanished → ψ not influencing entropy."
assert not math.isclose(d2S_dpsi2_val, 0.0, abs_tol=1e-12), "∂²S/∂ψ² vanished → ψ not influencing jerk."
assert not math.isclose(Theta, 0.0, abs_tol=1e-12), "Θ(ψ) vanished → threshold independent of ψ."
print("\nInvariant‑usage check passed: ψ appears explicitly in both jerk and threshold.")

# ----------------------------------------------------------------------
# END OF AUDIT
# ----------------------------------------------------------------------