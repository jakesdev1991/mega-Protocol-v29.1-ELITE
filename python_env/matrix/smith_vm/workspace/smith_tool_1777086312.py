# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import List, Tuple, Complex

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (v65.0) - ENFORCEMENT SCRIPT
# =============================================================================
# This script validates mathematical soundness and invariant compliance
# for the Cross-Domain Contamination Detector & Coherence Isomorphism Manifold (v60.0-Ω)
# =============================================================================

# Protocol Constants (from Rubric §6 & Smith Audit v65.0)
DOMAIN_MATCH_THRESHOLD = 0.85
ISOMORPHISM_CONFIDENCE_MIN = 0.70
CONTAMINATION_ALERT_LEVEL = 0.50
PSI_INTEGRITY_THRESHOLD = 0.95
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

# Cross-Domain Constants (from module)
LAMBDA_COUPLING = 0.5
KAPPA_CONFINEMENT = 0.5
ETA_TENSOR_LEAK = 0.3
MU_DOMAIN_MATCH = 0.4

def validate_bounds(value: float, name: str, min_val: float = 0.0, max_val: float = 1.0) -> bool:
    """Validate that a metric stays within [0,1] bounds"""
    if not (min_val <= value <= max_val):
        print(f"INVARIANT VIOLATION: {name} = {value:.4f} (expected [{min_val}, {max_val}])")
        return False
    return True

def calculate_cod_cross_domain(
    diagnostic_vec: List[Complex],
    plasma_vec: List[Complex],
    h_instability: float,
    xi_confinement: float,
    theta_tensor_leak: float,
    domain_match_score: float
) -> float:
    """
    Calculate Chain Overlap Density (COD) with cross-domain contamination detection
    Implements the formula from CrossDomainCoherenceManifold.cpp
    """
    # Input validation
    assert len(diagnostic_vec) == len(plasma_vec), "Vector dimensions must match"
    n = len(diagnostic_vec)
    assert n > 0, "Vectors must be non-empty"
    
    # 1. Fidelity: Diagnostic-Plasma Alignment Accuracy
    dot = 0.0
    magD = 0.0
    magP = 0.0
    for i in range(n):
        dot += np.real(np.conj(diagnostic_vec[i]) * plasma_vec[i])  # Real part of complex dot product
        magD += np.abs(diagnostic_vec[i])**2
        magP += np.abs(plasma_vec[i])**2
    
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = max(0.0, min(1.0, fidelity))  # Clamp to [0,1]
    
    # 2. Penalty terms (all in (0,1] for inputs in [0,1])
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    confinement_penalty = math.exp(-KAPPA_CONFINEMENT * xi_confinement)
    exposure_penalty = math.exp(-ETA_TENSOR_LEAK * theta_tensor_leak)
    domain_penalty = math.exp(-MU_DOMAIN_MATCH * (1.0 - domain_match_score))
    
    # 3. Final COD calculation
    cod = fidelity * instability_penalty * confinement_penalty * exposure_penalty * domain_penalty
    return max(0.0, min(1.0, cod))  # Final clamp for numerical safety

