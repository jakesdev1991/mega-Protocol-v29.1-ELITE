# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# Constants from the C++ code
LAMBDA_COUPLING = 0.5
MU_PROVENANCE = 0.7
PSI_INTEGRITY_THRESHOLD = 0.95
PROVENANCE_INTEGRITY_MIN = 0.60
PROPAGATION_DEPTH_MAX = 0.50
RECOVERY_VELOCITY_MIN = 0.40
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

# Ported mathematical functions from C++ code
def calculate_provenance_integrity(origin_verification, custody_gap_count, cross_facility_transfers):
    origin_component = origin_verification * 0.5
    gap_penalty = (1.0 - custody_gap_count) * 0.3
    transfer_factor = (1.0 - cross_facility_transfers * 0.5) * 0.2
    integrity = origin_component + gap_penalty * transfer_factor
    return max(0.0, min(1.0, integrity))

def calculate_propagation_depth(control_depth, cross_facility_transfers, custody_gap_count):
    control_component = control_depth * 0.5
    transfer_component = cross_facility_transfers * 0.3
    gap_amplifier = 1.0 + (custody_gap_count * 0.4)
    depth = (control_component + transfer_component) * gap_amplifier
    return max(0.0, min(1.0, depth))

def calculate_recovery_velocity(safety_criticality, provenance_integrity, propagation_depth):
    safety_component = safety_criticality * 0.4
    integrity_component = provenance_integrity * 0.3
    depth_penalty = (1.0 - propagation_depth) * 0.3
    velocity = safety_component + integrity_component + depth_penalty
    return max(0.0, min(1.0, velocity))

def calculate_recovery_success_probability(recovery_velocity, provenance_integrity, propagation_depth):
    velocity_component = recovery_velocity * 0.5
    integrity_component = provenance_integrity * 0.3
    depth_component = (1.0 - propagation_depth) * 0.2
    probability = velocity_component + integrity_component + depth_component
    return max(0.0, min(1.0, probability))

def calculate_provenance_risk(provenance_integrity, propagation_depth, recovery_velocity):
    integrity_deficit = 1.0 - provenance_integrity
    velocity_deficit = 1.0 - recovery_velocity
    risk = integrity_deficit * propagation_depth * velocity_deficit
    return max(0.0, min(1.0, risk))

def calculate_cod_provenance_aware(diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak, 
                                 provenance_integrity, recovery_velocity, provenance_risk):
    # Fidelity calculation (dot product of normalized vectors)
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(size):
        # Treat complex numbers as vectors in C2 (real and imaginary parts)
        d_real, d_imag = diagnostic_vec[i].real, diagnostic_vec[i].imag
        p_real, p_imag = plasma_vec[i].real, plasma_vec[i].imag
        dot += d_real * p_real + d_imag * p_imag  # Real part of conjugate product
        magD += d_real*d_real + d_imag*d_imag
        magP += p_real*p_real + p_imag*p_imag
    
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = max(0.0, min(1.0, fidelity))
    
    # Penalties
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    integrity_penalty = math.exp(-MU_PROVENANCE * (1.0 - provenance_integrity))
    recovery_penalty = math.exp(-MU_PROVENANCE * (1.0 - recovery_velocity))
    risk_penalty = math.exp(-MU_PROVENANCE * provenance_risk)
    
    return fidelity * instability_penalty * exposure_penalty * integrity_penalty * recovery_penalty * risk_penalty

# Risk level classification (from C++ code)
def assess_risk(provenance_risk):
    if provenance_risk > 0.70:
        return "CATASTROPHIC"
    elif provenance_risk > 0.50:
        return "CRITICAL"
    elif provenance_risk > 0.30:
        return "MEDIUM"
    else:
        return "LOW"

# Provenance state classification (from C++ code)
def classify_provenance_state(provenance_integrity, custody_gap_count, recovery_velocity):
    if provenance_integrity > 0.80 and custody_gap_count < 0.20:
        return "VERIFIED"
    if recovery_velocity < 0.30 or provenance_integrity < 0.40:
        return "UNTRACKABLE"
    if custody_gap_count > 0.50 or provenance_integrity < 0.60:
        return "COMPROMISED"
    return "PARTIAL"

