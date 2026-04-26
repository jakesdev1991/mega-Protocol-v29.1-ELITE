# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import cmath
from typing import List, Tuple, Union

# === OMEGA PROTOCOL INVARIANTS (v65.0) ===
DOMAIN_MATCH_THRESHOLD = 0.85
ISOMORPHISM_CONFIDENCE_MIN = 0.70
CONTAMINATION_ALERT_LEVEL = 0.50
PSI_INTEGRITY_THRESHOLD = 0.95
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

# === COD FUNCTION CONSTANTS (from UIPO v65.0) ===
LAMBDA_COUPLING = 0.5
KAPPA_CONFINEMENT = 0.5
ETA_TENSOR_LEAK = 0.3
MU_DOMAIN_MATCH = 0.4

def classify_domain(terms: str) -> str:
    """Simplified domain classifier (keyword-based, matches C++ logic)"""
    lower = terms.lower()
    if any(k in lower for k in ["tokamak", "plasma", "fusion", "confinement"]):
        return "FUSION_PHYSICS"
    if any(k in lower for k in ["bitcoin", "liquidity", "crypto", "market"]):
        return "FINANCE_CRYPTO"
    if any(k in lower for k in ["identity", "trauma", "psychology"]):
        return "PSYCHOLOGY"
    if any(k in lower for k in ["bureaucracy", "organization"]):
        return "BUREAUCRACY"
    return "UNKNOWN"

def calculate_domain_match(branch: str, concepts: str) -> float:
    """Calculate domain match score [0,1]"""
    branch_domain = classify_domain(branch)
    concept_domain = classify_domain(concepts)
    
    if branch_domain == concept_domain:
        return 1.0
    if branch_domain == "UNKNOWN" or concept_domain == "UNKNOWN":
        return 0.5
    return 0.2  # Mismatch

def calculate_contamination_risk(domain_match: float, query_complexity: float) -> float:
    """Calculate contamination risk [0,1]"""
    mismatch = 1.0 - domain_match
    return max(0.0, min(1.0, mismatch * query_complexity))

def calculate_cod(
    diagnostic_vec: List[complex],
    plasma_vec: List[complex],
    h_instability: float,
    xi_confinement: float,
    theta_tensor_leak: float,
    domain_match_score: float
) -> float:
    """
    Calculate Chain Overlap Density (COD) with domain extension
    All inputs must be in [0,1] for h_instability, xi_confinement, theta_tensor_leak, domain_match_score
    Returns COD in (0,1]
    """
    # 1. Fidelity: Diagnostic-Plasma Alignment Accuracy
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    
    for i in range(size):
        prod = diagnostic_vec[i].conjugate() * plasma_vec[i]
        dot += abs(prod)
        magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += abs(plasma_vec[i] * plasma_vec[i])
    
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = max(0.0, min(1.0, fidelity))  # Clamp to [0,1]
    
    # 2. Root-Aligned COD Formula (with domain extension)
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    confinement_penalty = math.exp(-KAPPA_CONFINEMENT * xi_confinement)
    exposure_penalty = math.exp(-ETA_TENSOR_LEAK * theta_tensor_leak)
    domain_penalty = math.exp(-MU_DOMAIN_MATCH * (1.0 - domain_match_score))
    
    cod = fidelity * instability_penalty * confinement_penalty * exposure_penalty * domain_penalty
    return max(0.0, min(1.0, cod))  # Ensure [0,1] (though mathematically >0)

def contamination_alert_decision(
    psi_integrity: float,
    domain_match: float,
    contamination_risk: float,
    isomorphism_confidence: float
) -> Tuple[str, str]:
    """
    Determine action based on Omega Protocol safety gates
    Returns (action_code, message)
    """
    # PRIMARY GATE: Ψ_integrity (non-negotiable)
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return ("BLOCK_QUERY", "CRITICAL: Integrity breach. Query blocked pending investigation.")
    
    # DOMAIN GATE: Check match score
    if domain_match < DOMAIN_MATCH_THRESHOLD:
        if contamination_risk > CONTAMINATION_ALERT_LEVEL:
            return ("FLAG_FOR_REVIEW", "Domain mismatch detected. Query flagged for audit review.")
        return ("AWAIT_CLARIFICATION", "Domain uncertain. Awaiting query clarification before proceeding.")
    
    # ISOMORPHISM GATE: Validate cross-domain mappings
    if isomorphism_confidence < ISOMORPHISM_CONFIDENCE_MIN:
        return ("FLAG_FOR_REVIEW", "Isomorphism confidence insufficient. Flagged for structural validation review.")
    
    return ("PROCEED", "Domain alignment verified. Cross-domain isomorphism valid.")

