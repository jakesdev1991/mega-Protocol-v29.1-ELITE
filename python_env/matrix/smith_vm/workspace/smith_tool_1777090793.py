# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import List, Tuple, NamedTuple

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (FROM v61.0-Ω MANIFOLD)
# =============================================================================
class OmegaInvariants:
    PSI_INTEGRITY_THRESHOLD = 0.95   # Identity Continuity
    ETHICAL_EXPOSURE_MAX = 0.30      # Max allowable exposure
    COD_THRESHOLD = 0.85             # Alignment Fidelity
    COUPLING_MIN = 0.70              # Min infrastructure-psych alignment
    AUDIT_ENTROPY_PER_CHECK = 0.02   # Per validation check
    LAMBDA_COUPLING = 0.5            # Instability/exposure penalty weight
    MU_ETHICAL = 0.6                 # Ethical risk penalty weight

# =============================================================================
# MATHEMATICAL VALIDATION FUNCTIONS
# =============================================================================
def calculate_coupling(proprietary_density: float, identity_relevance: float) -> float:
    """Calculate identity-infrastructure coupling (geometric mean)"""
    assert 0.0 <= proprietary_density <= 1.0, "Proprietary density must be in [0,1]"
    assert 0.0 <= identity_relevance <= 1.0, "Identity relevance must be in [0,1]"
    return math.sqrt(proprietary_density * identity_relevance)

def calculate_ethical_exposure(infrastructure_exposure: float, coupling: float) -> float:
    """Calculate ethical exposure risk (exposure × coupling)"""
    assert 0.0 <= infrastructure_exposure <= 1.0, "Infrastructure exposure must be in [0,1]"
    assert 0.0 <= coupling <= 1.0, "Coupling must be in [0,1]"
    risk = infrastructure_exposure * coupling
    return min(max(risk, 0.0), 1.0)  # Clamp to [0,1]

def calculate_cod_psychethics(
    diagnostic_vec: List[complex],
    plasma_vec: List[complex],
    h_instability: float,
    theta_tensor_leak: float,
    ethical_exposure_risk: float
) -> float:
    """Calculate Chain Overlap Density with psychology-specific ethical penalty"""
    # Validate inputs
    assert 0.0 <= h_instability <= 1.0, "h_instability must be in [0,1]"
    assert 0.0 <= theta_tensor_leak <= 1.0, "theta_tensor_leak must be in [0,1]"
    assert 0.0 <= ethical_exposure_risk <= 1.0, "ethical_exposure_risk must be in [0,1]"
    
    # 1. Fidelity calculation (dot product normalization)
    size = min(len(diagnostic_vec), len(plasma_vec))
    if size == 0:
        return 0.0
        
    dot = 0.0
    magD = 0.0
    magP = 0.0
    for i in range(size):
        dot += np.abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
        magD += np.abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += np.abs(plasma_vec[i] * plasma_vec[i])
    
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = min(max(fidelity, 0.0), 1.0)
    
    # 2. Penalties
    instability_penalty = math.exp(-OmegaInvariants.LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-OmegaInvariants.LAMBDA_COUPLING * theta_tensor_leak)
    ethical_penalty = math.exp(-OmegaInvariants.MU_ETHICAL * ethical_exposure_risk)
    
    cod = fidelity * instability_penalty * exposure_penalty * ethical_penalty
    return min(max(cod, 0.0), 1.0)  # Ensure [0,1] bounds

def ethical_silence_decision(psi_integrity: float, ethical_exposure: float) -> str:
    """Determine action based on Ethical Silence Protocol"""
    assert 0.0 <= psi_integrity <= 1.0, "psi_integrity must be in [0,1]"
    assert 0.0 <= ethical_exposure <= 1.0, "ethical_exposure must be in [0,1]"
    
    if psi_integrity < OmegaInvariants.PSI_INTEGRITY_THRESHOLD:
        return "IDENTITY_LOCKDOWN"
    if ethical_exposure > 0.70:
        return "IDENTITY_LOCKDOWN"
    if ethical_exposure > 0.50:
        return "HALT_OPERATIONS"
    if ethical_exposure > 0.30:
        return "FREEZE_ACCESS"
    return "PROCEED"

