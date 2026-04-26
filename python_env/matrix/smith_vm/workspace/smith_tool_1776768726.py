# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Validates the Engine's Linux HSA unified memory informational jerk stability
analysis against the Omega Physics Rubric v26.0.

Assumptions:
- Normalized data as given in the Engine's output:
    φ_N = Φ_N / I0 = 0.78
    φ_Δ = Φ_Δ / I0 = 0.35
    dotφ_N = 2.1e3 s⁻¹
    dotφ_Δ = 8.7e3 s⁻¹
    ξ⁻² = 4.2e6 s⁻²  → ξ = 1/√(ξ⁻²)
- Source jerk J_source = 1.5e12 s⁻³
- Relaxation‑time approximation: ddotφ ≈ dotφ / ξ, ddotψ ≈ ddotφ_N/φ_N - dotψ²,
  and higher derivatives obtained by dividing by ξ again.
- Entropy: Shannon conditional entropy S_h = -Σ p_i ln p_i with
    p_N ∝ φ_N, p_Δ ∝ φ_Δ  (normalized so p_N + p_Δ = 1).
- Jerk components as per the Engine's formulae.
"""

import math
from typing import Tuple

# ----------------------------------------------------------------------
# Helper functions for entropy derivatives
# ----------------------------------------------------------------------
def entropy_and_derivatives(phi_N: float, phi_Delta: float) -> Tuple[float, float, float, float, float, float]:
    """
    Returns:
        S          : Shannon entropy
        dS_dphiN   : ∂S/∂φ_N
        d2S_dphiN2 : ∂²S/∂φ_N²
        d3S_dphiN3 : ∂³S/∂φ_N³
        dS_dphiD   : ∂S/∂φ_Δ
        d2S_dphiD2 : ∂²S/∂φ_Δ²
    """
    s = phi_N + phi_Delta
    pN = phi_N / s
    pD = phi_Delta / s

    # Shannon entropy
    S = -(pN * math.log(pN) if pN > 0 else 0.0 +
          pD * math.log(pD) if pD > 0 else 0.0)

    # First derivatives
    dpN_dphiN = phi_Delta / (s * s)          # ∂p_N/∂φ_N
    dpD_dphiN = -phi_Delta / (s * s)         # ∂p_Δ/∂φ_N
    dpN_dphiD = -phi_N / (s * s)             # ∂p_N/∂φ_Δ
    dpD_dphiD = phi_N / (s * s)              # ∂p_Δ/∂φ_Δ

    dS_dphiN = -(dpN_dphiN * (math.log(pN) + 1) +
                 dpD_dphiN * (math.log(pD) + 1))
    dS_dphiD = -(dpN_dphiD * (math.log(pN) + 1) +
                 dpD_dphiD * (math.log(pD) + 1))

    # Second derivatives (analytic, but we compute via sympy‑like manual diff)
    # For brevity we compute numerically using a small step; this is sufficient for validation.
    eps = 1e-8
    def S_of(phiN, phiD):
        ss = phiN + phiD
        pNn = phiN / ss
        pDd = phiD / ss
        return -(pNn * math.log(pNn) if pNn > 0 else 0.0 +
                 pDd * math.log(pDd) if pDd > 0 else 0.0)

    d2S_dphiN2 = (S_of(phi_N + eps, phi_Delta) - 2 * S_of(phi_N, phi_Delta) + S_of(phi_N - eps, phi_Delta)) / (eps * eps)
    d2S_dphiD2 = (S_of(phi_N, phi_Delta + eps) - 2 * S_of(phi_N, phi_Delta) + S_of(phi_N, phi_Delta - eps)) / (eps * eps)

    # Third derivative w.r.t φ_N (numeric)
    d3S_dphiN3 = (S_of(phi_N + 2*eps, phi_Delta) -
                  3 * S_of(phi_N + eps, phi_Delta) +
                  3 * S_of(phi_N - eps, phi_Delta) -
                  S_of(phi_N - 2*eps, phi_Delta)) / (2 * eps**3)

    return S, dS_dphiN, d2S_dphiN2, d3S_dphiN3, dS_dphiD, d2S_dphiD2

# ----------------------------------------------------------------------
# Main validation
# ----------------------------------------------------------------------
def main():
    # ----- Input data (normalized) -----
    phi_N = 0.78
    phi_Delta = 0.35
    dot_phi_N = 2.1e3          # s⁻¹
    dot_phi_Delta = 8.7e3      # s⁻¹
    xi_inv2 = 4.2e6            # s⁻²
    xi = 1.0 / math.sqrt(xi_inv2)   # s
    J_source = 1.5e12          # s⁻³

    # ----- Derived quantities -----
    psi = math.log(phi_N)                     # ln(Φ_N/I0)
    dot_psi = dot_phi_N / phi_N               # dψ/dt

    # Relaxation‑time approximations
    ddot_phi_N = dot_phi_N / xi
    ddot_phi_Delta = dot_phi_Delta / xi
    ddot_psi = ddot_phi_N / phi_N - dot_psi**2
    ddot_dot_psi = ddot_psi / xi              # d³ψ/dt³ (approx)
    ddot_dot_phi_Delta = ddot_phi_Delta / xi  # d³φ_Δ/dt³ (approx)

    # ----- Entropy and its derivatives -----
    S, dS_dphiN, d2S_dphiN2, d3S_dphiN3, dS_dphiD, d2S_dphiD2 = entropy_and_derivatives(phi_N, phi_Delta)

    # Chain rule for ψ‑derivatives (φ_N = e^ψ)
    dS_dpsi = dS_dphiN * phi_N                     # ∂S/∂ψ
    d2S_dpsi2 = (d2S_dphiN2 * phi_N**2) + (dS_dphiN * phi_N)
    d3S_dpsi3 = (d3S_dphiN3 * phi_N**3) +
                (3 * d2S_dphiN2 * phi_N**2) +
                (dS_dphiN * phi_N)

    # ----- Jerk components -----
    J_psi = (dS_dpsi * ddot_dot_psi +
             3 * d2S_dpsi2 * dot_psi * ddot_psi +
             d3S_dpsi3 * dot_psi**3)

    J_Delta = (dS_dphiD * ddot_dot_phi_Delta +
               3 * d2S_dphiD2 * dot_phi_Delta * ddot_phi_Delta)

    J_total = J_psi + J_Delta + J_source

    # ----- Stability metrics -----
    omega = 1.0 / xi                         # s⁻¹
    omega_psi = omega * math.exp(-psi / 2.0) # ψ‑modulated frequency
    natural_jerk_scale = omega_psi ** 3      # s⁻³
    sigma_J2 = J_total ** 2                  # variance proxy (single‑sample)
    dimless_var = sigma_J2 / (omega_psi ** 6)

    # ----- Boundary checks -----
    shredding_val = phi_N**2 + 3 * phi_Delta**2
    freeze_val = 3 * phi_N**2 + phi_Delta**2

    # ----- Tolerance for comparison with Engine's reported numbers -----
    rel_tol = 1e-2   # 1 %

    # Expected values from Engine's narrative (approx)
    expected = {
        "psi": math.log(0.78),
        "dot_psi": 2.69e3,
        "ddot_phi_N": 4.29e6,
        "ddot_phi_Delta": 1.78e7,
        "ddot_psi": -1.74e6,
        "ddot_dot_psi": -3.55e9,
        "ddot_dot_phi_Delta": 3.63e10,
        "p_N": 0.690,
        "p_Delta": 0.310,
        "S": None,  # not explicitly given
        "dS_dpsi": None,
        "d2S_dpsi2": None,
        "d3S_dpsi3": None,
        "J_psi": 7.07e9,
        "J_Delta": -1.30e12,
        "J_total": 2.07e11,
        "omega": 2040.8,
        "omega_psi": 2305.0,
        "natural_jerk_scale": 1.22e10,
        "sigma_J2": 4.28e22,
        "dimless_var": 287.0,
        "shredding_val": 0.9759,
        "freeze_val": 1.9477,
    }

    # Actual computed values
    actual = {
        "psi": psi,
        "dot_psi": dot_psi,
        "ddot_phi_N": ddot_phi_N,
        "ddot_phi_Delta": ddot_phi_Delta,
        "ddot_psi": ddot_psi,
        "ddot_dot_psi": ddot_dot_psi,
        "ddot_dot_phi_Delta": ddot_dot_phi_Delta,
        "p_N": phi_N / (phi_N + phi_Delta),
        "p_Delta": phi_Delta / (phi_N + phi_Delta),
        "S": S,
        "dS_dpsi": dS_dpsi,
        "d2S_dpsi2": d2S_dpsi2,
        "d3S_dpsi3": d3S_dpsi3,
        "J_psi": J_psi,
        "J_Delta": J_Delta,
        "J_total": J_total,
        "omega": omega,
        "omega_psi": omega_psi,
        "natural_jerk_scale": natural_jerk_scale,
        "sigma_J2": sigma_J2,
        "dimless_var": dimless_var,
        "shredding_val": shredding_val,
        "freeze_val": freeze_val,
    }

    # ----- Validation -----
    print("=== Omega Protocol Validation Report ===\n")
    all_ok = True
    for key in expected:
        exp = expected[key]
        act = actual[key]
        if exp is None:
            continue  # skip if Engine didn't give a number
        diff = abs(act - exp)
        rel = diff / (abs(exp) + 1e-30)
        ok = rel <= rel_tol
        if not ok:
            all_ok = False
            print(f"[FAIL] {key}: expected {exp:.6e}, got {act:.6e} (rel err {rel:.2e})")
        else:
            print(f"[OK]   {key}: {act:.6e}")

    print("\n--- Boundary Checks ---")
    print(f"Shredding condition (φ_N² + 3φ_Δ²) = {shredding_val:.6f}  (threshold = 1.0)")
    print(f"Freeze condition (3φ_N² + φ_Δ²)   = {freeze_val:.6f}    (threshold = 1.0)")
    if shredding_val < 1.0 - 1e-9:
        print("[OK]  System is NOT at shredding boundary.")
    else:
        all_ok = False
        print("[FAIL] System AT or PAST shredding boundary.")
    if freeze_val > 1.0 + 1e-9:
        print("[OK]  System is NOT at freeze boundary.")
    else:
        all_ok = False
        print("[FAIL] System AT or PAST freeze boundary.")

    print("\n--- Stability Assessment ---")
    print(f"Dimensionless jerk variance = {dimless_var:.3f}")
    if dimless_var > 1.0:
        print("[RESULT] Variance ≫ 1 → Unstable regime (as Engine concluded).")
    else:
        print("[RESULT] Variance ≲ 1 → Stable regime.")

    # ----- Enforce Omega Protocol Invariants (assertions) -----
    # These will raise AssertionError if any invariant is violated.
    assert math.isfinite(psi), "ψ must be finite"
    assert xi > 0.0, "Relaxation time ξ must be positive"
    assert 0.0 <= phi_N / (phi_N + phi_Delta) <= 1.0, "Probability p_N out of bounds"
    assert 0.0 <= phi_Delta / (phi_N + phi_Delta) <= 1.0, "Probability p_Δ out of bounds"
    # Entropy must be non‑negative
    assert S >= 0.0, "Shannon entropy must be non‑negative"
    # Jerk components can be any real number; no further constraint.
    # Boundaries: system must be strictly inside safe region (not exactly on the manifold)
    assert shredding_val < 1.0, "Shredding boundary violated or reached"
    assert freeze_val > 1.0, "Freeze boundary violated or reached"

    if all_ok:
        print("\n=== VALIDATION PASSED: Engine output is mathematically sound and compliant with Omega Protocol invariants ===")
    else:
        print("\n=== VALIDATION FAILED: Discrepancies detected ===")
        raise AssertionError("Validation failed – see above messages.")

if __name__ == "__main__":
    main()