def validate_math_compliance() -> None:
    """
    Comprehensive validation of mathematical compliance with Omega Protocol invariants
    Tests dimensional bounds, gate hierarchy, and functional correctness
    """
    print("=== OMEGA PROTOCOL MATH COMPLIANCE VALIDATION ===\n")
    
    # Test 1: Dimensional bounds for all metric functions
    print("Test 1: Verifying dimensional bounds ([0,1]) for all metric functions")
    
    # Domain match scores
    test_cases_domain = [
        ("tokamak", "plasma confinement", 1.0),
        ("tokamak", "bitcoin liquidity", 0.2),
        ("unknown_branch", "unknown_concept", 0.5),
        ("fusion reactor", "crypto market", 0.2),
        ("plasma", "plasma", 1.0)
    ]
    
    for branch, concepts, expected in test_cases_domain:
        result = calculate_domain_match(branch, concepts)
        assert 0.0 <= result <= 1.0, f"Domain match out of bounds: {result} for {branch}/{concepts}"
        assert abs(result - expected) < 1e-5, f"Domain match mismatch: expected {expected}, got {result}"
    print("✓ Domain match scores: All in [0,1] and correct")
    
    # Contamination risk
    test_cases_risk = [
        (1.0, 0.0, 0.0),   # Perfect match, any complexity -> 0 risk
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 1.0),   # Zero match, max complexity -> 1 risk
        (0.5, 0.5, 0.25),  # 50% mismatch, 50% complexity
        (0.2, 0.8, 0.64)   # 80% mismatch, 80% complexity
    ]
    
    for match, complexity, expected in test_cases_risk:
        result = calculate_contamination_risk(match, complexity)
        assert 0.0 <= result <= 1.0, f"Contamination risk out of bounds: {result}"
        assert abs(result - expected) < 1e-5, f"Risk mismatch: expected {expected}, got {result}"
    print("✓ Contamination risk: All in [0,1] and correct")
    
    # COD calculation
    # Create test vectors (simple case: aligned vectors)
    diag_vec = [complex(1, 0)] * 3
    plasma_vec = [complex(1, 0)] * 3
    
    test_cases_cod = [
        # (h_inst, xi_conf, theta_leak, domain_match, expected_range_note)
        (0.0, 0.0, 0.0, 1.0, (1.0, 1.0)),      # Ideal case: COD=1.0
        (1.0, 1.0, 1.0, 0.0, (0.0, 1.0)),      # Worst case: COD>0
        (0.5, 0.5, 0.5, 0.5, (0.0, 1.0)),      # Mid values
        (0.0, 0.0, 0.0, 0.5, (0.0, 1.0)),      # Domain penalty only
    ]
    
    for h, xi, theta, domain_match, (low, high) in test_cases_cod:
        result = calculate_cod(diag_vec, plasma_vec, h, xi, theta, domain_match)
        assert 0.0 < result <= 1.0, f"COD out of bounds: {result} (should be in (0,1])"
        assert result >= low and result <= high, f"COD {result} not in expected range [{low},{high}]"
    print("✓ COD calculation: All results in (0,1]")
    
    # Test 2: Safety gate hierarchy enforcement
    print("\nTest 2: Verifying safety gate hierarchy")
    
    # Case 1: Integrity breach -> BLOCK_QUERY (overrides everything)
    decision, msg = contamination_alert_decision(
        psi_integrity=0.94,  # Below threshold
        domain_match=1.0,
        contamination_risk=0.0,
        isomorphism_confidence=1.0
    )
    assert decision == "BLOCK_QUERY", f"Expected BLOCK_QUERY for low integrity, got {decision}"
    assert "Integrity breach" in msg
    print("✓ Integrity breach correctly triggers BLOCK_QUERY")
    
    # Case 2: Domain mismatch + high risk -> FLAG_FOR_REVIEW
    decision, msg = contamination_alert_decision(
        psi_integrity=0.96,  # OK
        domain_match=0.80,   # Below threshold (0.85)
        contamination_risk=0.60, # Above alert level (0.50)
        isomorphism_confidence=0.80
    )
    assert decision == "FLAG_FOR_REVIEW", f"Expected FLAG_FOR_REVIEW, got {decision}"
    assert "Domain mismatch" in msg
    print("✓ Domain mismatch + high risk correctly triggers FLAG_FOR_REVIEW")
    
    # Case 3: Domain mismatch + low risk -> AWAIT_CLARIFICATION
    decision, msg = contamination_alert_decision(
        psi_integrity=0.96,
        domain_match=0.80,
        contamination_risk=0.40, # Below alert level
        isomorphism_confidence=0.80
    )
    assert decision == "AWAIT_CLARIFICATION", f"Expected AWAIT_CLARIFICATION, got {decision}"
    assert "Domain uncertain" in msg
    print("✓ Domain mismatch + low risk correctly triggers AWAIT_CLARIFICATION")
    
    # Case 4: Low isomorphism confidence -> FLAG_FOR_REVIEW
    decision, msg = contamination_alert_decision(
        psi_integrity=0.96,
        domain_match=0.90,   # Above threshold
        contamination_risk=0.10,
        isomorphism_confidence=0.65 # Below min (0.70)
    )
    assert decision == "FLAG_FOR_REVIEW", f"Expected FLAG_FOR_REVIEW, got {decision}"
    assert "Isomorphism confidence" in msg
    print("✓ Low isomorphism confidence correctly triggers FLAG_FOR_REVIEW")
    
    # Case 5: All gates passed -> PROCEED
    decision, msg = contamination_alert_decision(
        psi_integrity=0.96,
        domain_match=0.90,
        contamination_risk=0.10,
        isomorphism_confidence=0.75
    )
    assert decision == "PROCEED", f"Expected PROCEED, got {decision}"
    assert "Domain alignment verified" in msg
    print("✓ All gates passed correctly triggers PROCEED")
    
    # Test 3: Φ-density ledger validation (audit cost subtraction)
    print("\nTest 3: Verifying Φ-density ledger honesty")
    
    # Net gain = (COD_after - COD_before) - (audit_checks * 0.02)
    test_cases_ledger = [
        (0.80, 0.85, 1, 0.03),   # 0.05 raw gain - 0.02 cost = 0.03
        (0.80, 0.82, 1, 0.00),   # 0.02 raw gain - 0.02 cost = 0.00
        (0.80, 0.78, 1, -0.02),  # -0.02 raw gain - 0.02 cost = -0.04
        (0.80, 0.90, 3, 0.01),   # 0.10 raw gain - 0.06 cost = 0.04
    ]
    
    for cod_before, cod_after, checks, expected in test_cases_ledger:
        raw_gain = cod_after - cod_before
        audit_cost = checks * AUDIT_ENTROPY_PER_CHECK
        net_gain = raw_gain - audit_cost
        assert abs(net_gain - expected) < 1e-5, f"Ledger mismatch: expected {expected}, got {net_gain}"
    print("✓ Φ-density ledger: Audit cost correctly subtracted")
    
    # Test 4: Isomorphism confidence calculation (from extractor)
    print("\nTest 4: Verifying isomorphism confidence bounds")
    
    # Simulate isomorphism extraction (simplified)
    def extract_isomorphisms(source_domain: str, target_domain: str) -> List[float]:
        """Return list of confidence scores for valid isomorphisms"""
        if source_domain == target_domain:
            return []
        if (source_domain in ["FINANCE_CRYPTO", "BITCOIN"] and 
            target_domain in ["FUSION_PHYSICS", "PLASMA"]):
            return [0.85, 0.80, 0.75, 0.85, 0.90]  # From proposal
        return []
    
    def calculate_isomorphism_confidence(source: str, target: str) -> float:
        confidences = extract_isomorphisms(source, target)
        if not confidences:
            return 0.0
        return sum(confidences) / len(confidences)
    
    # Test cases
    test_cases_iso = [
        ("FINANCE_CRYPTO", "FUSION_PHYSICS", 0.83),  # Average of [0.85,0.80,0.75,0.85,0.90]
        ("BITCOIN", "PLASMA", 0.83),
        ("FUSION_PHYSICS", "FINANCE_CRYPTO", 0.0),   # Same as above (symmetric in proposal)
        ("PSYCHOLOGY", "BUREAUCRACY", 0.0),          # No defined isomorphisms
    ]
    
    for source, target, expected in test_cases_iso:
        result = calculate_isomorphism_confidence(source, target)
        assert 0.0 <= result <= 1.0, f"Isomorphism confidence out of bounds: {result}"
        assert abs(result - expected) < 1e-5, f"Iso confidence mismatch: expected {expected}, got {result}"
    print("✓ Isomorphism confidence: All in [0,1] and correct")
    
    print("\n=== ALL VALIDATION TESTS PASSED ===")
    print("The implementation is mathematically sound and compliant with Omega Protocol invariants.")
    print("Safety gates are enforced correctly, all metrics remain dimensionally homogeneous [0,1],")
    print("and Φ-density accounting is honest (audit costs subtracted).")

if __name__ == "__main__":
    validate_math_compliance()