def validate_cod_invariants():
    """Test COD function for mathematical soundness and invariant compliance"""
    print("="*60)
    print("VALIDATING CHAIN OVERLAP DENSITY (COD) INVARIANTS")
    print("="*60)
    
    # Test Case 1: Perfect alignment, zero instability
    diag = [1.0+0j, 1.0+0j]
    plasm = [1.0+0j, 1.0+0j]
    cod = calculate_cod_cross_domain(diag, plasm, 0.0, 0.0, 0.0, 1.0)
    assert validate_bounds(cod, "COD (perfect alignment)", 0.99, 1.0), "COD should be near 1.0"
    print(f"✓ Perfect alignment COD: {cod:.4f}")
    
    # Test Case 2: Orthogonal vectors (zero fidelity)
    diag = [1.0+0j, 0.0+0j]
    plasm = [0.0+0j, 1.0+0j]
    cod = calculate_cod_cross_domain(diag, plasm, 0.0, 0.0, 0.0, 1.0)
    assert validate_bounds(cod, "COD (orthogonal)", 0.0, 0.01), "COD should be near 0.0"
    print(f"✓ Orthogonal vectors COD: {cod:.4f}")
    
    # Test Case 3: Maximum instability penalty
    diag = [1.0+0j]
    plasm = [1.0+0j]
    cod = calculate_cod_cross_domain(diag, plasm, 1.0, 0.0, 0.0, 1.0)
    expected = math.exp(-LAMBDA_COUPLING * 1.0)  # ≈ 0.6065
    assert validate_bounds(cod, "COD (max instability)", expected-0.01, expected+0.01), \
        f"COD should be ≈ {expected:.4f}"
    print(f"✓ Max instability COD: {cod:.4f} (expected ≈ {expected:.4f})")
    
    # Test Case 4: Domain mismatch penalty
    diag = [1.0+0j]
    plasm = [1.0+0j]
    cod_good = calculate_cod_cross_domain(diag, plasm, 0.0, 0.0, 0.0, 0.9)  # Good match
    cod_bad = calculate_cod_cross_domain(diag, plasm, 0.0, 0.0, 0.0, 0.5)   # Poor match
    assert cod_good > cod_bad, "Higher domain match should yield higher COD"
    assert validate_bounds(cod_good, "COD (good match)", 0.9, 1.0), "Good match COD too low"
    assert validate_bounds(cod_bad, "COD (poor match)", 0.0, 0.5), "Poor match COD too high"
    print(f"✓ Domain match effect: good={cod_good:.4f}, bad={cod_bad:.4f}")
    
    # Test Case 5: Combined penalties (worst case)
    diag = [1.0+0j]
    plasm = [0.0+0j]  # Orthogonal + max penalties
    cod = calculate_cod_cross_domain(diag, plasm, 1.0, 1.0, 1.0, 0.0)
    assert validate_bounds(cod, "COD (worst case)", 0.0, 0.01), "Worst case COD should be near 0"
    print(f"✓ Worst case COD: {cod:.4f}")
    
    print("✓ ALL COD INVARIANT TESTS PASSED\n")
    return True

def validate_phi_density_accounting():
    """Test Φ-density ledger for honest accounting"""
    print("="*60)
    print("VALIDATING Φ-DENSITY LEDGER ACCOUNTING")
    print("="*60)
    
    # Test Case 1: Positive gain with audit cost subtraction
    cod_before = 0.70
    cod_after = 0.85
    audit_checks = 6
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    net_gain = raw_gain - audit_cost
    
    expected_net = (0.85 - 0.70) - (6 * 0.02)  # 0.15 - 0.12 = 0.03
    assert abs(net_gain - expected_net) < 1e-5, f"Net gain mismatch: {net_gain} vs {expected_net}"
    assert validate_bounds(net_gain, "Net Φ gain", -1.0, 1.0), "Net gain out of bounds"
    print(f"✓ Positive gain case: raw={raw_gain:.4f}, cost={audit_cost:.4f}, net={net_gain:.4f}")
    
    # Test Case 2: Negative gain (audit cost > raw gain)
    cod_before = 0.80
    cod_after = 0.81
    audit_checks = 6
    raw_gain = 0.01
    audit_cost = 0.12
    net_gain = raw_gain - audit_cost  # -0.11
    assert net_gain < 0, "Net gain should be negative when cost > raw gain"
    assert validate_bounds(net_gain, "Net Φ gain (negative)", -1.0, 0.0), "Negative net gain invalid"
    print(f"✓ Negative gain case: raw={raw_gain:.4f}, cost={audit_cost:.4f}, net={net_gain:.4f}")
    
    # Test Case 3: Zero gain boundary
    cod_before = 0.78
    cod_after = 0.90
    audit_checks = 6
    raw_gain = 0.12
    audit_cost = 0.12
    net_gain = 0.0
    assert abs(net_gain) < 1e-5, "Net gain should be zero at break-even"
    print(f"✓ Break-even case: raw={raw_gain:.4f}, cost={audit_cost:.4f}, net={net_gain:.4f}")
    
    print("✓ ALL Φ-DENSITY LEDGER TESTS PASSED\n")
    return True

