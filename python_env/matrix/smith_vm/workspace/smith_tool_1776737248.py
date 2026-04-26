# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Audit Script – Validation of Engine (architect) thought
# --------------------------------------------------------------
# This script reproduces the key calculations from the agent's internal
# thought process and checks:
#   1. Numerical consistency (tolerance 1e-2 relative)
#   2. Invariant bounds for the stiffnesses (Phi_N, Phi_Delta)
#   3. Stability criterion based on dimensionless jerk variance
# --------------------------------------------------------------

import numpy as np

# ------------------------------------------------------------------
# Input data (as supplied by the agent)
# ------------------------------------------------------------------
phi_N   = 0.78          # Φ_N / I0
phi_D   = 0.35          # Φ_Δ / I0
phi_dot_N = 2.1e3       # s^-1
phi_dot_D = 8.7e3       # s^-1
xi_inv2 = 4.2e6         # s^-2  (=> ξ = 1/sqrt(xi_inv2))
J_source = 1.5e12       # s^-3  (source jerk)

# ------------------------------------------------------------------
# Derived constants
# ------------------------------------------------------------------
xi = 1.0 / np.sqrt(xi_inv2)                # s
psi   = np.log(phi_N)                      # ln(Φ_N/I0)
psi_dot = phi_dot_N / phi_N                # s^-1
# Second derivatives approximated via ξ scaling (as in the thought)
phi_ddot_N = phi_dot_N / xi
phi_ddot_D = phi_dot_D / xi
psi_ddot   = phi_ddot_N/phi_N - psi_dot**2
psi_dddot  = psi_ddot / xi
phi_dddot_D = phi_ddot_D / xi

# ------------------------------------------------------------------
# Probabilities and entropy derivatives
# ------------------------------------------------------------------
e_psi = np.exp(psi)                 # should equal phi_N
den   = e_psi + phi_D
p_N   = e_psi / den
p_D   = phi_D / den

# dS/dpsi
dS_dpsi = -p_N * np.log(p_D/p_N)
# d2S/dpsi2
dS_dpsi2 = -p_N*(1-p_N)*(np.log(phi_D)-psi) - p_N
# d3S/dpsi3 (value taken from the thought; we keep it for verification)
dS_dpsi3 = 0.089   # approx.

# ------------------------------------------------------------------
# Jerk components (discrete third derivative analogue)
# ------------------------------------------------------------------
J_psi = (dS_dpsi)*psi_dddot \
        + 3*(dS_dpsi2)*psi_dot*psi_ddot \
        + (dS_dpsi3)*psi_dot**3

J_Delta = (0.802)*phi_dddot_D \
          + 3*(-2.857)*phi_dot_D*phi_ddot_D   # using the numbers from the thought

J_total = J_psi + J_Delta + J_source

# ------------------------------------------------------------------
# Invariant checks (stiffnesses)
# ------------------------------------------------------------------
# We do not have λ and I0 explicitly, but we can evaluate the
# dimensionless combinations that determine the boundaries:
shredding_cond = phi_N**2 + 3*phi_D**2   # should be < 1 for stability
freeze_cond    = 3*phi_N**2 + phi_D**2   # should be < 1 for stability

# ------------------------------------------------------------------
# Stability metric (dimensionless jerk variance)
# ------------------------------------------------------------------
omega = 1.0/xi                     # ξ⁻¹  (natural frequency)
omega_psi = omega * np.exp(-psi/2.0)   # ψ‑modulated frequency
jerk_natural = omega_psi**3        # natural jerk scale
dimensionless_jerk = J_total / jerk_natural
variance_dimless   = dimensionless_jerk**2   # Var(𝒥̃)

# ------------------------------------------------------------------
# Tolerance for numerical agreement
# ------------------------------------------------------------------
tol = 1e-2   # 1% relative tolerance

def approx_equal(a, b, rel=tol):
    return np.isclose(a, b, rtol=rel, atol=0.0)

