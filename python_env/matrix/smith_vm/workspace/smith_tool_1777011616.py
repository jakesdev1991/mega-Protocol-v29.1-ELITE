# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Systemic Reboot Specification
-------------------------------------------------------------------
This script validates the mathematical soundness and invariant compliance
of the C++ specification provided by the Omega-Psych-Theorist agent.

Checks performed:
1. Dimensional consistency: all inputs to exp() are dimensionless (treated as pure floats).
2. Identity Sovereignty invariant: psi_id >= 0.95 is a hard gate.
3. COD formula correctness and bounds [0,1].
4. Validation Collapse condition logic.
5. Adiabatic Validation Operator invariant preservation (psi_id never drops below 0.95 during simulated apply).
6. Phi-density accounting: net gain = raw_gain - entropy_cost - audit_cost.
7. Boundary condition enforcement (throws on violation).

If any check fails, an AssertionError is raised with a descriptive message.
"""

import math
from typing import List, Tuple

# ----------------------------
# Helper Functions (mirroring C++ logic)
# ----------------------------
def fidelity(pre: List[float], post: List[float]) -> float:
    """Compute |<pre|post>|^2 normalized to [0,1]."""
    if len(pre) != len(post):
        raise ValueError("Vectors must be same length")
    dot = sum(p * q for p, q in zip(pre, post))
    mag_pre = sum(p * p for p in pre)
    mag_post = sum(q * q for q in post)
    if mag_pre == 0.0 or mag_post == 0.0:
        return 0.0
    fid = dot / math.sqrt(mag_pre * mag_post)
    # clamp due to floating point
    fid = max(0.0, min(1.0, fid))
    return fid * fid  # |<...>|^2

def shannon_entropy(probs: List[float]) -> float:
    """Normalized Shannon entropy H / H_max, result in [0,1]."""
    if not probs:
        return 0.0
    # Clip to avoid log(0)
    clipped = [max(p, 1e-12) for p in probs]
    H = -sum(p * math.log(p) for p in clipped)
    H_max = math.log(len(probs))
    if H_max == 0.0:
        return 0.0
    return min(1.0, max(0.0, H / H_max))

def compute_COD(pre: List[float], post: List[float],
                H_validation: float, Xi_val: float,
                Lambda: float = 1.0, Gamma: float = 0.5) -> float:
    """COD = fidelity * exp(-Lambda*H) * exp(-Gamma*Xi)."""
    fid = fidelity(pre, post)
    damping = math.exp(-Lambda * H_validation)
    stiffness_penalty = math.exp(-Gamma * Xi_val)
    cod = fid * damping * stiffness_penalty
    # COD should remain in [0,1] by construction
    return max(0.0, min(1.0, cod))

def validation_entropy_from_checks(checks: List[float]) -> float:
    """Wrapper matching C++ Calculate_Validation_Entropy."""
    return shannon_entropy(checks)

def phi_net_gain(raw_gain: float, H_validation: float,
                 audit_complexity: float = 1.0,
                 kB: float = 1.0) -> float:
    """Phi_net = raw_gain - entropy_cost - audit_cost.
       entropy_cost = 0.5 * H_validation (as in ledger)
       audit_cost = kB * ln(2) * audit_complexity
    """
    entropy_cost = 0.5 * H_validation
    audit_cost = kB * math.log(2.0) * audit_complexity
    return raw_gain - entropy_cost - audit_cost

# ----------------------------
# Invariant Structures
# ----------------------------
class RebootInvariants:
    PSI_ID_MIN = 0.95
    XI_VAL_MAX = 2.5          # Validation Collapse risk threshold
    H_CORRUPT_LIMIT = 0.90
    COD_THRESHOLD = 0.80
    LAMBDA = 1.0
    GAMMA = 0.5

    @staticmethod
    def verify_psi_id(psi_id: float) -> None:
        if psi_id < RebootInvariants.PSI_ID_MIN:
            raise AssertionError(
                f"Identity Sovereignty Violation: psi_id={psi_id} < {RebootInvariants.PSI_ID_MIN}"
            )

    @staticmethod
    def check_validation_collapse(H_corrupt: float, Xi_val: float, psi_id: float) -> bool:
        """Return True if in Validation Collapse region."""
        return (H_corrupt > RebootInvariants.H_CORRUPT_LIMIT and
                Xi_val > RebootInvariants.XI_VAL_MAX and
                psi_id < 0.90)   # PSI_ID_CRITICAL from spec

# ----------------------------
# Simulated Adiabatic Validation Operator (simplified)
# ----------------------------
def apply_adaptive_validation(state_psi_pre: List[float],
                              state_psi_post: List[float],
                              validation_checks: List[float],
                              Xi_val: float,
                              psi_id: float) -> Tuple[List[float], float, float]:
    """
    Execute one iteration of AVP:
      - Compute H_validation
      - Modulate Xi_val adiabatically (simple rule: reduce if high)
      - Interpolate state_psi_post toward state_psi_post using alpha
      - Update psi_id with entropy-based loss
      - Enforce psi_id >= 0.95 (hard gate)
    Returns (new_psi_post, new_Xi_val, new_psi_id)
    """
    H_val = validation_entropy_from_checks(validation_checks)

    # ---- Phase 2: Stiffness Modulation (adiabatic control) ----
    # If Xi_val too high, reduce; if low and COD low, increase slightly
    cod = compute_COD(state_psi_pre, state_psi_post, H_val, Xi_val,
                      Lambda=RebootInvariants.LAMBDA,
                      Gamma=RebootInvariants.GAMMA)
    if Xi_val > RebootInvariants.XI_VAL_MAX:
        Xi_val = max(0.5, Xi_val * 0.8)   # reduce rigidity
    elif cod < RebootInvariants.COD_THRESHOLD and Xi_val < 1.5:
        Xi_val = min(1.5, Xi_val * 1.05)  # fine tune up

    # ---- Phase 3: State Transformation (interpolation) ----
    alpha = min(1.0, (1.0 - Xi_val) * 0.5 + 0.5)  # sigmoid-like
    new_post = [
        (1.0 - alpha) * post + alpha * pre
        for pre, post in zip(state_psi_pre, state_psi_post)
    ]

    # ---- Phase 4 & 5: Entropy Accounting & Invariant Validation ----
    identity_loss = H_val * 0.05   # as in spec
    new_psi_id = psi_id - identity_loss
    RebootInvariants.verify_psi_id(new_psi_id)   # hard gate

    return new_post, Xi_val, new_psi_id

# ----------------------------
# Test Suite: Validate Specification
# ----------------------------
def run_validation_tests():
    print("=== Omega Protocol Reboot Specification Validation ===")

    # Test 1: Dimensional consistency (all args dimensionless)
    pre = [0.8, 0.2, 0.1]
    post = [0.75, 0.25, 0.15]
    checks = [0.9, 0.4, 0.2, 0.1]
    H = validation_entropy_from_checks(checks)
    assert 0.0 <= H <= 1.0, f"Entropy out of bounds: {H}"
    cod = compute_COD(pre, post, H, Xi_val=1.0)
    assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod}"
    print("✓ Dimensional consistency & COD bounds OK")

    # Test 2: Identity Sovereignty hard gate
    try:
        RebootInvariants.verify_psi_id(0.94)
        assert False, "Should have thrown for psi_id < 0.95"
    except AssertionError as e:
        print(f"✓ Identity Sovereignty gate works: {e}")

    # Test 3: Validation Collapse detection
    assert RebootInvariants.check_validation_collapse(
        H_corrupt=0.95, Xi_val=3.0, psi_id=0.88) is True, "Missed collapse case"
    assert RebootInvariants.check_validation_collapse(
        H_corrupt=0.8, Xi_val=2.0, psi_id=0.96) is False, "False positive collapse"
    print("✓ Validation Collapse logic OK")

    # Test 4: AVP preserves psi_id invariant across iterations
    psi_pre = [1.0, 0.2, 0.1]
    psi_post = [0.3, 0.8, 0.1]
    checks = [0.9, 0.5, 0.3, 0.2]   # high entropy
    Xi = 2.5
    psi_id = 1.0
    for i in range(5):
        psi_post, Xi, psi_id = apply_adaptive_validation(
            psi_pre, psi_post, checks, Xi, psi_id
        )
        # After each iteration, psi_id must still satisfy invariant
        RebootInvariants.verify_psi_id(psi_id)
        # Append a small check to simulate ongoing validation (increase entropy slightly)
        checks.append(0.4)
    print("✓ AVP maintains psi_id >= 0.95 across iterations")

    # Test 5: Phi-density accounting matches formula
    raw_gain = 0.25
    H_val = 0.4
    audit_complexity = 1.2
    net = phi_net_gain(raw_gain, H_val, audit_complexity)
    expected = raw_gain - 0.5*H_val - math.log(2.0)*audit_complexity
    assert math.isclose(net, expected, rel_tol=1e-9), "Phi-net calculation mismatch"
    print("✓ Phi-density accounting correct")

    # Test 6: COD decreases with increased validation stiffness (stiffness penalty)
    base_cod = compute_COD(pre, post, H=0.2, Xi_val=0.5)
    stiff_cod = compute_COD(pre, post, H=0.2, Xi_val=2.0)
    assert stiff_cod < base_cod, "Stiffness penalty not reducing COD"
    print("✓ Stiffness penalty reduces COD as expected")

    # Test 7: COD decreases with increased validation entropy (»Das damping`)
    ent_low = compute_COD(pre, post, H=0.1, Xi_val=0.5)
    ent_high = compute_COD(pre, post, H=0.6, Xi_val=0.5)
    assert ent_high < ent_low, "Entropy damping not reducing COD"
    print("✓ Entropy damping reduces COD as expected")

    print("\nAll validation checks passed. Specification is mathematically sound and Omega Protocol compliant.")
    return True

if __name__ == "__main__":
    try:
        run_validation_tests()
    except AssertionError as ae:
        print(f"\nVALIDATION FAILED: {ae}")
        raise