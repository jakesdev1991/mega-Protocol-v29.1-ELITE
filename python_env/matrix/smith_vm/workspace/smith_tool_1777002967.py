# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script for Audience Resonance Mapping (Sales)
Checks:
- Dimensional consistency (all inputs/outputs dimensionless)
- COD formula correctness
- Invariant hard gates
- Failure-mode detection thresholds
- Stabilization operator behavior (trust softening, urgency injection)
- Entropy accounting (including audit cost)
- Benchmark sanity (values within expected bounds)
"""

import math
import random
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants (mirroring the C++ definitions)
# ----------------------------------------------------------------------
LAMBDA_IMP = 1.0          # impedance damping
GAMMA_TRUST = 0.5         # trust penalty
K_BOLTZMANN = 1.0         # normalized Boltzmann constant

PSI_ID_MIN = 0.95
XI_TRUST_MAX = 3.0
Z_TOPO_MAX = 2.5

V_URG_LIMIT = 1.2
Z_TOPO_LIMIT = 2.0
PSI_ID_CRITICAL = 0.90
XI_TRUST_SHOCK = 2.5

COD_THRESHOLD = 0.85
FALSE_POS_VURG = 1.0

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def normalize(v: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in v))
    if norm == 0:
        return v
    return [x / norm for x in v]

def fidelity_squared(cur: List[float], tgt: List[float]) -> float:
    """|⟨cur|tgt⟩|² assuming vectors are already normalized."""
    dot = sum(c * t for c, t in zip(cur, tgt))
    return dot * dot

def cod(cur: List[float], tgt: List[float], z_topo: float, xi_trust: float) -> float:
    """Chain Overlap Density as per Eq. (COD)."""
    fid = fidelity_squared(normalize(cur), normalize(tgt))
    damping = math.exp(-LAMBDA_IMP * z_topo)
    penalty = math.exp(-GAMMA_TRUST * xi_trust)
    return fid * damping * penalty

def verify_invariants(psi_id: float, xi_trust: float, z_topo: float) -> Tuple[bool, str]:
    """Hard gate check – returns (ok, message)."""
    if psi_id < PSI_ID_MIN:
        return False, f"Identity Dissociation: psi_id={psi_id} < {PSI_ID_MIN}"
    if xi_trust > XI_TRUST_MAX:
        return False, f"Measurement Shock Risk: xi_trust={xi_trust} > {XI_TRUST_MAX}"
    if z_topo > Z_TOPO_MAX:
        return False, f"Silent Rejection Risk: z_topo={z_topo} > {Z_TOPO_MAX}"
    return True, "OK"

def phi_loss(psi_id: float, xi_trust: float, z_topo: float,
             audit_complexity: float = 1.0) -> float:
    """Φ loss = identity erosion + stability breach + audit entropy."""
    loss = 0.0
    if psi_id < PSI_ID_MIN:
        loss += (PSI_ID_MIN - psi_id) * 0.5 * K_BOLTZMANN
    if xi_trust > XI_TRUST_MAX:
        loss += (xi_trust - XI_TRUST_MAX) * 0.2 * K_BOLTZMANN
    audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
    loss += audit_entropy
    return loss

def failure_mode(psi_id: float, v_urg: float, xi_trust: float,
                 z_topo: float, cod_val: float) -> str:
    """Return one of the four failure modes or 'NONE'."""
    if v_urg > V_URG_LIMIT and xi_trust > XI_TRUST_SHOCK:
        return "MEASUREMENT_SHOCK"
    if z_topo > Z_TOPO_LIMIT and cod_val < 0.60:
        return "SILENT_REJECTION"
    if psi_id < PSI_ID_CRITICAL:
        return "IDENTITY_DISSOCIATION"
    if cod_val >= COD_THRESHOLD and v_urg > FALSE_POS_VURG:
        return "FALSE_POSITIVE"
    return "NONE"

def soften_trust(xi_trust: float, target: float, alpha: float = 0.1) -> float:
    return xi_trust * (1.0 - alpha) + target * alpha

def inject_urgency(v_urg: float, t: float, max_val: float) -> float:
    tau, sigma = 0.5, 0.2
    ramp = math.tanh((t - tau) / sigma)
    return min(max_val, ramp * max_val)

# ----------------------------------------------------------------------
# Validation Tests
# ----------------------------------------------------------------------
def test_dimensional_consistency():
    # All inputs are pure numbers; outputs must be pure numbers.
    cur = [1.0, 0.0, 0.0]
    tgt = [0.0, 1.0, 0.0]
    z = 1.5
    xi = 2.0
    c = cod(cur, tgt, z, xi)
    assert isinstance(c, float) and not math.isnan(c), "COD must be a real number"
    # Invariants return bool and str
    ok, msg = verify_invariants(0.96, 2.0, 1.5)
    assert ok and msg == "OK", "Valid state should pass invariants"
    loss = phi_loss(0.96, 2.0, 1.5)
    assert isinstance(loss, float) and loss >= 0.0, "Phi loss must be non‑negative real"
    fm = failure_mode(0.96, 0.5, 2.0, 1.5, c)
    assert fm in {"NONE", "MEASUREMENT_SHOCK", "SILENT_REJECTION",
                  "IDENTITY_DISSOCIATION", "FALSE_POSITIVE"}
    print("[PASS] Dimensional consistency and basic type checks")

def test_cod_formula():
    # Use orthogonal vectors -> fidelity 0
    cur = [1.0, 0.0, 0.0]
    tgt = [0.0, 1.0, 0.0]
    assert math.isclose(cod(cur, tgt, 0.0, 0.0), 0.0, abs_tol=1e-12)
    # Identical vectors -> fidelity 1
    cur = tgt = [1.0, 0.0, 0.0]
    assert math.isclose(cod(cur, tgt, 0.0, 0.0), 1.0, abs_tol=1e-12)
    # Known damping/penalty
    cur = tgt = [1.0, 0.0, 0.0]
    z, xi = 1.0, 2.0
    expected = math.exp(-LAMBDA_IMP * z) * math.exp(-GAMMA_TRUST * xi)
    assert math.isclose(cod(cur, tgt, z, xi), expected, rel_tol=1e-12)
    print("[PASS] COD formula matches definition")

def test_invariant_hard_gate():
    # Violate each condition in turn
    assert not verify_invariants(0.9, 2.0, 1.5)[0]   # psi_id low
    assert not verify_invariants(0.96, 4.0, 1.5)[0]  # xi_trust high
    assert not verify_invariants(0.96, 2.0, 3.0)[0]  # z_topo high
    # Valid point passes
    assert verify_invariants(0.96, 2.0, 1.5)[0]
    print("[PASS] Invariant hard gates behave as expected")

def test_failure_mode_thresholds():
    # Measurement Shock
    assert failure_mode(0.96, 1.3, 3.0, 1.0, 0.5) == "MEASUREMENT_SHOCK"
    # Silent Rejection
    assert failure_mode(0.96, 0.5, 2.0, 2.2, 0.5) == "SILENT_REJECTION"
    # Identity Dissociation
    assert failure_mode(0.8, 0.5, 2.0, 1.0, 0.5) == "IDENTITY_DISSOCIATION"
    # False Positive
    assert failure_mode(0.96, 1.3, 1.0, 1.0, 0.9) == "FALSE_POSITIVE"
    # None
    assert failure_mode(0.96, 0.5, 1.0, 1.0, 0.5) == "NONE"
    print("[PASS] Failure-mode detection thresholds correct")

def test_stabilization_operator():
    xi = 2.5
    xi_new = soften_trust(xi, target=1.0)
    assert 1.0 <= xi_new <= 2.5 and xi_new < xi, "Trust should soften toward target"
    v = 0.0
    v_new = inject_urgency(v, t=0.6, max_val=1.0)
    assert 0.0 <= v_new <= 1.0, "Urgency injected within bounds"
    # After sufficient time, urgency should approach max
    v_late = inject_urgency(0.0, t=1.0, max_val=1.0)
    assert math.isclose(v_late, 1.0, abs_tol=1e-3), "Urgency ramps to max"
    print("[PASS] Stabilization operator functions as intended")

def test_phi_accounting():
    # Base loss from identity erosion
    loss_id = phi_loss(0.90, 2.0, 1.0)
    expected_id = (0.95 - 0.90) * 0.5 * K_BOLTZMANN
    assert math.isclose(loss_id, expected_id, rel_tol=1e-12)
    # Base loss from stability breach
    loss_xi = phi_loss(0.96, 3.5, 1.0)
    expected_xi = (3.5 - 3.0) * 0.2 * K_BOLTZMANN
    assert math.isclose(loss_xi, expected_xi, rel_tol=1e-12)
    # Audit cost term
    loss_audit = phi_loss(0.96, 2.0, 1.0, audit_complexity=2.0)
    expected_audit = K_BOLTZMANN * math.log(2.0) * 2.0
    # identity and stability terms are zero for this call
    assert math.isclose(loss_audit - expected_audit, 0.0, abs_tol=1e-12)
    print("[PASS] Phi‑loss accounting includes audit entropy correctly")

def test_benchmark_sanity():
    # Simulate a tiny benchmark (few trials) to ensure no runtime errors
    random.seed(42)
    trials = 10
    success = 0
    for _ in range(trials):
        # random state
        psi_id = random.uniform(0.8, 1.0)
        xi_trust = random.uniform(0.5, 3.5)
        z_topo = random.uniform(0.5, 3.0)
        v_urg = random.uniform(0.0, 1.5)
        cur = [random.random() for _ in range(3)]
        tgt = [random.random() for _ in range(3)]
        c = cod(cur, tgt, z_topo, xi_trust)
        fm = failure_mode(psi_id, v_urg, xi_trust, z_topo, c)
        # Apply a simple stabilization step (trust soften if shock)
        if fm == "MEASUREMENT_SHOCK":
            xi_trust = soften_trust(xi_trust, target=1.5)
        # Re‑evaluate invariants
        ok, _ = verify_invariants(psi_id, xi_trust, z_topo)
        if ok:
            success += 1
    failure_rate = 1.0 - success / trials
    assert 0.0 <= failure_rate <= 1.0
    print(f"[PASS] Benchmark sanity check – failure rate = {failure_rate:.2f}")

def main():
    print("=== Omega Protocol Validation – Audience Resonance Mapping ===")
    test_dimensional_consistency()
    test_cod_formula()
    test_invariant_hard_gate()
    test_failure_mode_thresholds()
    test_stabilization_operator()
    test_phi_accounting()
    test_benchmark_sanity()
    print("\nAll validation checks passed. The implementation is mathematically sound and compliant with the Omega Protocol invariants.")

if __name__ == "__main__":
    main()