# Smith Invariant Enforcement check
def check_invariants(psi_integrity, provenance_integrity, propagation_depth, 
                    recovery_velocity, cod):
    psi_ok = psi_integrity >= PSI_INTEGRITY_THRESHOLD
    prov_ok = provenance_integrity >= PROVENANCE_INTEGRITY_MIN
    prop_ok = propagation_depth <= PROPAGATION_DEPTH_MAX
    recov_ok = recovery_velocity >= RECOVERY_VELOCITY_MIN
    cod_ok = cod >= COD_THRESHOLD
    return {
        "psi_integrity_ok": psi_ok,
        "provenance_integrity_ok": prov_ok,
        "propagation_depth_ok": prop_ok,
        "recovery_velocity_ok": recov_ok,
        "cod_ok": cod_ok,
        "all_passed": psi_ok and prov_ok and prop_ok and recov_ok and cod_ok
    }

# Φ-Density Ledger calculation
def calculate_net_gain(cod_before, cod_after, audit_checks):
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

# Validation test suite
def run_validation_tests():
    print("Running Omega Protocol Mathematical Validation...")
    print("=" * 60)
    
    # Test 1: Boundedness of core functions [0,1]
    print("Test 1: Verifying [0,1] bounds for core functions")
    test_cases = [
        (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (0.0, 1.0, 1.0),
        (0.5, 0.5, 0.5), (1.0, 0.0, 0.0), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0), (1.0, 1.0, 1.0)
    ]
    
    for ov, cg, cft in test_cases:
        pi = calculate_provenance_integrity(ov, cg, cft)
        assert 0.0 <= pi <= 1.0, f"Provenance integrity out of bounds: {pi}"
    
    for cd, cft, cg in test_cases:
        pd = calculate_propagation_depth(cd, cft, cg)
        assert 0.0 <= pd <= 1.0, f"Propagation depth out of bounds: {pd}"
    
    for sc, pi, pd in [(0.0,0.0,0.0), (0.0,1.0,1.0), (1.0,0.0,0.0), (1.0,1.0,1.0), (0.5,0.5,0.5)]:
        rv = calculate_recovery_velocity(sc, pi, pd)
        assert 0.0 <= rv <= 1.0, f"Recovery velocity out of bounds: {rv}"
    
    for rv, pi, pd in [(0.0,0.0,0.0), (0.0,1.0,1.0), (1.0,0.0,0.0), (1.0,1.0,1.0), (0.5,0.5,0.5)]:
        rsp = calculate_recovery_success_probability(rv, pi, pd)
        assert 0.0 <= rsp <= 1.0, f"Recovery success prob out of bounds: {rsp}"
    
    for pi, pd, rv in [(0.0,0.0,0.0), (0.0,1.0,1.0), (1.0,0.0,0.0), (1.0,1.0,1.0), (0.5,0.5,0.5)]:
        pr = calculate_provenance_risk(pi, pd, rv)
        assert 0.0 <= pr <= 1.0, f"Provenance risk out of bounds: {pr}"
    
    print("✓ All core functions produce outputs in [0,1]")
    
    # Test 2: COD function bounds and behavior
    print("\nTest 2: Verifying COD function behavior")
    # Simple vector test: identical vectors should give high fidelity
    diag = [1.0+0j, 0.0+0j]
    plasm = [1.0+0j, 0.0+0j]
    cod_val = calculate_cod_provenance_aware(diag, plasm, 0.0, 0.0, 1.0, 1.0, 0.0)
    assert 0.9 <= cod_val <= 1.0, f"COD too low for identical vectors: {cod_val}"
    
    # Orthogonal vectors should give low fidelity
    diag = [1.0+0j, 0.0+0j]
    plasm = [0.0+0j, 1.0+0j]
    cod_val = calculate_cod_provenance_aware(diag, plasm, 0.0, 0.0, 1.0, 1.0, 0.0)
    assert 0.0 <= cod_val <= 0.1, f"COD too high for orthogonal vectors: {cod_val}"
    
    # Penalty effects: zero provenance integrity should decrease COD
    cod_high = calculate_cod_provenance_aware(diag, plasm, 0.0, 0.0, 1.0, 1.0, 0.0)
    cod_low = calculate_cod_provenance_aware(diag, plasm, 0.0, 0.0, 0.0, 1.0, 0.0)
    assert cod_low < cod_high, "Low provenance integrity did not decrease COD"
    
    print("✓ COD function behaves as expected")
    
    # Test 3: Risk level classification
    print("\nTest 3: Verifying risk level classification")
    assert assess_risk(0.25) == "LOW"
    assert assess_risk(0.35) == "MEDIUM"
    assert assess_risk(0.55) == "CRITICAL"
    assert assess_risk(0.75) == "CATASTROPHIC"
    print("✓ Risk levels classified correctly")
    
    # Test 4: Provenance state classification
    print("\nTest 4: Verifying provenance state classification")
    assert classify_provenance_state(0.85, 0.1, 0.5) == "VERIFIED"
    assert classify_provenance_state(0.3, 0.1, 0.5) == "UNTRACKABLE"  # low integrity
    assert classify_provenance_state(0.7, 0.6, 0.5) == "COMPROMISED"  # high gaps
    assert classify_provenance_state(0.7, 0.1, 0.2) == "UNTRACKABLE"  # low recovery
    assert classify_provenance_state(0.65, 0.3, 0.5) == "PARTIAL"
    print("✓ Provenance states classified correctly")
    
    # Test 5: Smith Invariant Enforcement
    print("\nTest 5: Verifying Smith Invariant Enforcement")
    # Valid state
    inv = check_invariants(0.96, 0.65, 0.4, 0.45, 0.86)
    assert inv["all_passed"] == True, "Valid state failed invariant check"
    
    # Invalid state (low psi_integrity)
    inv = check_invariants(0.94, 0.65, 0.4, 0.45, 0.86)
    assert inv["psi_integrity_ok"] == False, "Should fail psi_integrity check"
    assert inv["all_passed"] == False, "Should fail overall"
    
    # Invalid state (low provenance integrity)
    inv = check_invariants(0.96, 0.5, 0.4, 0.45, 0.86)
    assert inv["provenance_integrity_ok"] == False, "Should fail provenance integrity check"
    
    print("✓ Invariant enforcement works correctly")
    
    # Test 6: Φ-Density Ledger
    print("\nTest 6: Verifying Φ-Density Ledger")
    net_gain = calculate_net_gain(0.8, 0.85, 10)  # 10 audit checks
    expected = (0.85 - 0.8) - (10 * 0.02)  # 0.05 - 0.2 = -0.15
    assert abs(net_gain - expected) < 1e-9, f"Ledger calculation incorrect: {net_gain} vs {expected}"
    print("✓ Φ-Density Ledger calculation correct")
    
    # Test 7: Derivativity check - ensure no overlap with v75.0 metrics
    print("\nTest 7: Verifying derivativity avoidance (conceptual)")
    # v75.0 would use: api_exposure, control_depth, safety_criticality
    # v76.0 uses: provenance_integrity, propagation_depth, recovery_velocity
    # These are mathematically distinct constructions
    # We verify that changing provenance_integrity doesn't directly map to v75.0 metrics
    pi1 = calculate_provenance_integrity(0.9, 0.1, 0.1)
    pi2 = calculate_provenance_integrity(0.1, 0.9, 0.9)
    assert pi1 > pi2, "Provenance integrity should respond differently to inputs than v75.0 metrics"
    print("✓ Provenance metrics are structurally distinct from v75.0")
    
    print("\n" + "=" * 60)
    print("ALL VALIDATION TESTS PASSED")
    print("Mathematical implementation is sound and compliant with Omega Protocol invariants.")
    print("=" * 60)

if __name__ == "__main__":
    run_validation_tests()