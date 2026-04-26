# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Higher‑Order Lattice Polarization
-----------------------------------------------------------------------
Checks the core invariants that must hold for a stable derivation:
    1. Metric positivity:          g_zz = 1 + Phi_Delta > 0
    2. Entropy‑freeze safety:      S_pair = S0 + Phi_Delta * S1 >= 0
    3. Symplectic invariant:       Phi_N * (1 + Phi_Delta) ≈ C (constant)
    4. Real polarization tensors:  Im(Pi_L) = Im(Pi_M) = 0
    5. Effective coupling denominator non‑zero:
          D = 1 + Pi_T + Phi_Delta*(Pi_L + 2*Pi_M)  ≠ 0
    6. Faddeev‑Popov determinant finite (same as metric positivity).

If any check fails, the function returns False and logs the offending invariant.
"""

import math
from typing import Tuple, NamedTuple, Optional

class Polarization(NamedTuple):
    Pi_L: complex
    Pi_M: complex
    Pi_T: float   # assumed real in the truncation

class State(NamedTuple):
    Phi_N: float
    Phi_Delta: float
    S0: float
    S1: float
    pol: Polarization
    e: float          # coupling constant (for reference)
    C: float          # symplectic constant (expected value of Phi_N*(1+Phi_Delta))

TOL = 1e-12   # tolerance for equality checks
EPS = 1e-15   # small epsilon to avoid division by zero in logs

def validate_invariants(state: State) -> Tuple[bool, Optional[str]]:
    """
    Returns (is_valid, reason_if_invalid).
    """
    Phi_N, Phi_Delta, S0, S1, pol, e, C = state

    # 1. Metric positivity (g_zz > 0)
    g_zz = 1.0 + Phi_Delta
    if g_zz <= 0.0:
        return False, f"Metric collapse: g_zz = {g_zz} ≤ 0 (Phi_Delta = {Phi_Delta})"

    # 2. Entropy‑freeze safety (S_pair ≥ 0)
    S_pair = S0 + Phi_Delta * S1
    if S_pair < -TOL:
        return False, f"Entropy freeze violated: S_pair = {S_pair} < 0"

    # 3. Symplectic invariant: Phi_N * (1+Phi_Delta) ≈ C
    symplectic = Phi_N * g_zz
    if abs(symplectic - C) > TOL * max(1.0, abs(C)):
        return False, (
            f"Symplectic invariant broken: Phi_N*(1+Phi_Delta) = {symplectic}, "
            f"expected C = {C} (diff = {abs(symplectic-C)})"
        )

    # 4. Real polarization tensors
    if abs(pol.Pi_L.imag) > TOL:
        return False, f"Imaginary part in Pi_L: {pol.Pi_L.imag}"
    if abs(pol.Pi_M.imag) > TOL:
        return False, f"Imaginary part in Pi_M: {pol.Pi_M.imag}"

    # 5. Effective coupling denominator non‑zero
    #   D = 1 + Pi_T + Phi_Delta*(Pi_L + 2*Pi_M)
    #   Note: Pi_L, Pi_M are complex; we already forced imag≈0, so take real part.
    Pi_L_real = pol.Pi_L.real
    Pi_M_real = pol.Pi_M.real
    D = 1.0 + pol.Pi_T + Phi_Delta * (Pi_L_real + 2.0 * Pi_M_real)
    if abs(D) < EPS:
        return False, f"Effective coupling denominator near zero: D = {D}"

    # 6. Faddeev‑Popov determinant finiteness (same as metric positivity)
    #   Δ_FP ∝ (1+Phi_Delta)^(-1/2) → requires g_zz > 0
    # Already checked in step 1.

    # All invariants satisfied
    return True, None

# ----------------------------------------------------------------------
# Example usage (replace with actual runtime values from the Omega node):
if __name__ == "__main__":
    # Mock state that should PASS
    example_state = State(
        Phi_N=0.5,
        Phi_Delta=-0.2,          # g_zz = 0.8 > 0
        S0=1.0,
        S1=-0.5,                 # S_pair = 1.0 + (-0.2)*(-0.5) = 1.1 > 0
        pol=Polarization(Pi_L=0.01+0j, Pi_M=-0.003+0j, Pi_T=0.02),
        e=0.302822,              # approximate QED coupling
        C=0.5 * (1.0 - 0.2)      # expected symplectic constant
    )

    valid, reason = validate_invariants(example_state)
    if valid:
        print("✅ PASS: All Omega Protocol invariants satisfied.")
    else:
        print(f"❌ FAIL: {reason}")

    # ------------------------------------------------------------------
    # Demonstrate a failing case (metric collapse)
    failing_state = example_state._replace(Phi_Delta=-1.0)  # g_zz = 0
    valid, reason = validate_invariants(failing_state)
    if not valid:
        print(f"\n🔴 Expected failure: {reason}")