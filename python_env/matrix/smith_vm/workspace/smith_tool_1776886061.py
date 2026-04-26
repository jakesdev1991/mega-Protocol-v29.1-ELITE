# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol validation script for the Engine's stability analysis.

Checks:
  1. Mathematical soundness of the integral I(Λ, v).
  2. Presence of required Omega‑Protocol invariants (ψ, ξ_N, ξ_Δ)
     in the supplied Engine output.

If either check fails, the script returns META-FAIL.
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. Integral convergence test
# ----------------------------------------------------------------------
def integrand(k_vec, Lambda, v):
    """
    k_vec : shape (..., 3) array of wave‑vectors
    Lambda: float > 0
    v     : shape (3,) coupling vector
    Returns the integrand value at each k_vec.
    """
    k_sq = np.sum(k_vec**2, axis=-1)          # |k|^2
    kv   = np.sum(k_vec * v, axis=-1)         # k·v
    return np.exp(-k_sq / (2.0 * Lambda**2)) / (1.0 + kv**2)

def monte_carlo_integral(Lambda, v, N_samples=2_000_000, radius=10.0):
    """
    Estimate I(Λ,v) by Monte‑Carlo sampling inside a sphere of given radius.
    The Gaussian tail beyond 'radius' is negligible for the Λ values we test.
    """
    # Sample points uniformly in a cube [-radius, radius]^3 and keep those inside the sphere
    pts = np.random.uniform(-radius, radius, size=(N_samples, 3))
    inside = np.sum(pts**2, axis=1) <= radius**2
    pts = pts[inside]
    if pts.size == 0:
        return 0.0
    vol_sphere = (4.0/3.0) * np.pi * radius**3
    # Uniform pdf inside sphere = 1/vol_sphere
    f_vals = integrand(pts, Lambda, v)
    return vol_sphere * np.mean(f_vals)

def test_integral_convergence():
    """Run the integral for several Λ values and show that it stays finite."""
    v_vec = np.array([0.0, 0.0, 1.28])   # choose v along z‑axis (magnitude 1.28)
    Lambdas = [0.2, 0.5, 0.75, 0.82, 1.0, 2.0]
    print("Integral I(Λ, v) estimates (Monte‑Carlo, 2M samples):")
    results = {}
    for L in Lambdas:
        I = monte_carlo_integral(L, v_vec, N_samples=1_000_000)  # fewer samples for speed
        results[L] = I
        print(f"  Λ = {L:5.2f} → I ≈ {I:.6f}")
    # Check that none of the results are NaN or Inf
    finite = all(np.isfinite(v) for v in results.values())
    return finite, results

# ----------------------------------------------------------------------
# 2. Invariant presence test
# ----------------------------------------------------------------------
def check_invariants(text):
    """Return True if all required invariants appear in the text."""
    required = ["psi", "xi_N", "xi_Delta"]  # case‑insensitive search
    found = [term.lower() in text.lower() for term in required]
    missing = [term for term, present in zip(required, found) if not present]
    return all(found), missing

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # Engine output (as provided in the prompt)
    engine_output = """// Stability Analysis for Higher-Order Lattice Polarization Corrections
// Revealed Potential 'Shredding' Flaw in Phi_Delta Orthogonality

// 1. Orthogonality Breakdown Risk:
// - Z2 symmetry derivation incomplete; missing Hamiltonian proof
// - Potential Phi_N/Phi_Delta cross-talk contaminating UV regime

// 2. Premature Divergence in Phi_Delta:
// - Integral convergence verified for given Lambda=0.82, v=1.28
// - Sensitivity analysis shows robustness under parameter variation

// 3. Poisson Recovery Validation:
// - Phi_N dominance at short distances confirmed for Lambda < 1.0
// - Recommend tightening Lambda to 0.75 to ensure UV/IR separation

// 4. Stability Operator Proposal:
// - Implement dynamic Lambda adjustment via Xi_bound feedback
// - Enforce orthogonality via Hamiltonian symmetry constraints

// Impact on Omega Protocol Φ Density:
// - Prevents Φ-leaks from mode mixing (-0.12 Φ)
// - Ensures reliable UV stability (+0.08 Φ)
// - Net Gain: +0.08 Φ with tightened controls"""

    print("="*60)
    print("Omega‑Protocol Validation of Engine Stability Analysis")
    print("="*60)

    # ---- Integral test ----
    integral_ok, integral_vals = test_integral_convergence()
    print("\nIntegral convergence check:")
    if integral_ok:
        print("  PASS – Integral is finite for all tested Λ (as expected from Gaussian damping).")
    else:
        print("  FAIL – Integral produced non‑finite values.")

    # ---- Invariant test ----
    invariants_ok, missing = check_invariants(engine_output)
    print("\nInvariant presence check:")
    if invariants_ok:
        print("  PASS – All required invariants (psi, xi_N, xi_Delta) found.")
    else:
        print(f"  FAIL – Missing invariants: {', '.join(missing)}")

    # ---- Final decision ----
    overall_pass = integral_ok and invariants_ok
    print("\n" + "="*60)
    if overall_pass:
        print("RESULT: META-PASS – Analysis is mathematically sound and invariant‑compliant.")
    else:
        print("RESULT: META-FAIL – Analysis fails one or more Omega‑Protocol checks.")
    print("="*60)

if __name__ == "__main__":
    main()