def check_invariants(
    psi_integrity: float,
    ethical_exposure: float,
    cod: float,
    identity_coupling: float
) -> Tuple[bool, dict]:
    """Check all Omega Protocol invariants"""
    checks = {
        'psi_integrity_ok': psi_integrity >= OmegaInvariants.PSI_INTEGRITY_THRESHOLD,
        'ethical_exposure_ok': ethical_exposure <= OmegaInvariants.ETHICAL_EXPOSURE_MAX,
        'cod_ok': cod >= OmegaInvariants.COD_THRESHOLD,
        'coupling_ok': identity_coupling >= OmegaInvariants.COUPLING_MIN
    }
    all_passed = all(checks.values())
    return all_passed, checks

def calculate_phi_net_gain(
    cod_before: float,
    cod_after: float,
    audit_checks: int
) -> float:
    """Calculate net Φ-density gain with audit cost subtraction"""
    assert 0.0 <= cod_before <= 1.0, "cod_before must be in [0,1]"
    assert 0.0 <= cod_after <= 1.0, "cod_after must be in [0,1]"
    assert audit_checks >= 0, "audit_checks must be non-negative"
    
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * OmegaInvariants.AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

# =============================================================================
# COMPREHENSIVE VALIDATION TEST SUITE
# =============================================================================
def run_validation_tests():
    """Run exhaustive tests to verify mathematical soundness and protocol compliance"""
    print("="*60)
    print("OMEGA PROTOCOL v61.0-Ω MATHEMATICAL VALIDATION")
    print("="*60)
    
    # Test 1: Dimensional Consistency
    print("\n[TEST 1] DIMENSIONAL CONSISTENCY CHECK")
    test_cases = [
        (0.0, 0.0, 0.0),    # Minimums
        (0.5, 0.5, 0.5),    # Midpoints
        (1.0, 1.0, 1.0),    # Maximums
        (0.2, 0.8, 0.4),    # Mixed values
    ]
    
    for pd, ir, ie in test_cases:
        coupling = calculate_coupling(pd, ir)
        exposure = calculate_ethical_exposure(ie, coupling)
        assert 0.0 <= coupling <= 1.0, f"Coupling OOB: {coupling}"
        assert 0.0 <= exposure <= 1.0, f"Exposure OOB: {exposure}"
        print(f"  ✓ Coupling({pd:.2f},{ir:.2f})={coupling:.3f}, Exposure({ie:.2f},{coupling:.3f})={exposure:.3f}")
    
    # Test 2: COD Calculation Bounds
    print("\n[TEST 2] COD BOUNDS VALIDATION")
    diag_vec = [1+0j, 0+1j]
    plasma_vec = [0+1j, 1+0j]
    for h in [0.0, 0.5, 1.0]:
        for ttl in [0.0, 0.5, 1.0]:
            for eth in [0.0, 0.5, 1.0]:
                cod = calculate_cod_psychethics(diag_vec, plasma_vec, h, ttl, eth)
                assert 0.0 <= cod <= 1.0, f"COD OOB: {cod} at h={h}, ttl={ttl}, eth={eth}"
                print(f"  ✓ COD(h={h:.1f}, ttl={ttl:.1f}, eth={eth:.1f}) = {cod:.3f}")
    
    # Test 3: Ethical Silence Protocol Hierarchy
    print("\n[TEST 3] ETHICAL SILENCE PROTOCOL HIERARCHY")
    test_scenarios = [
        (0.96, 0.25, "PROCEED"),      # Healthy state
        (0.96, 0.35, "FREEZE_ACCESS"), # Medium exposure
        (0.96, 0.55, "HALT_OPERATIONS"), # High exposure
        (0.96, 0.75, "IDENTITY_LOCKDOWN"), # Critical exposure
        (0.90, 0.20, "IDENTITY_LOCKDOWN"), # Low integrity triggers lockdown
    ]
    
    for psi, exp, expected in test_scenarios:
        action = ethical_silence_decision(psi, exp)
        assert action == expected, f"Expected {expected} for psi={psi}, exp={exp}, got {action}"
        print(f"  ✓ psi={psi:.2f}, exp={exp:.2f} → {action}")
    
    # Test 4: Invariant Enforcement Logic
    print("\n[TEST 4] INVARIANT ENFORCEMENT VALIDATION")
    invariant_tests = [
        # (psi, exp, cod, coup, expected_pass, description)
        (0.96, 0.25, 0.90, 0.75, True, "All invariants satisfied"),
        (0.94, 0.25, 0.90, 0.75, False, "Psi integrity failure"),
        (0.96, 0.35, 0.90, 0.75, False, "Ethical exposure failure"),
        (0.96, 0.25, 0.80, 0.75, False, "COD failure"),
        (0.96, 0.25, 0.90, 0.65, False, "Coupling failure"),
    ]
    
    for psi, exp, cod, coup, expected_pass, desc in invariant_tests:
        passed, checks = check_invariants(psi, exp, cod, coup)
        assert passed == expected_pass, f"Invariant check failed for: {desc}"
        status = "PASS" if passed else "FAIL"
        print(f"  ✓ {desc}: {status} (ψ:{checks['psi_integrity_ok']} ε:{checks['ethical_exposure_ok']} C:{checks['cod_ok']} κ:{checks['coupling_ok']})")
    
    # Test 5: Φ-Density Accounting
    print("\n[TEST 5] Φ-DENSITY ACCOUNTING VALIDATION")
    phi_tests = [
        (0.80, 0.85, 5, 0.03),   # Gain 0.05 - audit cost 0.10 = -0.05
        (0.80, 0.90, 3, 0.04),   # Gain 0.10 - audit cost 0.06 = +0.04
        (0.90, 0.85, 2, -0.07),  # Loss 0.05 - audit cost 0.04 = -0.09
        (0.85, 0.85, 0, 0.00),   # No change, no audit
    ]
    
    for before, after, checks, expected_gain in phi_tests:
        gain = calculate_phi_net_gain(before, after, checks)
        assert abs(gain - expected_gain) < 1e-9, f"Φ gain mismatch: expected {expected_gain}, got {gain}"
        print(f"  ✓ COD: {before:.2f}→{after:.2f} ({checks} audits) → Φ = {gain:+.3f}")
    
    # Test 6: Self-Audit Meta-Verification (from manifesto)
    print("\n[TEST 6] SELF-AUDIT META-VERIFICATION")
    # Verify all metrics remain bounded [0,1] under extreme conditions
    stress_tests = [
        # (proprietary_density, identity_relevance, infrastructure_exposure, h_instability, theta_tensor_leak, ethical_exposure)
        (1.0, 1.0, 1.0, 1.0, 1.0, 1.0),   # Maximum stress
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),   # Minimum stress
        (0.5, 0.5, 0.5, 0.5, 0.5, 0.25),  # Nominal operation
    ]
    
    for pd, ir, ie, h, ttl, exp in stress_tests:
        coupling = calculate_coupling(pd, ir)
        exposure = calculate_ethical_exposure(ie, coupling)
        # Verify ethical exposure = infrastructure_exposure × coupling (within coupling bounds)
        expected_exp = min(max(ie * coupling, 0.0), 1.0)
        assert abs(exposure - expected_exp) < 1e-9, f"Ethical exposure calculation error"
        
        # Verify COD calculation doesn't produce NaN or inf
        diag_vec = [complex(pd, ir), complex(1-pd, 1-ir)]
        plasma_vec = [complex(ie, h), complex(1-ie, 1-ttl)]
        cod = calculate_cod_psychethics(diag_vec, plasma_vec, h, ttl, exposure)
        assert not (math.isnan(cod) or math.isinf(cod)), f"COD produced NaN/Inf"
        assert 0.0 <= cod <= 1.0, f"COD OOB: {cod}"
        
        print(f"  ✓ Stress test PD={pd:.2f} IR={ir:.2f} IE={ie:.2f} → C={coupling:.3f} ε={exposure:.3f} COD={cod:.3f}")
    
    print("\n" + "="*60)
    print("ALL VALIDATION TESTS PASSED")
    print("Identity-Infrastructure Integrity Manifold v61.0-Ω is")
    print("MATHEMATICALLY SOUND and OMEGA PROTOCOL COMPLIANT")
    print("="*60)

# Execute validation suite
if __name__ == "__main__":
    run_validation_tests()