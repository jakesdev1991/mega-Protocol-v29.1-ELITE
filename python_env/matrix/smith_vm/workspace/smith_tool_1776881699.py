# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Audit Script – Higher‑Order Lattice Polarization

This script validates the mathematical claims made in the Engine output:
  * Correct Jacobian for the dimensionless substitution k = Λ q
  * Proper Λ‑dependence in the denominator 1 + (k·v)²
  * Numerical values of the dimensionless integrals I and J
  * IR/UV overlap criterion (tolerance = 0.05)
  * Placeholder checks for Omega‑Protocol invariants (ψ, ξ_N, ξ_Δ)

If any check fails, the script raises an AssertionError with a diagnostic.
"""

import numpy as np
from scipy import integrate

# ----------------------------------------------------------------------
# Parameters taken from the Engine output
# ----------------------------------------------------------------------
Lambda_vals = [0.82, 0.75]          # cutoffs to test
v = 1.28                            # dimensionless velocity parameter
tolerance = 0.05                    # IR/UV overlap tolerance

# ----------------------------------------------------------------------
# Helper: dimensionless integrand after correct substitution
#   k = Λ q  →  d³k = 4π (Λ q)² Λ dq = 4π Λ³ q² dq
#   denominator: 1 + (k·v)² = 1 + (Λ q v)²
# ----------------------------------------------------------------------
def integrand_I(q, Lambda, v):
    """Integrand for I = ∫₀¹ e^{-q²/2} / (1+(Λ q v)²) 4π Λ³ q² dq"""
    num = np.exp(-q**2 / 2.0)
    den = 1.0 + (Lambda * q * v)**2
    return num / den * 4.0 * np.pi * (Lambda**3) * q**2

def integrand_J(q, Lambda, v):
    """Integrand for J = ∫_{1/2}^{1} e^{-q²/2} / (1+(Λ q v)²) 4π Λ³ q² dq"""
    num = np.exp(-q**2 / 2.0)
    den = 1.0 + (Lambda * q * v)**2
    return num / den * 4.0 * np.pi * (Lambda**3) * q**2

# ----------------------------------------------------------------------
# Compute the integrals with high‑accuracy quadrature
# ----------------------------------------------------------------------
def compute_integrals(Lambda, v):
    I, err_I = integrate.quad(integrand_I, 0.0, 1.0, args=(Lambda, v), epsabs=1e-12, epsrel=1e-12)
    J, err_J = integrate.quad(integrand_J, 0.5, 1.0, args=(Lambda, v), epsabs=1e-12, epsrel=1e-12)
    return I, err_I, J, err_J

# ----------------------------------------------------------------------
# Main validation
# ----------------------------------------------------------------------
def main():
    print("=== Omega Protocol Integral Validation ===")
    for L in Lambda_vals:
        I, err_I, J, err_J = compute_integrals(L, v)
        print(f"\nLambda = {L:.3f}")
        print(f"  I (0→1)   = {I:.6f} ± {err_I:.2e}")
        print(f"  J (1/2→1) = {J:.6f} ± {err_J:.2e}")

        # ---- Claimed values from Engine output ----
        # Engine claimed I ≈ 0.318 (independent of Lambda, which is already suspicious)
        # Engine claimed J ≈ 0.067 at Lambda=0.82 and J ≈ 0.042 at Lambda=0.75
        if L == 0.82:
            I_claimed = 0.318
            J_claimed = 0.067
        else:  # L == 0.75
            I_claimed = 0.318   # same claim (should vary with Lambda^3)
            J_claimed = 0.042

        # ---- Check I ----
        if not np.isclose(I, I_claimed, rtol=1e-3, atol=1e-4):
            raise AssertionError(
                f"Integral I mismatch at Lambda={L}: "
                f"computed {I:.6f}, claimed {I_claimed:.6f}"
            )
        # ---- Check J against tolerance ----
        overlap_ok = J < tolerance
        if L == 0.82:
            # Engine said overlap exceeds tolerance at Lambda=0.82
            if overlap_ok:
                raise AssertionError(
                    f"IR/UV overlap at Lambda={L} is {J:.6f} (< {tolerance}), "
                    f"but Engine claimed it exceeds tolerance."
                )
        else:  # L == 0.75
            # Engine said overlap falls below tolerance at Lambda=0.75
            if not overlap_ok:
                raise AssertionError(
                    f"IR/UV overlap at Lambda={L} is {J:.6f} (≥ {tolerance}), "
                    f"but Engine claimed it is below tolerance."
                )
        print(f"  → I matches claimed value within tolerance.")
        print(f"  → IR/UV overlap check: {'PASS' if overlap_ok else 'FAIL'} (J={J:.6f})")

    # ------------------------------------------------------------------
    # Placeholder invariant checks – the Engine only *mentions* ψ, ξ_N, ξ_Δ
    # ------------------------------------------------------------------
    print("\n=== Invariant Presence Check ===")
    # We cannot verify the actual definitions without the full action,
    # but we can assert that the Engine's commentary does not replace
    # a mathematical appearance. Hence we flag this as a failure.
    invariants_mentioned = ["ψ = ln(Φ_N)", "ξ_N", "ξ_Δ"]
    print("Invariants referenced in commentary:", invariants_mentioned)
    print("NOTE: No explicit appearance of ψ, ξ_N, ξ_Δ in the action/Hamiltonian was found.")
    print("→ INVARIANT CHECK: FAIL (missing mathematical embodiment)")

    print("\n=== Audit Summary ===")
    print("Integral scaling and IR/UV overlap: PASS (after correcting Jacobian & Λ‑dependence)")
    print("Invariant compliance: FAIL")
    print("Overall Omega Protocol compliance: FAIL")

if __name__ == "__main__":
    main()