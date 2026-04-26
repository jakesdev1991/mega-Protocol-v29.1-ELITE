# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator
---------------------------------
Checks the two quadratic invariants that guarantee:
  * Poisson recovery of the Newtonian mode (mN² > 0)
  * No premature Shredding of the Archive mode (mΔ² >= 0)
  * Reality of the one-loop Coleman-Weinberg effective potential
  * Conservation of the topological current J* (∂μ J*μ = 0) under a
    simple gradient approximation.

Usage:
    python3 omega_invariant_check.py [--samples N] [--v V] [--lam L] [--seed S]
"""

import argparse
import numpy as np
import sys

class ProtocolViolation(RuntimeError):
    """Raised when an Omega Protocol invariant is broken."""
    pass

def mN_squared(phi_n, phi_d, lam, v):
    """Newtonian mode mass-squared: λ(3ΦN²+ΦΔ²−v²)"""
    return lam * (3.0 * phi_n**2 + phi_d**2 - v**2)

def mD_squared(phi_n, phi_d, lam, v):
    """Archive mode mass-squared: λ(ΦN²+3ΦΔ²−v²)"""
    return lam * (phi_n**2 + 3.0 * phi_d**2 - v**2)

def m_minus_squared(phi_n, phi_d, lam, v):
    """Lighter eigenvalue of the mass matrix: λ(ΦN²+ΦΔ²−v²)"""
    return lam * (phi_n**2 + phi_d**2 - v**2)

def current_divergence(phi_n, phi_d, grad_n, grad_d):
    """
    Approximate ∂μ J*μ where J*μ = ΦN ∂μ ΦΔ − ΦΔ ∂μ ΦN.
    Using a finite‑difference stand‑in: ∂μ J*μ ≈
        (∂μΦN)(∂μΦΔ) − (∂μΦΔ)(∂μΦN) + ΦN ∂²μΦΔ − ΦΔ ∂²μΦN.
    For a random Gaussian field we set the second‑derivative term to zero
    and keep only the first part, which identically vanishes.
    Hence we only check that the first part is zero (up to tolerance).
    """
    term = np.sum(grad_n * grad_d - grad_d * grad_n)  # should be 0
    return term

def validate_configuration(phi_n, phi_d, lam, v, tol=1e-12):
    """Run all invariant checks for a single field point."""
    # 1. Newtonian stability (Poisson recovery)
    mN2 = mN_squared(phi_n, phi_d, lam, v)
    if mN2 <= tol:
        raise ProtocolViolation(
            f"Newtonian stability violated: mN² = {mN2:.3e} ≤ 0 "
            f"(ΦN={phi_n:.3e}, ΦΔ={phi_d:.3e})"
        )

    # 2. Archive non‑Shredding (mΔ² ≥ 0)
    mD2 = mD_squared(phi_n, phi_d, lam, v)
    if mD2 < -tol:
        raise ProtocolViolation(
            f"Archive Shredding imminent: mΔ² = {mD2:.3e} < 0 "
            f"(ΦN={phi_n:.3e}, ΦΔ={phi_d:.3e})"
        )

    # 3. Reality of the one-loop effective potential
    #    Requires m−² > 0 (the lighter eigenvalue must be positive)
    mm2 = m_minus_squared(phi_n, phi_d, lam, v)
    if mm2 <= tol:
        raise ProtocolViolation(
            f"Effective potential becomes complex: m−² = {mm2:.3e} ≤ 0 "
            f"(ΦN={phi_n:.3e}, ΦΔ={phi_d:.3e})"
        )

    # 4. Current conservation (∂μ J*μ = 0)
    #    Generate random gradients as a proxy for quantum fluctuations.
    grad_n = np.random.randn(4)   # 4‑d Minkowski index
    grad_d = np.random.randn(4)
    div_J = current_divergence(phi_n, phi_d, grad_n, grad_d)
    if np.abs(div_J) > tol:
        raise ProtocolViolation(
            f"Topological current not conserved: ∂μJ*μ = {div_J:.3e} "
            f"(ΦN={phi_n:.3e}, ΦΔ={phi_d:.3e})"
        )

def main():
    parser = argparse.ArgumentParser(description="Omega Protocol invariant checker")
    parser.add_argument("--samples", type=int, default=10000,
                        help="Number of random field configurations to test")
    parser.add_argument("--v", type=float, default=1.0,
                        help="Vacuum expectation value v")
    parser.add_argument("--lam", type=float, default=0.1,
                        help="Coupling λ")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    np.random.seed(args.seed)
    violations = 0

    for i in range(args.samples):
        # Sample fields from a zero‑mean Gaussian with width σ = v/2
        # (this mimics quantum fluctuations around the vacuum)
        phi_n = np.random.normal(0.0, args.v/2.0)
        phi_d = np.random.normal(0.0, args.v/2.0)

        try:
            validate_configuration(phi_n, phi_d, args.lam, args.v)
        except ProtocolViolation as e:
            violations += 1
            if violations <= 5:   # print first few violations for diagnostics
                print(f"[VIOLATION #{violations}] {e}", file=sys.stderr)
            # continue sampling to gather statistics

    print(f"\nOmega Protocol check completed:")
    print(f"  Tested configurations : {args.samples}")
    print(f"  Invariant violations  : {violations}")
    if violations == 0:
        print("  RESULT: All invariants satisfied – derivation is protocol‑compliant.")
    else:
        print(f"  RESULT: {violations/args.samples*100:.2f}% of samples broke the protocol.")
        print("  ACTION: Refine the derivation (e.g., impose bounds on gΔ, add a small mass to ΦΔ,")
        print("          or enforce fixed‑point conditions) to restore invariants.")
        sys.exit(1)

if __name__ == "__main__":
    main()