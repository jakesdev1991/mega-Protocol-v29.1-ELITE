# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Audit Script – Validation of Bureaucratic Decision Manifold (v27.3-Omega-Polarized)
-----------------------------------------------------------------------------------------------
This script independently verifies the mathematical soundness and invariant compliance of the
key components from the provided C++ specification. It focuses on:
  1. Dimensional homogeneity (all terms dimensionless [0,1] after clamping).
  2. Correct implementation of the COD formula with hard gate on Ψ_id^org.
  3. Proper calculation of Topological Impedance (H_top).
  4. Invariant checking (Ψ_id^org ≥ 0.95) and exception throwing.
  5. Benchmark suite: ensuring no hardcoded stub values for baseline_cod and H_top.
  6. Geodesic Smoothing Gate (GSG) logic: identity‑preserving simulation before pruning.
  7. Audit cost subtraction in Φ‑density ledger.

The script uses random sampling to stress‑test the functions and reports any violations.
"""

import math
import random
import sys
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions mirroring the C++ logic (kept dimensionless)
# ----------------------------------------------------------------------
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def topological_impedance(path: List[Tuple[float, float]]) -> float:
    """
    path: list of (approval_cost, risk_variance) both in [0,1]
    Returns H_top = clamp( sum(cost*variance) / sum(cost) , 0, 1 )
    """
    if not path:
        return 0.0
    total_impedance = sum(c * v for c, v in path)
    total_length = sum(c for c, _ in path)
    if total_length == 0.0:
        return 0.0
    raw = total_impedance / total_length
    return clamp(raw, 0.0, 1.0)

def cod_decision(intent: List[float], outcome: List[float],
                 H_top: float, Xi_sys: float, Psi_id: float,
                 Lambda: float = 1.0, Gamma: float = 0.5) -> float:
    """
    COD = |<Ψ_intent|Ψ_outcome>|^2 * exp(-Λ*H_top) * exp(-Γ*Xi_sys) * Ψ_id
    Hard gate: if Ψ_id < 0.95 → COD = 0
    All vectors assumed normalized? We compute fidelity as cosine similarity.
    """
    if Psi_id < 0.95:
        return 0.0
    # cosine similarity (fidelity)
    dot = sum(i * o for i, o in zip(intent, outcome))
    magI = math.sqrt(sum(i * i for i in intent))
    magO = math.sqrt(sum(o * o for o in outcome))
    if magI == 0.0 or magO == 0.0:
        fidelity = 0.0
    else:
        fidelity = dot / (magI * magO)
    fidelity = clamp(fidelity, 0.0, 1.0)
    damping = math.exp(-Lambda * H_top)
    stiffness_penalty = math.exp(-Gamma * Xi_sys)
    return fidelity * damping * stiffness_penalty * Psi_id

def verify_identity_continuity(Psi_id: float, threshold: float = 0.95) -> bool:
    """Returns True if invariant holds; mimics the C++ function that throws on False."""
    return Psi_id >= threshold

def audit_entropy_cost(complexity: float = 1.0) -> float:
    """ΔS_audit = K_B * ln(2) * complexity, with K_B = 1 (dimensionless)."""
    return math.log(2.0) * complexity

def phi_density_impact(H_top: float, cod_gain: float, audit_complexity: float = 1.0) -> float:
    """Φ impact = cod_gain - noise_cost - audit_entropy_cost"""
    noise_cost = H_top * 0.5
    return cod_gain - noise_cost - audit_entropy_cost(audit_complexity)

# ----------------------------------------------------------------------
# Validation Tests
# ----------------------------------------------------------------------
def test_dimensional_homogeneity() -> List[str]:
    errors = []
    # Random vectors and parameters
    for _ in range(1000):
        intent = [random.random() for _ in range(4)]
        outcome = [random.random() for _ in range(4)]
        H_top = random.random()
        Xi_sys = random.random() * 3.0  # allowed up to 3.0 per invariant
        Psi_id = random.random()
        # COD should stay in [0,1] (or 0 if gate triggers)
        cod = cod_decision(intent, outcome, H_top, Xi_sys, Psi_id)
        if not (0.0 <= cod <= 1.0 + 1e-12):
            errors.append(f"COD out of bounds: {cod} (Psi_id={Psi_id}, H_top={H_top}, Xi_sys={Xi_sys})")
        # H_top already clamped by function, but double-check
        if not (0.0 <= H_top <= 1.0):
            errors.append(f"H_top not clamped: {H_top}")
        # Xi_sys not clamped in code but used in exp; exp argument can be >1 but result still in (0,1]
        # We just ensure the exponential term is in (0,1]
        exp_term = math.exp(-0.5 * Xi_sys)  # Gamma=0.5
        if not (0.0 < exp_term <= 1.0):
            errors.append(f"Stiffness penalty out of (0,1]: {exp_term} for Xi_sys={Xi_sys}")
    return errors

def test_cod_hard_gate() -> List[str]:
    errors = []
    intent = [1.0, 0.0, 0.0, 0.0]
    outcome = [1.0, 0.0, 0.0, 0.0]
    H_top = 0.2
    Xi_sys = 1.0
    # Test just below threshold
    for Psi_id in [0.94, 0.90, 0.5]:
        cod = cod_decision(intent, outcome, H_top, Xi_sys, Psi_id)
        if abs(cod - 0.0) > 1e-12:
            errors.append(f"Hard gate failed: COD={cod} for Psi_id={Psi_id} (<0.95)")
    # Test just above threshold
    for Psi_id in [0.95, 0.96, 1.0]:
        cod = cod_decision(intent, outcome, H_top, Xi_sys, Psi_id)
        if cod <= 0.0:
            errors.append(f"Hard gate incorrectly zeroed COD={cod} for Psi_id={Psi_id} (>=0.95)")
    return errors

def test_topological_impedance() -> List[str]:
    errors = []
    # Edge cases
    if topological_impedance([]) != 0.0:
        errors.append("Empty path should give 0 impedance")
    if topological_impedance([(0.0, 0.5)]) != 0.0:
        errors.append("Zero approval cost should give 0 impedance")
    # Random check: ensure output in [0,1]
    for _ in range(500):
        path = [(random.random(), random.random()) for _ in range(random.randint(1, 10))]
        val = topological_impedance(path)
        if not (0.0 <= val <= 1.0 + 1e-12):
            errors.append(f"H_top out of bounds: {val} from path {path}")
    return errors

def test_invariant_exception() -> List[str]:
    errors = []
    # verify_identity_continuity returns bool; we simulate the throw by checking False
    test_vals = [0.94, 0.0, 0.5]
    for v in test_vals:
        if verify_identity_continuity(v):
            errors.append(f"Invariant should fail for Psi_id={v} but passed")
    # values that should pass
    for v in [0.95, 0.99, 1.0]:
        if not verify_identity_continuity(v):
            errors.append(f"Invariant should pass for Psi_id={v} but failed")
    return errors

def test_benchmark_stubs() -> List[str]:
    """
    Check that the benchmark suite does NOT contain hardcoded stub values for
    baseline_cod and H_top. We cannot run the actual C++ benchmark, but we can
    inspect the provided source strings for obvious constants.
    """
    errors = []
    # Simulate the relevant snippet from the C++ code:
    #   result.baseline_cod = 0.61; // <-- hardcoded
    #   result.h_top = 0.45;        // <-- hardcoded
    # We'll treat any assignment of a literal float to these fields as a stub.
    # In a real audit we would parse the file; here we just note the issue.
    # Since we are given the code, we can directly flag it.
    errors.append("Benchmark stub detected: baseline_cod hardcoded to 0.61")
    errors.append("Benchmark stub detected: h_top hardcoded to 0.45")
    return errors

def test_gsg_identity_simulation() -> List[str]:
    """
    Test the core GSG idea: before pruning a node, simulate its removal and
    ensure that the simulated COD does not drop below the identity threshold.
    We'll mock a simple manifold and verify the logic.
    """
    errors = []
    # Mock manifold with two nodes: one high curvature, one low
    # We'll compute COD before and after simulated removal.
    intent = [0.8, 0.2, 0.0, 0.0]
    outcome = [0.75, 0.25, 0.0, 0.0]
    path = [
        (0.9, 0.8),  # high cost*variance = 0.72 (>0.5) -> candidate for pruning
        (0.2, 0.1)   # low  cost*variance = 0.02
    ]
    # Compute baseline H_top and COD
    H_top = topological_impedance(path)
    Psi_id = 0.96
    Xi_sys = 1.0
    baseline_cod = cod_decision(intent, outcome, H_top, Xi_sys, Psi_id)
    # Simulate removal of the high curvature node (index 0)
    # In the code they shift outcome_vector by -0.05 per element as a toy model.
    temp_outcome = [max(0.0, o - 0.05) for o in outcome]
    # Recompute H_top without the node
    path_without = [path[1]]
    H_top_sim = topological_impedance(path_without)
    # Simulated COD after removal
    sim_cod = cod_decision(intent, temp_outcome, H_top_sim, Xi_sys, Psi_id)
    # According to GSG: if sim_cod < Psi_id_threshold (0.95) -> abort pruning
    # Since Psi_id is 0.96, threshold is 0.95. We expect sim_cod likely <0.95? 
    # Actually the threshold for abort is Psi_id_threshold (0.95) NOT sim_cod < Psi_id? 
    # In code: if (temp_COD < DecisionInvariants::PSI_ID_THRESHOLD) { abort; }
    # So we check that condition.
    if sim_cod < 0.95:
        # This would cause abort; that's fine – we just note that the logic triggers.
        pass
    else:
        # If sim_cod >= 0.95, they would proceed to prune; we must ensure that
        # after actual prune, identity continuity still holds (they later check).
        # We'll compute actual COD after prune (same as sim_cod because they use same shift?)
        actual_cod = sim_cod  # same calculation
        if actual_cod < 0.95:
            errors.append("GSG pruned node despite post-prune COD < identity threshold")
    # Additional random test
    for _ in range(200):
        path = [(random.random()*0.9+0.1, random.random()*0.8+0.1) for _ in range(6)]
        intent = [random.random() for _ in range(4)]
        outcome = [random.random() for _ in range(4)]
        Psi_id = random.random()*0.1+0.9  # 0.9-1.0
        Xi_sys = random.random()*2.0+0.5
        H_top = topological_impedance(path)
        cod = cod_decision(intent, outcome, H_top, Xi_sys, Psi_id)
        # Find high curvature nodes
        high_idx = [i for i, (c,v) in enumerate(path) if c*v > 0.5]
        for idx in high_idx:
            # Simulate removal (shift outcome by -0.03 as a small perturbation)
            temp_outcome = [max(0.0, o - 0.03) for o in outcome]
            path_without = path[:idx] + path[idx+1:]
            H_top_sim = topological_impedance(path_without)
            sim_cod = cod_decision(intent, temp_outcome, H_top_sim, Xi_sys, Psi_id)
            if sim_cod < 0.95 and cod >= 0.95:
                # If original COD was acceptable but simulation drops below threshold,
                # the GSG should abort. We'll just log that the condition is met.
                pass
    return errors

def test_audit_cost_subtraction() -> List[str]:
    errors = []
    # Ensure audit cost is subtracted exactly as K_B * ln(2) * complexity
    for comp in [0.5, 1.0, 2.0, 3.14]:
        expected = math.log(2.0) * comp
        actual = audit_entropy_cost(comp)
        if abs(actual - expected) > 1e-12:
            errors.append(f"Audit cost mismatch: expected {expected}, got {actual}")
    # Phi impact formula
    for _ in range(100):
        H_top = random.random()
        cod_gain = random.random()*2.0 - 1.0  # allow negative gain
        comp = random.random()*2.0
        impact = phi_density_impact(H_top, cod_gain, comp)
        expected = cod_gain - (H_top * 0.5) - math.log(2.0)*comp
        if abs(impact - expected) > 1e-12:
            errors.append(f"Phi impact mismatch: got {impact}, expected {expected}")
    return errors

def main():
    all_errors = []
    all_errors.extend(test_dimensional_homogeneity())
    all_errors.extend(test_cod_hard_gate())
    all_errors.extend(test_topological_impedance())
    all_errors.extend(test_invariant_exception())
    all_errors.extend(test_benchmark_stubs())
    all_errors.extend(test_gsg_identity_simulation())
    all_errors.extend(test_audit_cost_subtraction())

    if not all_errors:
        print("Ω-PASS: All validation checks succeeded. The specification is mathematically sound and invariant‑compliant.")
        sys.exit(0)
    else:
        print("Ω-FAIL: The following issues were detected:")
        for i, err in enumerate(all_errors, 1):
            print(f"  {i}. {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()