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
----------------------------------
Checks the three core invariants for the Higher-Order Lattice Polarization
derivation:
  1. Shredding boundary: Phi_N^2 + 3*Phi_Delta^2 <= v^2
  2. Poisson recovery: effective mass-squared for Phi_N >= 0
  3. Perturbative validity: each log correction < 0.1 (conservative)

If any invariant is violated, a ProtocolViolation is raised.
"""

import math
import sys

class ProtocolViolation(RuntimeError):
    """Raised when an Omega Protocol invariant is broken."""
    pass

def validate_omega_invariant(
    Phi_N: float,
    Phi_Delta: float,
    v: float,
    alpha0: float,
    g_N: float,
    g_Delta: float,
    Lambda_N: float,
    Lambda_Delta: float,
    q: float,
    lam: float = 1.0,   # lambda from the Mexican‑hat potential (set to 1 for scaling)
) -> None:
    """
    Raise ProtocolViolation if any invariant is violated.
    All quantities are assumed to be positive, dimensionless (or in same units).
    """
    # 1. Shredding boundary (Phi_N^2 + 3 Phi_Delta^2 <= v^2)
    lhs_shred = Phi_N**2 + 3.0 * Phi_Delta**2
    if lhs_shred > v**2 + 1e-12:   # tiny tolerance for FP error
        raise ProtocolViolation(
            f"Shredding boundary violated: Phi_N^2+3*Phi_Delta^2 = {lhs_shred:.6e} > v^2 = {v**2:.6e}"
        )

    # 2. Poisson recovery: effective mass^2 for Phi_N >= 0
    # m_N^2 = lambda * (Phi_N^2 + Phi_Delta^2 - v^2)
    mN2 = lam * (Phi_N**2 + Phi_Delta**2 - v**2)
    if mN2 < -1e-12:
        raise ProtocolViolation(
            f"Poisson recovery broken: effective mass^2 for Phi_N = {mN2:.6e} < 0"
        )

    # 3. Perturbative validity of each logarithmic term
    #   term_N = (alpha0 * g_N^2 / (4*pi)) * ln(Lambda_N^2 / q^2)
    #   term_D = (3*alpha0 * g_Delta^2 / (4*pi)) * ln(Lambda_Delta^2 / q^2)
    #   term_QED = (alpha0/(3*pi)) * ln(Lambda^2 / q^2)   (Lambda taken as UV cutoff)
    # We conservatively require |term| < 0.1
    def log_term(prefactor, Lambda):
        if Lambda <= 0 or q <= 0:
            raise ValueError("Cutoffs and momentum scale must be positive.")
        return prefactor * math.log(Lambda**2 / q**2)

    pref_N = alpha0 * g_N**2 / (4.0 * math.pi)
    pref_D = 3.0 * alpha0 * g_Delta**2 / (4.0 * math.pi)
    pref_QED = alpha0 / (3.0 * math.pi)

    term_N = log_term(pref_N, Lambda_N)
    term_D = log_term(pref_D, Lambda_Delta)
    # For the QED‑like piece we reuse the same UV cutoff as the Archive (conservative)
    term_QED = log_term(pref_QED, max(Lambda_N, Lambda_Delta))

    for name, val in [("Newtonian", term_N), ("Archive", term_D), ("QED", term_QED)]:
        if abs(val) >= 0.1:
            raise ProtocolViolation(
                f"Perturbative validity broken: {name} term = {val:.6e} (>= 0.1)"
            )

    # If we reach here, all invariants hold for the given point.
    return True

# ----------------------------------------------------------------------
# Example usage (feel free to modify parameters to test edge cases)
if __name__ == "__main__":
    # Example parameters that *should* be safe:
    test_params = dict(
        Phi_N=0.5,
        Phi_Delta=0.2,
        v=1.0,
        alpha0=1/137.0,
        g_N=0.02,
        g_Delta=0.01,
        Lambda_N=10.0,
        Lambda_Delta=10.0,
        q=1.0,
        lam=1.0,
    )
    try:
        validate_omega_invariant(**test_params)
        print("✅ All Omega Protocol invariants satisfied.")
    except ProtocolViolation as e:
        print("❌ Protocol violation detected:", e)
        sys.exit(1)