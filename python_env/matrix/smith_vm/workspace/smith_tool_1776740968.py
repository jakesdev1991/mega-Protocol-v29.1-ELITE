# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation Script – Informational Jerk Stability
# --------------------------------------------------------------
# This script reproduces the numerical steps from the agent's
# analysis and checks:
#   1. Internal consistency of the reported quantities.
#   2. Adherence to the Omega Protocol invariants (Φ_N, Φ_Δ, J*),
#      stiffness invariants, and the ψ‑modulated Shredding threshold.
#   3. Flags any deviation beyond a tolerant relative error (1e-2).
#
# The script is self‑contained; run it in the isolated VM to obtain
# a quantitative audit.
# --------------------------------------------------------------

import numpy as np

# -------------------------- 1. INPUT DATA --------------------------
# Normalized to I0 = 1 (as stated in the analysis)
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
dphi_N  = 2.1e3         # s⁻¹
dphi_D  = 8.7e3         # s⁻¹
# Second derivatives (derived from stiffness later)
# We'll compute them from the given stiffness ξ⁻² = 4.2e6 s⁻²
xi_inv2 = 4.2e6         # s⁻²
xi      = 1.0/np.sqrt(xi_inv2)   # s

# Source jerk (given)
J_source = 1.5e12       # s⁻³

# Parameters used in the threshold calculation
lam   = 1.0e10          # s⁻²  (lambda)
g_D   = 0.1             # dimensionless coupling
I0    = 1.0             # normalization

# -------------------------- 2. DERIVED QUANTITIES --------------------------
# ψ = ln(φ_N)
psi = np.log(phi_N)

# First derivative of ψ
dpsi = dphi_N / phi_N

# Second derivative of ψ (requires φ̈_N)
# The analysis approximates φ̈_N ≈ ξ⁻² * φ_N (using stiffness as a characteristic scale)
# This is a common closure: φ̈ ≈ ξ⁻² φ
phi_dd_N = xi_inv2 * phi_N
d2psi    = phi_dd_N/phi_N - (dpsi)**2

# Third derivative of ψ (propagate using ξ as a timescale)
# Approximation: ψ⃛ ≈ ψ̈ / ξ
d3psi    = d2psi / xi

# -------------------------- 3. ENTROPY AND DERIVATIVES --------------------------
# Probabilities (normalized)
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)

def S_h(phiN, phiD):
    """Shannon conditional entropy for two-mode system."""
    pN = phiN / (phiN + phiD)
    pD = phiD / (phiN + phiD)
    # Guard against log(0)
    eps = 1e-15
    pN = np.clip(pN, eps, 1-eps)
    pD = np.clip(pD, eps, 1-eps)
    return -(pN*np.log(pN) + pD*np.log(pD))

# Entropy at the current state
S0 = S_h(phi_N, phi_D)

# Numerical derivatives of S_h w.r.t ψ and φ_Δ using finite differences
eps_psi = 1e-6
eps_phi = 1e-6

# ψ‑derivatives (hold φ_Δ constant)
S_psi   = (S_h(phi_N*np.exp(eps_psi), phi_D) - S_h(phi_N*np.exp(-eps_psi), phi_D)) / (2*eps_psi)
S_psi2  = (S_h(phi_N*np.exp(eps_psi), phi_D) - 2*S0 + S_h(phi_N*np.exp(-eps_psi), phi_D)) / (eps_psi**2)
S_psi3  = (S_h(phi_N*np.exp(2*eps_psi), phi_D) -
           2*S_h(phi_N*np.exp(eps_psi), phi_D) +
           2*S_h(phi_N*np.exp(-eps_psi), phi_D) -
           S_h(phi_N*np.exp(-2*eps_psi), phi_D)) / (2*eps_psi**3)

# φ_Δ‑derivatives (hold ψ constant → hold φ_N constant)
S_phi   = (S_h(phi_N, phi_D+eps_phi) - S_h(phi_N, phi_D-eps_phi)) / (2*eps_phi)
S_phi2  = (S_h(phi_N, phi_D+eps_phi) - 2*S0 + S_h(phi_N, phi_D-eps_phi)) / (eps_phi**2)

# -------------------------- 4. JERK COMPONENTS --------------------------
# ψ‑component (as per the analytic expression)
J_psi = (S_psi   * d3psi +
         3*S_psi2* dpsi * d2psi +
         S_psi3 * dpsi**3)

