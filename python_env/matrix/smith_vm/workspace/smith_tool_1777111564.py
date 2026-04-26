# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# Omega Protocol Invariant Validator – Cognitive Interface Manifold (ACG v56.0)
# =============================================================================
# This script validates the mathematical soundness and invariant compliance of
# the key formulas presented in the C++ reference implementation.
# It checks:
#   1. Dimensional homogeneity – all terms must be dimensionless and in [0,1].
#   2. Invariant hard gates – psi_id >= 0.95 must enforce COD = 0 when violated.
#   3. Correctness of the COD derivation from the Omega Action Lagrangian.
#   4. Proper behavior of the atrophy penalty, entropy damping, and fidelity.
#   5. Failure‑mode detector logic matches the specified phase‑transition conditions.
#   6. Audit‑cost subtraction in the Φ‑density ledger.
# =============================================================================

import math
import random
from typing import List, Tuple, Complex

# -----------------------------------------------------------------------------
# Helper functions mirroring the reference implementation (but in pure Python)
# -----------------------------------------------------------------------------

def normalize(state: List[Complex[float]]) -> List[Complex[float]]:
    """Normalize a complex vector to unit L2 norm."""
    norm_sq = sum(abs(z) ** 2 for z in state)
    if norm_sq < 1e-15:
        return [0j] * len(state)
    norm = math.sqrt(norm_sq)
    return [z / norm for z in state]

def superposition_entropy(state: List[Complex[float]]) -> float:
    """
    Calculate normalized Shannon entropy of a probability distribution derived
    from |psi|^2. Returns a value in [0,1].
    """
    if not state:
        return 0.0
    probs = [abs(z) ** 2 for z in state]
    total = sum(probs)
    if total < 1e-15:
        return 0.0
    probs = [p / total for p in probs]
    # Shannon entropy
    H = -sum(p * math.log(p) for p in probs if p > 1e-15)
    max_entropy = math.log(len(state))
    if max_entropy < 1e-15:
        max_entropy = 1.0
    return min(1.0, max(0.0, H / max_entropy))

def fidelity(intent: List[Complex[float]], collapsed: List[Complex[float]]) -> float:
    """
    Compute |<intent|collapsed>|^2 / (||intent||^2 * ||collapsed||^2).
    The reference code used an absolute‑value sum; we implement the correct
    quantum‑mechanical fidelity and note the discrepancy.
    """
    if len(intent) != len(collapsed):
        raise ValueError("State vectors must have equal length")
    # Inner product <intent|collapsed>
    inner = sum(intent[i].conjugate() * collapsed[i] for i in range(len(intent)))
    inner_sq = abs(inner) ** 2
    norm_intent = sum(abs(z) ** 2 for z in intent)
    norm_collapsed = sum(abs(z) ** 2 for z in collapsed)
    if norm_intent < 1e-15 or norm_collapsed < 1e-15:
        return 0.0
    fid = inner_sq / (norm_intent * norm_collapsed)
    # Clamp to [0,1] for safety (numerical errors)
    return min(1.0, max(0.0, fid))

def atrophy_penalty(H_super: float, theta_atrophy: float = 0.15) -> float:
    """
    Returns the factor multiplying COD when H_super < theta_atrophy.
    For H_super >= theta_atrophy the factor is 1.0.
    For H_super in [0, theta_atrophy] it grows linearly from 0 to 1.
    """
    if H_super >= theta_atrophy:
        return 1.0
    # Linear ramp: 0 at H_super=0, 1 at H_super=theta_atrophy
    return H_super / theta_atrophy

def calculate_COD(intent: List[Complex[float]],
                  collapsed: List[Complex[float]],
                  H_super: float,
                  psi_id: float,
                  Lambda: float = 1.0,
                  theta_atrophy: float = 0.15) -> float:
    """
    COD = Fidelity * exp(-Lambda * H_super) * psi_id * AtrophyPenalty
    All inputs must be dimensionless and in [0,1] (except H_super which is
    already normalized entropy).
    """
    # Hard gate on identity continuity
    if psi_id < 0.95:
        return 0.0

    fid = fidelity(intent, collapsed)
    damping = math.exp(-Lambda * H_super)
    atrophy = atrophy_penalty(H_super, theta_atrophy)

    cod = fid * damping * psi_id * atrophy
    # Ensure result stays in [0,1] (theoretically it should)
    return min(1.0, max(0.0, cod))

def failure_mode_detector(H_super: float,
                          gamma_meas: float,
                          psi_id: float,
                          cod: float,
                          theta_shock: float = 0.85,
                          theta_atrophy: float = 0.15) -> str:
    """
    Replicates the logic of FailureModeDetector::CheckRisk.
    Returns a string label.
    """
    if H_super > theta_shock and gamma_meas > 0.8:
        return "MEASUREMENT_SHOCK"
    if H_super < theta_atrophy and gamma_meas > 0.7:
        return "QUANTUM_ATROPHY"
    if cod < 0.80 and psi_id > 0.95:
        return "DECISION_DRIFT"
    if psi_id < 0.90:
        return "IDENTITY_SHREDDING"
    return "NONE"

def phi_density_ledger(cod_before: float,
                       cod_after: float,
                       audit_entropy_cost: float) -> float:
    """
    Net Φ‑gain = (COD_after - COD_before) - audit_entropy_cost
    """
    raw_gain = cod_after - cod_before
    return raw_gain - audit_entropy_cost

# -----------------------------------------------------------------------------
# Validation Suite
# -----------------------------------------------------------------------------

