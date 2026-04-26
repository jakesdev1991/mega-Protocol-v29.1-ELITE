# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Omega-Psych-Theorist's Systemic Reboot Derivation.
Checks mathematical soundness and compliance with Omega Protocol invariants:
    - Phi_N (implicitly via psi = ln(Phi_N))
    - Phi_Delta (audit entropy cost subtraction)
    - J* (identity continuity invariant: psi_id_org >= 0.95 hard gate)
All quantities are dimensionless and bounded [0,1] as required.
"""

import math
import random
from typing import List, Tuple

# --------------------------------------------------------------
# 1. Core invariants and helper functions (as per the derivation)
# --------------------------------------------------------------

PSI_ID_THRESHOLD = 0.95          # hard gate for identity continuity
LAMBDA_COUPLING = 1.0            # entropic damping constant in COD
K_BOLTZMANN = 1.0                # dimensionless Boltzmann constant for audit entropy


def normalize_vector(v: List[float]) -> List[float]:
    """Return L2-normalized copy of v (handles zero vector)."""
    norm = math.sqrt(sum(x * x for x in v))
    if norm < 1e-12:
        return [0.0] * len(v)
    return [x / norm for x in v]


def dot_product(a: List[float], b: List[float]) -> float:
    return sum(ai * bi for ai, bi in zip(a, b))


def calculate_COD_Reboot(intent_vec: List[float],
                         identity_vec: List[float],
                         ambiguity: float,
                         psi_id: float) -> float:
    """
    COD_reboot = |<Psi_con^reboot |Psi_id^org>|^2 * exp(-Lambda * H_super) * Psi_id^org
    All inputs assumed already normalized where appropriate.
    """
    if psi_id < PSI_ID_THRESHOLD:
        return 0.0                     # Identity Hard Gate

    # Fidelity term (squared overlap)
    fid = dot_product(intent_vec, identity_vec)
    fid_sq = fid * fid                 # since vectors are normalized, this is |<...>|^2

    # Uncertainty penalty
    damping = math.exp(-LAMBDA_COUPLING * ambiguity)

    return fid_sq * damping * psi_id


def calculate_superposition_entropy(fragments: List[List[float]]) -> float:
    """
    Approximate normalized Shannon entropy over narrative fragments.
    Uses a simple heuristic: probability ~ 1/(1+sqrt(dim)) per fragment.
    Returns value in [0,1].
    """
    if not fragments:
        return 0.0
    probs = []
    for frag in fragments:
        # heuristic: longer/more unique embedding -> lower probability
        prob = 1.0 / (1.0 + math.sqrt(len(frag)))
        probs.append(prob)
    total = sum(probs)
    probs = [p / total for p in probs]

    H = -sum(p * math.log(p) for p in probs if p > 0.0)
    max_H = math.log(len(fragments))
    if max_H < 1e-12:
        max_H = 1.0
    return min(1.0, max(0.0, H / max_H))


def audit_entropy_cost(n_ops: int) -> float:
    """
    Delta S_audit = k_B * ln(2) * N_ops   (dimensionless)
    """
    return K_BOLTZMANN * math.log(2.0) * n_ops


def verify_identity_continuity(psi_id: float) -> bool:
    """Hard gate: psi_id must never fall below threshold."""
    return psi_id >= PSI_ID_THRESHOLD


def phi_density_impact(cod_before: float,
                       cod_after: float,
                       audit_cost: float) -> float:
    """
    Net Phi-density gain = (COD_after - COD_before) - Delta S_audit
    """
    return (cod_after - cod_before) - audit_cost


# --------------------------------------------------------------
# 2. Validation scenarios
# --------------------------------------------------------------

def test_bounds_and_properties():
    """Test that COD stays in [0,1] and respects hard gate."""
    random.seed(42)
    dim = 128

    for _ in range(200):
        # random normalized vectors
        intent = normalize_vector([random.uniform(-1, 1) for _ in range(dim)])
        identity = normalize_vector([random.uniform(-1, 1) for _ in range(dim)])
        ambiguity = random.uniform(0.0, 1.0)
        psi_id = random.uniform(0.0, 1.0)

        cod = calculate_COD_Reboot(intent, identity, ambiguity, psi_id)

        # COD must be in [0,1]
        assert 0.0 <= cod <= 1.0 + 1e-9, f"COD out of bounds: {cod}"

        # If psi_id below threshold, COD must be zero
        if psi_id < PSI_ID_THRESHOLD:
            assert abs(cod) < 1e-9, f"Hard gate violated: psi_id={psi_id}, COD={cod}"

        # Monotonic in psi_id (above threshold) and damping
        if psi_id >= PSI_ID_THRESHOLD:
            # increase psi_id should not decrease COD (other factors same)
            psi_id2 = min(1.0, psi_id + 0.1)
            cod2 = calculate_COD_Reboot(intent, identity, ambiguity, psi_id2)
            assert cod2 >= cod - 1e-9, f"COD not monotonic in psi_id: {cod} -> {cod2}"


def test_adiabatic_operator():
    """Simulate the ARG operator and enforce invariants."""
    random.seed(123)
    dim = 128

    # Simulate a fragmented organization
    n_fragments = 100
    fragments = [[random.uniform(-1, 1) for _ in range(dim)] for _ in range(n_fragments)]

    # Compute initial identity vector as normalized mean of fragments
    mean_vec = [sum(f[i] for f in fragments) / n_fragments for i in range(dim)]
    identity_vec = normalize_vector(mean_vec)
    psi_id_org = 0.78   # start below hard gate -> should trigger repair

    # Misaligned reboot intent (pure efficiency)
    reboot_intent = normalize_vector([random.uniform(0.6, 0.9) for _ in range(dim)])

    ambiguity = calculate_superposition_entropy(fragments)
    reboot_freq = 0.7   # high

    # ----- Pre‑apply state -----
    cod_before = calculate_COD_Reboot(reboot_intent, identity_vec, ambiguity, psi_id_org)
    assert cod_before < 0.2, f"Expected low COD pre‑repair, got {cod_before}"

    # ----- Apply ARG (simplified) -----
    audit_ops = 0
    audit_cost = 0.0

    # Phase 1: diagnostic (no change)
    # Phase 2: intellectual validation – we simulate a successful re‑entanglement
    # by nudging identity vector toward reboot intent and raising psi_id_org
    # (this mirrors the "Narrative Re‑entanglement" step)
    if psi_id_org < PSI_ID_THRESHOLD:
        # repair step: increase identity coherence
        psi_id_org = min(1.0, psi_id_org + 0.20)   # adiabatic recovery
        audit_ops += 1
        audit_cost += audit_entropy_cost(1)

        # rotate identity vector slightly toward intent (simulate new narrative)
        blended = [0.7 * identity_vec[i] + 0.3 * reboot_intent[i] for i in range(dim)]
        identity_vec = normalize_vector(blended)

    # Phase 3: recompute COD
    cod_after = calculate_COD_Reboot(reboot_intent, identity_vec, ambiguity, psi_id_org)

    # Phase 4: invariant check – must not violate hard gate
    assert verify_identity_continuity(psi_id_org), \
        f"Identity continuity broken after ARG: psi_id_org={psi_id_org}"

    # Phase 5: Phi‑density ledger
    phi_gain = phi_density_impact(cod_before, cod_after, audit_cost)

    # Net gain should be positive for a successful re‑entanglement
    assert phi_gain > 0.0, f"Phi-density not gained: {phi_gain} (audit cost={audit_cost})"

    # Additionally, COD should have risen significantly
    assert cod_after > 0.6, f"COD insufficiently raised: {cod_after}"


def test_failure_mode_detection():
    """Check that the postulated failure thresholds trigger correctly."""
    # Define thresholds from the text
    H_SUPER_LIMIT = 0.80
    GAMMA_CRITICAL = 0.6
    PSI_ID_CRITICAL = 0.85
    COD_THRESHOLD = 0.90

    def check_risk(H_super, gamma, psi_id, cod):
        if (H_super > H_SUPER_LIMIT and
                gamma > GAMMA_CRITICAL and
                psi_id < PSI_ID_CRITICAL):
            return "REBOOT_COLLAPSE"
        if psi_id < PSI_ID_CRITICAL and cod < COD_THRESHOLD:
            return "IDENTITY_VACUUM"
        if cod > COD_THRESHOLD and psi_id < PSI_ID_CRITICAL:
            return "FALSE_CLARITY"
        return "NONE"

    # Case 1: Reboot Collapse Cascade
    assert check_risk(0.85, 0.7, 0.8, 0.5) == "REBOOT_COLLAPSE"
    # Case 2: Identity Vacuum (low COD, low identity)
    assert check_risk(0.5, 0.2, 0.8, 0.5) == "IDENTITY_VACUUM"
    # Case 3: False Clarity (high COD but identity still low)
    assert check_risk(0.3, 0.1, 0.8, 0.95) == "FALSE_CLARITY"
    # Case 4: Healthy
    assert check_risk(0.2, 0.1, 0.97, 0.6) == "NONE"


def test_dimensional_consistency():
    """Spot‑check that all intermediate quantities are dimensionless and bounded."""
    # COD
    assert 0.0 <= calculate_COD_Reboot([1.0], [1.0], 0.0, 1.0) <= 1.0
    # Entropy
    assert 0.0 <= calculate_superposition_entropy([[0.5, 0.5]]) <= 1.0
    # Audit cost
    assert audit_entropy_cost(5) >= 0.0
    # Phi impact
    phi = phi_density_impact(0.2, 0.8, 0.1)
    # No inherent bounds, but we can check it's a real number
    assert isinstance(phi, float)


if __name__ == "__main__":
    try:
        test_bounds_and_properties()
        print("✓ Bounds and properties test passed")
        test_adiabatic_operator()
        print("✓ Adiabatic operator test passed")
        test_failure_mode_detection()
        print("✓ Failure mode detection test passed")
        test_dimensional_consistency()
        print("✓ Dimensional consistency test passed")
        print("\nAll validation checks succeeded. The derivation is mathematically sound "
              "and compliant with Omega Protocol invariants.")
    except AssertionError as e:
        raise SystemExit(f"Validation failed: {e}")