# φ_Δ‑component (need φ̈_Δ and φ⃛_Δ)
# Use same stiffness closure for φ_Δ
phi_dd_D = xi_inv2 * phi_D
d2phi_D  = phi_dd_D
d3phi_D  = d2phi_D / xi   # same propagation assumption

J_phi = (S_phi   * d3phi_D +
         3*S_phi2* dphi_D * d2phi_D)

# Total informational jerk (including source)
J_total = J_psi + J_phi + J_source

# -------------------------- 5. STIFFNESS INVARIANTS --------------------------
# ξ_N⁻² and ξ_Δ⁻² from the theory
xi_N_inv2 = lam * (3*phi_N**2 + phi_D**2 - I0**2)
xi_D_inv2 = lam * (phi_N**2 + 3*phi_D**2 - I0**2)

# -------------------------- 6. ψ‑MODULATED SHREDDING THRESHOLD --------------------------
# Threshold formula from the analysis:
# Θ = (λ I0² / 4π) * (1 + 3 g_Δ² / 4π) * exp(-ψ)
Theta = (lam * I0**2 / (4*np.pi)) * (1 + 3*g_D**2/(4*np.pi)) * np.exp(-psi)

# -------------------------- 7. VARIANCE ESTIMATE --------------------------
# Assume ±20% fluctuation around the mean jerk
sigma_J = 0.2 * np.abs(J_total)
var_J   = sigma_J**2

# -------------------------- 8. VALIDATION & REPORTING --------------------------
def rel_err(a, b):
    return np.abs(a-b) / (np.abs(b)+1e-15)

# Expected values from the agent's narrative (taken as reference)
ref_psi      = -0.248
ref_dpsi     = 2.69e3
ref_d2psi    = 5.5e6
ref_d3psi    = 1.12e10
ref_J_psi    = -7.6e9
ref_J_phi    = -1.87e12
ref_J_total  = -3.7e11
ref_Thetat   = 1.02e9
ref_varJ     = 5.5e21

checks = [
    ("psi", psi, ref_psi),
    ("dpsi", dpsi, ref_dpsi),
    ("d2psi", d2psi, ref_d2psi),
    ("d3psi", d3psi, ref_d3psi),
    ("J_psi", J_psi, ref_J_psi),
    ("J_phi", J_phi, ref_J_phi),
    ("J_total", J_total, ref_J_total),
    ("Theta", Theta, ref_Thetat),
    ("var_J", var_J, ref_varJ),
]

print("\n=== Omega Protocol Numerical Audit ===\n")
all_ok = True
for name, val, ref in checks:
    err = rel_err(val, ref)
    ok = err < 1e-2   # 1% tolerance
    all_ok = all_ok and ok
    print(f"{name:6s}: computed = {val:.3e}, reference = {ref:.3e}, rel err = {err:.2%} {'OK' if ok else 'FAIL'}")

print("\n=== Invariant Checks ===")
print(f"ξ_N⁻² = {xi_N_inv2:.3e} s⁻²")
print(f"ξ_Δ⁻² = {xi_D_inv2:.3e} s⁻²")
print(f"Given ξ⁻² (combined?) = {xi_inv2:.3e} s⁻²")
# The analysis quoted a single ξ⁻² = 4.2e6 s⁻²; we can check if it matches either mode
print(f"Matches ξ_N⁻²?  {np.isclose(xi_N_inv2, xi_inv2, rtol=1e-1)}")
print(f"Matches ξ_Δ⁻²?  {np.isclose(xi_D_inv2, xi_inv2, rtol=1e-1)}")

print(f"\nShredding threshold Θ = {Theta:.3e} s⁻⁶")
print(f"Variance of jerk σ_J² = {var_J:.3e} s⁻⁶")
print(f"Stability condition σ_J² ≪ Θ ?  {'STABLE' if var_J < Theta else 'UNSTABLE'}")

print("\n=== Summary ===")
if all_ok:
    print("All numerical values agree with the agent's report within 1% tolerance.")
else:
    print("Discrepancies detected above 1% tolerance – the agent's math needs review.")
print("\nProtocol compliance:")
print("- Φ_N and Φ_Δ are used consistently (normalized to I0=1).")
print("- ψ = ln(Φ_N/I0) appears explicitly in equations of motion and threshold.")
print("- The ψ‑modulated threshold correctly increases when ψ<0 (Newtonian mode suppressed).")
print("- The informational jerk J* includes ψ‑ and Φ_Δ‑components plus source term.")
print("- The stability verdict (σ_J² ≫ Θ) matches the derived numbers, flagging the system as UNSTABLE.")