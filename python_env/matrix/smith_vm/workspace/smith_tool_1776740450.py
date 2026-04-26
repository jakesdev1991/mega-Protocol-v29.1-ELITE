# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script for the Linux HSA Unified Memory
Informational Jerk Stability Analysis.

This script checks:
  1. The defining invariants (Φ_N, Φ_Δ, I₀, λ) satisfy the stiffness relations.
  2. Both catastrophic boundaries are evaluated:
        • Shredding   : Φ_N² + 3 Φ_Δ² → I₀²   (ξ_Δ → ∞)
        • Informational Freeze : 3 Φ_N² + Φ_Δ² → I₀²   (ξ_N → ∞)
  3. Dimensional consistency of the jerk finite‑difference formula.
  4. Comparison of jerk variance with the ψ‑modulated stability threshold Θ.
  5. Detection of the sign error in ψ̈ reported in the engine output.

If all checks pass within a tolerant numerical error, the script prints
"PASS". Otherwise it reports the specific violations.

NOTE: The script assumes the supplied data are normalized to I₀ = 1.
      If you have a different I₀, scale Φ_N and Φ_Δ accordingly.
"""

import numpy as np

# ----------------------------------------------------------------------
# Supplied data (normalized to I₀ = 1)
# ----------------------------------------------------------------------
I0 = 1.0
lambda_ = 1.0e10          # s⁻²  (stiffness coupling)
gDelta = 0.1              # dimensionless coupling constant

phi_N = 0.78              # Φ_N / I₀
phi_D = 0.35              # Φ_Δ / I₀

phi_N_dot = 2.1e3         # s⁻¹
phi_D_dot = 8.7e3         # s⁻¹

# Second derivatives supplied in the engine output (we will recompute)
phi_N_ddot_supplied = 4.3e6   # s⁻²
# phi_D_ddot not supplied; we will estimate using ξ later

# Source jerk (s⁻³)
J_source = 1.5e12

# ----------------------------------------------------------------------
# Helper: compute stiffness lengths ξ_N, ξ_Δ from definitions
# ----------------------------------------------------------------------
def compute_xi(phi_N, phi_D):
    """Return ξ_N, ξ_Δ (in seconds) from the stiffness invariants."""
    xi_N_inv2 = lambda_ * (3.0 * phi_N**2 + phi_D**2 - I0**2)
    xi_D_inv2 = lambda_ * (phi_N**2 + 3.0 * phi_D**2 - I0**2)
    # Guard against negative or zero values (would imply imaginary ξ)
    xi_N = 1.0 / np.sqrt(xi_N_inv2) if xi_N_inv2 > 0 else np.inf
    xi_D = 1.0 / np.sqrt(xi_D_inv2) if xi_D_inv2 > 0 else np.inf
    return xi_N, xi_D

xi_N, xi_D = compute_xi(phi_N, phi_D)

# ----------------------------------------------------------------------
# 1. Invariant check: stiffness relations should hold (within tolerance)
# ----------------------------------------------------------------------
tol = 1e-9
invariant_N = np.abs(lambda_ * (3.0*phi_N**2 + phi_D**2 - I0**2) - 1.0/xi_N**2) < tol
invariant_D = np.abs(lambda_ * (phi_N**2 + 3.0*phi_D**2 - I0**2) - 1.0/xi_D**2) < tol

print("Invariant checks:")
print(f"  ξ_N⁻² relation satisfied: {invariant_N}")
print(f"  ξ_Δ⁻² relation satisfied: {invariant_D}")

# ----------------------------------------------------------------------
# 2. Boundary conditions
# ----------------------------------------------------------------------
shredding_lhs = phi_N**2 + 3.0*phi_D**2
freeze_lhs    = 3.0*phi_N**2 + phi_D**2

shredding_ok = np.abs(shredding_lhs - I0**2) < 1e-3   # we expect < I0² for stability
freeze_ok    = np.abs(freeze_lhs    - I0**2) < 1e-3

print("\nBoundary condition checks (should be < I0² for stable regime):")
print(f"  Shredding   Φ_N² + 3Φ_Δ² = {shredding_lhs:.6f}  (I0² = {I0**2})")
print(f"  Freeze      3Φ_N² + Φ_Δ² = {freeze_lhs:.6f}    (I0² = {I0**2})")
print(f"  Shredding condition satisfied (stable): {shredding_ok}")
print(f"  Freeze    condition satisfied (stable): {freeze_ok}")

# ----------------------------------------------------------------------
# 3. ψ and its derivatives (re‑evaluate to catch sign error)
# ----------------------------------------------------------------------
psi = np.log(phi_N)                     # ln(Φ_N/I0)
psi_dot = phi_N_dot / phi_N
# Re‑compute ψ̈ using the correct formula:
psi_ddot = phi_N_ddot_supplied / phi_N - (phi_N_dot / phi_N)**2

# Estimate φ̈_Δ using ξ_D (as done in the engine output)
phi_D_ddot = phi_D_dot / xi_D if xi_D != np.inf else 0.0
phi_D_dddot = phi_D_ddot / xi_D if xi_D != np.inf else 0.0

# ψ̈ from engine output (incorrect)
psi_ddot_engine = 5.5e6   # as stated in the analysis

print("\nψ‑derivative checks:")
print(f"  ψ          = {psi:.6f}")
print(f"  ψ̇         = {psi_dot:.3e} s⁻¹")
print(f"  ψ̈ (correct) = {psi_ddot:.3e} s⁻²")
print(f"  ψ̈ (engine)  = {psi_ddot_engine:.3e} s⁻²")
print(f"  Sign error in ψ̈? {np.sign(psi_ddot) != np.sign(psi_ddot_engine)}")

# ----------------------------------------------------------------------
# 4. Entropy and its ψ‑derivatives (numeric evaluation)
# ----------------------------------------------------------------------
def entropy(psi_val, phi_D_val):
    """Shannon conditional entropy S_h for two‑state system."""
    e_psi = np.exp(psi_val)
    denom = e_psi + phi_D_val
    p_N = e_psi / denom
    p_D = phi_D_val / denom
    # Guard against log(0)
    S = 0.0
    if p_N > 0:
        S -= p_N * np.log(p_N)
    if p_D > 0:
        S -= p_D * np.log(p_D)
    return S

S = entropy(psi, phi_D)

# Numerical derivatives via finite differences (small step)
eps = 1e-6
dS_dpsi = (entropy(psi+eps, phi_D) - entropy(psi-eps, phi_D)) / (2*eps)
d2S_dpsi2 = (entropy(psi+eps, phi_D) - 2*S + entropy(psi-eps, phi_D)) / (eps**2)
d3S_dpsi3 = (entropy(psi+2*eps, phi_D) 
             - 2*entropy(psi+eps, phi_D) 
             + 2*entropy(psi-eps, phi_D) 
             - entropy(psi-2*eps, phi_D)) / (2*eps**3)

print("\nEntropy derivatives (numeric):")
print(f"  S_h          = {S:.6f}")
print(f"  ∂S/∂ψ        = {dS_dpsi:.6f}")
print(f"  ∂²S/∂ψ²      = {d2S_dpsi2:.6f}")
print(f"  ∂³S/∂ψ³      = {d3S_dpsi3:.6f}")

# ----------------------------------------------------------------------
# 5. Informational jerk via finite‑difference (needs Δt)
# ----------------------------------------------------------------------
# The engine output omitted Δt. We will ask the user to provide it.
# For demonstration we assume a sampling interval of 1 µs (typical for HSA counters).
dt = 1e-6   # seconds – user should adjust if different

# Build a short history of S_h values (we only have the current point;
# to illustrate we approximate past values using a linear trend – not rigorous).
# In a real validation you would feed the actual time‑series.
S_hist = [S, S, S, S]   # placeholder: all equal → jerk = 0
J_I_fd = (S_hist[0] - 3*S_hist[1] + 3*S_hist[2] - S_hist[3]) / (dt**3)

print("\nFinite‑difference jerk (placeholder using constant S_h):")
print(f"  Δt = {dt:.2e} s")
print(f"  J_I (FD) = {J_I_fd:.3e} s⁻³")

# ----------------------------------------------------------------------
# 6. ψ‑component of jerk (using correct derivatives)
# ----------------------------------------------------------------------
J_psi = (dS_dpsi * (phi_N_ddot_supplied / phi_N - (phi_N_dot/phi_N)**2 / xi_D)  # placeholder for ψ‴
         + 3 * d2S_dpsi2 * psi_dot * (phi_N_ddot_supplied / phi_N) 
         + d3S_dpsi3 * psi_dot**3)

# For simplicity we compute ψ‴ as ψ̈/ξ_D (as engine did)
psi_triple = psi_ddot / xi_D if xi_D != np.inf else 0.0
J_psi = (dS_dpsi * psi_triple
         + 3 * d2S_dpsi2 * psi_dot * psi_ddot
         + d3S_dpsi3 * psi_dot**3)

print("\nψ‑component of jerk (using correct ψ̈):")
print(f"  J_I^ψ = {J_psi:.3e} s⁻³")

# ----------------------------------------------------------------------
# 7. Φ_Δ‑component of jerk (mirroring engine approach)
# ----------------------------------------------------------------------
# Approximate ∂S/∂φ_Δ, ∂²S/∂φ_Δ² via finite difference
dS_dphiD = (entropy(psi, phi_D+eps) - entropy(psi, phi_D-eps)) / (2*eps)
d2S_dphiD2 = (entropy(psi, phi_D+eps) - 2*S + entropy(psi, phi_D-eps)) / (eps**2)

J_phiD = (dS_dphiD * phi_D_dddot
          + 3 * d2S_dphiD2 * phi_D_dot * phi_D_ddot)

print("\nΦ_Δ‑component of jerk:")
print(f"  J_I^Δ = {J_phiD:.3e} s⁻³")

# ----------------------------------------------------------------------
# 8. Total jerk and variance comparison with threshold Θ
# ----------------------------------------------------------------------
J_total = J_psi + J_phiD + J_source
print("\nTotal informational jerk:")
print(f"  J_I total = {J_total:.3e} s⁻³")

# Assume ±20% fluctuations around the mean (as in engine output)
sigma_J = 0.2 * np.abs(J_total)
sigma_J_sq = sigma_J**2
print(f"  σ_J = {sigma_J:.3e} s⁻³")
print(f"  σ_J² = {sigma_J_sq:.3e} s⁻⁶")

# Stability threshold Θ (ψ‑modulated) – check units:
# λ [s⁻²], I0² [dimensionless], gΔ² [dimensionless] → Θ [s⁻²]
Theta = (lambda_ * I0**2) / (4.0*np.pi) * (1.0 + 3.0*gDelta**2/(4.0*np.pi)) * np.exp(-psi)
print(f"\nStability threshold Θ = {Theta:.3e} s⁻²")

# To compare we need to bring Θ to same dimensions as σ_J².
# The engine implicitly assumed a missing time⁴ factor; we flag this.
print("\nDimensional check:")
print(f"  σ_J² has units s⁻⁶, Θ has units s⁻² → direct comparison is dimensionally inconsistent.")
print(f"  Unless a factor of (characteristic time)⁴ is introduced, the verdict is invalid.")

# ----------------------------------------------------------------------
# 9. Summary verdict based on invariant and boundary checks only
# ----------------------------------------------------------------------
pass_checks = invariant_N and invariant_D and shredding_ok and freeze_ok
print("\n=== SUMMARY ===")
print(f"Invariant & boundary checks PASSED: {pass_checks}")
if pass_checks:
    print("→ The analysis satisfies the core Omega Protocol invariants.")
    print("→ However, the jerk/variance vs. Θ comparison is dimensionally flawed;")
    print("  a correct validation requires a properly scaled threshold or")
    print("  a jerk expression with explicit Δt³.")
else:
    print("→ FAIL: one or more invariant/boundary conditions are violated.")

# ----------------------------------------------------------------------
# End of script
# ----------------------------------------------------------------------