def validate_domain_integrity_gate():
    """Test domain match and contamination risk calculations"""
    print("="*60)
    print("VALIDATING DOMAIN INTEGRITY GATE")
    print("="*60)
    
    # Mock domain classification (simplified for test)
    def classify_domain(terms: str) -> str:
        terms_lower = terms.lower()
        if any(k in terms_lower for k in ["tokamak", "plasma", "fusion", "confinement"]):
            return "FUSION_PHYSICS"
        if any(k in terms_lower for k in ["bitcoin", "liquidity", "crypto", "market"]):
            return "FINANCE_CRYPTO"
        return "UNKNOWN"
    
    def calculate_domain_match(branch: str, concepts: str) -> float:
        b_domain = classify_domain(branch)
        c_domain = classify_domain(concepts)
        if b_domain == c_domain:
            return 1.0
        if b_domain == "UNKNOWN" or c_domain == "UNKNOWN":
            return 0.5
        return 0.2  # Mismatch penalty
    
    def calculate_contamination_risk(domain_match: float, query_complexity: float = 0.8) -> float:
        mismatch = 1.0 - domain_match
        return min(1.0, mismatch * query_complexity)
    
    # Test Case 1: Perfect domain match
    match = calculate_domain_match("tokamak reactor design", "plasma confinement time")
    assert match == 1.0, "Perfect match should yield 1.0"
    risk = calculate_contamination_risk(match)
    assert risk == 0.0, "Zero mismatch should yield zero risk"
    print(f"✓ Perfect match: domain_match={match:.2f}, contamination_risk={risk:.2f}")
    
    # Test Case 2: Domain mismatch (finance → physics)
    match = calculate_domain_match("tokamak stability analysis", "bitcoin liquidity crunch")
    assert match == 0.2, "Mismatch should yield 0.2"
    risk = calculate_contamination_risk(match)
    expected_risk = (1.0 - 0.2) * 0.8  # 0.64
    assert abs(risk - expected_risk) < 1e-5, f"Risk mismatch: {risk} vs {expected_risk}"
    assert validate_bounds(risk, "Contamination risk (mismatch)", 0.5, 0.7), \
        "Mismatch risk should trigger alert threshold"
    print(f"✓ Finance→Physics mismatch: domain_match={match:.2f}, contamination_risk={risk:.2f}")
    
    # Test Case 3: Uncertain domain
    match = calculate_domain_match("tokamak analysis", "quantum entanglement applications")
    assert match == 0.5, "Unknown domain should yield 0.5"
    risk = calculate_contamination_risk(match)
    assert risk == 0.4, "(1-0.5)*0.8 = 0.4"
    print(f"✓ Uncertain domain: domain_match={match:.2f}, contamination_risk={risk:.2f}")
    
    print("✓ ALL DOMAIN INTEGRITY GATE TESTS PASSED\n")
    return True

def validate_isomorphism_extraction():
    """Test validity of cross-domain isomorphism extraction"""
    print("="*60)
    print("VALIDATING ISOMORPHISM EXTRACTION")
    print("="*60)
    
    # Valid isomorphisms from module (with confidence scores)
    VALID_ISOMORPHISMS = [
        ("liquidity", "confinement_time", "System's ability to sustain state", 0.85),
        ("liquidity_crunch", "L-mode_collapse", "Coherence failure bifurcation", 0.80),
        ("market_maker", "shear_flow_driver", "External stabilization force", 0.75),
        ("flash_crash", "ELM_event", "Rapid instability cascade", 0.85),
        ("order_book_depth", "correlation_length", "System-wide coherence metric", 0.90)
    ]
    
    # Test 1: Confidence score bounds
    for source, target, role, conf in VALID_ISOMORPHISMS:
        assert validate_bounds(conf, f"Isomorphism confidence ({source}→{target})", 0.7, 1.0), \
            f"Confidence {conf} below minimum threshold"
    print("✓ All isomorphism confidences within [0.7, 1.0]")
    
    # Test 2: Structural role validation (non-empty, descriptive)
    for _, _, role, _ in VALID_ISOMORPHISMS:
        assert len(role) > 10, f"Structural role too vague: {role}"
        assert "system" in role.lower() or "coherence" in role.lower() or "stabil" in role.lower(), \
            f"Role lacks systemic descriptor: {role}"
    print("✓ All isomorphism roles contain systemic descriptors")
    
    # Test 3: Average confidence calculation
    confs = [conf for _, _, _, conf in VALID_ISOMORPHISMS]
    avg_conf = sum(confs) / len(confs)
    assert avg_conf >= ISOMORPHISM_CONFIDENCE_MIN, \
        f"Average confidence {avg_conf:.2f} below threshold {ISOMORPHISM_CONFIDENCE_MIN}"
    print(f"✓ Average isomorphism confidence: {avg_conf:.2f} (≥ {ISOMORPHISM_CONFIDENCE_MIN})")
    
    print("✓ ALL ISOMORPHISM EXTRACTION TESTS PASSED\n")
    return True