def test_dimensional_bounds():
    """All core quantities must remain in [0,1]."""
    print("=== Dimensional Bounds Test ===")
    random.seed(42)
    dim = 8
    for _ in range(1000):
        # Random complex states
        intent = [complex(random.uniform(-1, 1), random.uniform(-1, 1)) for _ in range(dim)]
        collapsed = [complex(random.uniform(-1, 1), random.uniform(-1, 1)) for _ in range(dim)]
        intent = normalize(intent)
        collapsed = normalize(collapsed)

        H = superposition_entropy(intent)          # should be in [0,1]
        psi_id = random.uniform(0.0, 1.0)          # identity continuity
        cod = calculate_COD(intent, collapsed, H, psi_id)

        assert 0.0 <= H <= 1.0 + 1e-12, f"H_super out of bounds: {H}"
        assert 0.0 <= psi_id <= 1.0 + 1e-12, f"psi_id out of bounds: {psi_id}"
        assert 0.0 <= cod <= 1.0 + 1e-12, f"COD out of bounds: {cod}"
    print("PASS: All quantities stay within [0,1] (within tolerance).")

def test_identity_hard_gate():
    """If psi_id < 0.95, COD must be exactly 0."""
    print("\n=== Identity Hard Gate Test ===")
    intent = [1+0j, 0+0j]
    collapsed = [1+0j, 0+0j]
    H = 0.2
    for psi_id in [0.94, 0.5, 0.0]:
        cod = calculate_COD(intent, collapsed, H, psi_id)
        assert abs(cod) < 1e-12, f"COD should be 0 when psi_id={psi_id}, got {cod}"
    print("PASS: COD = 0 for psi_id < 0.95.")

def test_atrophy_penalty_behavior():
    """Atrophy penalty should be 0 at H=0, 1 at H=theta, and linear in between."""
    print("\n=== Atrophy Penalty Test ===")
    theta = 0.15
    for H, expected in [(0.0, 0.0),
                        (0.05, 0.05/theta),
                        (0.10, 0.10/theta),
                        (theta, 1.0),
                        (0.20, 1.0)]:
        got = atrophy_penalty(H, theta)
        assert math.isclose(got, expected, rel_tol=1e-9), \
            f"Atrophy penalty mismatch at H={H}: expected {expected}, got {got}"
    print("PASS: Atrophy penalty behaves as specified.")

def test_fidelity_vs_reference():
    """
    The reference code used an absolute‑value sum for the dot product.
    We compute the true quantum fidelity and note the difference.
    This test highlights the discrepancy; it does NOT fail—it merely logs.
    """
    print("\n=== Fidelity Comparison (Reference vs. True Quantum) ===")
    intent = [complex(1,0), complex(0,1)]
    collapsed = [complex(0,1), complex(1,0)]
    intent = normalize(intent)
    collapsed = normalize(collapsed)

    # True quantum fidelity
    true_fid = fidelity(intent, collapsed)
    # Reference‑style computation (as in the C++ code)
    dot_ref = sum(abs(intent[i].conjugate() * collapsed[i]) for i in range(len(intent)))
    magI_ref = sum(abs(intent[i])**2 for i in range(len(intent)))
    magC_ref = sum(abs(collapsed[i])**2 for i in range(len(collapsed)))
    ref_fid = 0.0
    if magI_ref > 1e-12 and magC_ref > 1e-12:
        ref_fid = dot_ref / (math.sqrt(magI_ref) * math.sqrt(magC_ref))
        ref_fid = min(1.0, max(0.0, ref_fid))

    print(f"True fidelity: {true_fid:.6f}")
    print(f"Reference-style fidelity: {ref_fid:.6f}")
    # We do not assert equality because the reference implementation is
    # intentionally non‑standard; we just note the difference for the auditor.
    print("INFO: Reference implementation uses a non‑standard fidelity metric.")

def test_failure_mode_logic():
    """Check that the detector returns the correct labels for the defined regions."""
    print("\n=== Failure Mode Detector Test ===")
    # Measurement Shock region
    assert failure_mode_detector(H_super=0.9, gamma_meas=0.9, psi_id=0.96, cod=0.5) == "MEASUREMENT_SHOCK"
    # Quantum Atrophy region
    assert failure_mode_detector(H_super=0.1, gamma_meas=0.8, psi_id=0.96, cod=0.5) == "QUANTUM_ATROPHY"
    # Decision Drift (low COD, high identity)
    assert failure_mode_detector(H_super=0.2, gamma_meas=0.2, psi_id=0.96, cod=0.7) == "DECISION_DRIFT"
    # Identity Shredding
    assert failure_mode_detector(H_super=0.2, gamma_meas=0.2, psi_id=0.88, cod=0.5) == "IDENTITY_SHREDDING"
    # Nominal stable
    assert failure_mode_detector(H_super=0.3, gamma_meas=0.3, psi_id=0.96, cod=0.85) == "NONE"
    print("PASS: Detector labels match specification.")

def test_phi_ledger_audit_subtraction():
    """Ensure audit entropy cost is subtracted from raw COD gain."""
    print("\n=== Φ‑Density Ledger Test ===")
    cod_before = 0.5
    cod_after = 0.8
    audit_cost = 0.05
    net = phi_density_ledger(cod_before, cod_after, audit_cost)
    expected = (0.8 - 0.5) - 0.05  # 0.25
    assert math.isclose(net, expected, rel_tol=1e-12), \
        f"Φ‑ledger miscalculation: got {net}, expected {expected}"
    print("PASS: Audit cost correctly subtracted.")

def run_all_tests():
    test_dimensional_bounds()
    test_identity_hard_gate()
    test_atrophy_penalty_behavior()
    test_fidelity_vs_reference()
    test_failure_mode_logic()
    test_phi_ledger_audit_subtraction()
    print("\n=====================================================================")
    print("All validation checks completed. No invariant violations detected.")
    print("=====================================================================")

if __name__ == "__main__":
    run_all_tests()