# ------------------------------------------------------------------
# Validation report
# ------------------------------------------------------------------
print("=== Omega Protocol Audit Report ===")
print(f"ξ = {xi:.3e} s")
print(f"ψ = ln(Φ_N/I0) = {psi:.6f}")
print(f"ψ̇ = {psi_dot:.3e} s⁻¹")
print(f"ψ̈ = {psi_ddot:.3e} s⁻²")
print(f"ψ̇̈ = {psi_dddot:.3e} s⁻³")
print()
print("Entropy derivatives:")
print(f"  ∂S/∂ψ   = {dS_dpsi:.6f}")
print(f"  ∂²S/∂ψ² = {dS_dpsi2:.6f}")
print(f"  ∂³S/∂ψ³ = {dS_dpsi3:.6f}")
print()
print("Jerk components:")
print(f"  𝒥_I^ψ   = {J_psi:.3e} s⁻³")
print(f"  𝒥_I^Δ   = {J_Delta:.3e} s⁻³")
print(f"  𝒥_source= {J_source:.3e} s⁻³")
print(f"  𝒥_I total= {J_total:.3e} s⁻³")
print()
print("Invariant boundary checks:")
print(f"  Φ_N² + 3Φ_Δ² = {shredding_cond:.6f}  (shredding if ≥ 1)")
print(f"  3Φ_N² + Φ_Δ² = {freeze_cond:.6f}    (freeze if ≥ 1)")
print()
print("Stability assessment:")
print(f"  ω = ξ⁻¹ = {omega:.2f} s⁻¹")
print(f"  ω_ψ = ω·e^{-ψ/2} = {omega_psi:.2f} s⁻¹")
print(f"  Natural jerk scale ω_ψ³ = {jerk_natural:.3e} s⁻³")
print(f"  Dimensionless jerk 𝒥̃ = 𝒥_I/ω_ψ³ = {dimensionless_jerk:.3f}")
print(f"  Dimensionless variance Var(𝒥̃) = {variance_dimless:.3f}")
print()
# Numerical consistency checks
checks = [
    ("ψ", psi, np.log(0.78)),
    ("ψ̇", psi_dot, 2.1e3/0.78),
    ("ψ̈", psi_ddot, (phi_dot_N/xi)/0.78 - (2.1e3/0.78)**2),
    ("ψ̇̈", psi_dddot, ((phi_dot_N/xi)/0.78 - (2.1e3/0.78)**2)/xi),
    ("𝒥_I^ψ", J_psi, -1.96e9 + 7.29e9 + 1.74e9),  # recomputed from parts
    ("𝒥_I^Δ", J_Delta, 0.802*3.63e10 + 3*(-2.857)*8.7e3*1.78e7),
    ("𝒥_I total", J_total, 2.07e11),
]
all_ok = True
for name, val, ref in checks:
    if not approx_equal(val, ref):
        print(f"[FAIL] {name}: got {val:.3e}, expected {ref:.3e}")
        all_ok = False
    else:
        print(f"[OK]   {name}: {val:.3e}")
if all_ok:
    print("\nAll numerical values agree with the agent's thought within tolerance.")
else:
    print("\nNumerical discrepancies detected – review the thought.")

# Invariant compliance
if shredding_cond >= 1.0:
    print("\n[VIOLATION] Shredding boundary approached or exceeded (Φ_N²+3Φ_Δ² ≥ 1).")
else:
    print(f"\n[OK] Shredding condition satisfied: {shredding_cond:.6f} < 1.")
if freeze_cond >= 1.0:
    print("[VIOLATION] Freeze boundary approached or exceeded (3Φ_N²+Φ_Δ² ≥ 1).")
else:
    print(f"[OK] Freeze condition satisfied: {freeze_cond:.6f} < 1.")

# Stability criterion (threshold of order 1 for variance)
if variance_dimless > 1.0:
    print(f"\n[INSTABILITY] Dimensionless jerk variance {variance_dimless:.2f} > 1 → unstable.")
else:
    print(f"\n[STABLE] Dimensionless jerk variance {variance_dimless:.2f} ≤ 1 → stable.")
print("\n=== End of Audit ===")