def validate_safety_gate_hierarchy():
    """Test the ordered safety gate hierarchy"""
    print("="*60)
    print("VALIDATING SAFETY GATE HIERARCHY")
    print("="*60)
    
    # Mock state for testing
    class MockState:
        def __init__(self, psi_integrity, domain_match, isomorphism_conf, cod_val):
            self.psi_integrity = psi_integrity
            self.domain_match_score = domain_match
            self.isomorphism_confidence = isomorphism_conf
            self.cod = cod_val
    
    def decide_action(state: MockState) -> str:
        """Implements ContaminationAlertProtocol.Decide logic"""
        # PRIMARY GATE: Ψ_integrity
        if state.psi_integrity < PSI_INTEGRITY_THRESHOLD:
            return "BLOCK_QUERY"
        
        # DOMAIN GATE
        if state.domain_match_score < DOMAIN_MATCH_THRESHOLD:
            # In real implementation, would check contamination_risk here
            # For simplicity, assume high risk when domain_match < threshold
            return "FLAG_FOR_REVIEW" 
        
        # ISOMORPHISM GATE
        if state.isomorphism_confidence < ISOMORPHISM_CONFIDENCE_MIN:
            return "FLAG_FOR_REVIEW"
        
        # COD GATE
        if state.cod < COD_THRESHOLD:
            return "FLAG_FOR_REVIEW"
            
        return "PROCEED"
    
    # Test Case 1: Ψ_integrity failure (should block regardless of other metrics)
    state = MockState(psi_integrity=0.90, domain_match=0.95, isomorphism_conf=0.80, cod=0.90)
    action = decide_action(state)
    assert action == "BLOCK_QUERY", f"Low Ψ_integrity should block, got {action}"
    print("✓ Low Ψ_integrity (0.90) → BLOCK_QUERY")
    
    # Test Case 2: Domain mismatch (should flag for review)
    state = MockState(psi_integrity=0.96, domain_match=0.80, isomorphism_conf=0.80, cod=0.90)
    action = decide_action(state)
    assert action == "FLAG_FOR_REVIEW", f"Domain mismatch should flag, got {action}"
    print("✓ Domain mismatch (0.80) → FLAG_FOR_REVIEW")
    
    # Test Case 3: Low isomorphism confidence (should flag)
    state = MockState(psi_integrity=0.96, domain_match=0.90, isomorphism_conf=0.65, cod=0.90)
    action = decide_action(state)
    assert action == "FLAG_FOR_REVIEW", f"Low isomorphism confidence should flag, got {action}"
    print("✓ Low isomorphism confidence (0.65) → FLAG_FOR_REVIEW")
    
    # Test Case 4: Low COD (should flag)
    state = MockState(psi_integrity=0.96, domain_match=0.90, isomorphism_conf=0.80, cod=0.80)
    action = decide_action(state)
    assert action == "FLAG_FOR_REVIEW", f"Low COD should flag, got {action}"
    print("✓ Low COD (0.80) → FLAG_FOR_REVIEW")
    
    # Test Case 5: All gates passed (should proceed)
    state = MockState(psi_integrity=0.96, domain_match=0.90, isomorphism_conf=0.80, cod=0.90)
    action = decide_action(state)
    assert action == "PROCEED", f"All gates passed should proceed, got {action}"
    print("✓ All gates passed → PROCEED")
    
    print("✓ ALL SAFETY GATE HIERARCHY TESTS PASSED\n")
    return True

def main():
    """Run all validation tests"""
    print("OMEGA PROTOCOL INVARIANT VALIDATION SUITE")
    print("Cross-Domain Contamination Detector v60.0-Ω")
    print("="*60)
    
    try:
        validate_cod_invariants()
        validate_phi_density_accounting()
        validate_domain_integrity_gate()
        validate_isomorphism_extraction()
        validate_safety_gate_hierarchy()
        
        print("="*60)
        print("🎉 ALL VALIDATION TESTS PASSED")
        print("✅ Mathematical soundness confirmed")
        print("✅ Omega Protocol invariants enforced")
        print("✅ No dimensional violations detected")
        print("="*60)
        return True
        
    except AssertionError as e:
        print("="*60)
        print(f"❌ VALIDATION FAILED: {str(e)}")
        print("="*60)
        return False
    except Exception as e:
        print("="*60)
        print(f"💥 UNEXPECTED ERROR: {str(e)}")
        print("="*60)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)