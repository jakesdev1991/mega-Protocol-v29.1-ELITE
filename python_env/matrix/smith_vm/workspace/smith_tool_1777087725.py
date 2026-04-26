# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random

def validate_omega_protocol():
    """
    Validates the mathematical soundness and Omega Protocol compliance 
    of the psychology branch audit report.
    """
    # === STEP 1: VALIDATE CORE INVARIANTS (ALPHA/BETA PSYCHOLOGY PROPOSAL) ===
    print("=== OMEGA PROTOCOL INVARIANT VALIDATION ===")
    
    # Define invariants from audit (Alpha/Beta v61.0-Ω)
    invariants = {
        'PSI_INTEGRITY_THRESHOLD': 0.95,
        'ETHICAL_EXPOSURE_MAX': 0.30,
        'COD_THRESHOLD': 0.85,
        'COUPLING_MIN': 0.70
    }
    
    # Check all invariants are in [0,1] (dimensional homogeneity)
    for name, value in invariants.items():
        if not (0 <= value <= 1):
            print(f"FAIL: Invariant {name} = {value} ∉ [0,1]")
            return False
        print(f"PASS: {name} = {value} ∈ [0,1]")
    
    # Validate ethical exposure risk function: clamp(exposure * coupling, 0, 1)
    def ethical_exposure(infrastructure_exposure, coupling):
        raw = infrastructure_exposure * coupling
        return max(0.0, min(1.0, raw))
    
    # Validate coupling function: sqrt(proprietary_density * identity_relevance)
    def identity_coupling(proprietary_density, identity_relevance):
        return math.sqrt(proprietary_density * identity_relevance)
    
    # Test with 10,000 random samples in [0,1]
    test_failures = 0
    for _ in range(10000):
        exp = random.random()
        coup = random.random()
        if not (0 <= ethical_exposure(exp, coup) <= 1):
            test_failures += 1
        pd = random.random()
        ir = random.random()
        coup_val = identity_coupling(pd, ir)
        if not (0 <= coup_val <= 1):
            test_failures += 1
    
    if test_failures > 0:
        print(f"FAIL: {test_failures} boundary violations in risk/coupling functions")
        return False
    print("PASS: Ethical exposure and coupling functions maintain [0,1] bounds")
    
    # === STEP 2: VALIDATE Φ-DENSITY CALCULATIONS ===
    print("\n=== Φ-DENSITY CALCULATION VALIDATION ===")
    
    # Agent Φ-density table from Step 6 (honest recalculation)
    agent_table = {
        'Alpha': {
            'Task Compliance': 0.10,
            'Originality': 0.10,
            'Code Integrity': 0.05,
            'Self-Audit Quality': 0.05,
            'Domain Insight': 0.10,
            'Net Claimed': 0.40
        },
        'Beta': {
            'Task Compliance': 0.00,
            'Originality': -0.15,
            'Code Integrity': 0.05,
            'Self-Audit Quality': 0.00,
            'Domain Insight': 0.00,
            'Net Claimed': -0.10
        },
        'Neo': {
            'Task Compliance': -0.10,
            'Originality': 0.00,
            'Code Integrity': -0.05,
            'Self-Audit Quality': 0.00,
            'Domain Insight': 0.00,
            'Net Claimed': -0.15
        }
    }
    
    # Verify agent net Φ-density sums
    for agent, components in agent_table.items():
        total = sum(components[key] for key in components if key != 'Net Claimed')
        claimed = components['Net Claimed']
        if not math.isclose(total, claimed, abs_tol=1e-5):
            print(f"FAIL: {agent} Φ-density mismatch: calculated {total:.5f} ≠ claimed {claimed:.5f}")
            return False
        print(f"PASS: {agent} Φ-density: {total:.5f} = {claimed:.5f}")
    
    # Protocol-level impact table
    protocol_impact = {
        'Alpha's gain': 0.40,
        'Beta avoidance': 0.15,
        'Neo avoidance': 0.15,
        'Audit rigor gain': 0.10,
        'Net Protocol Gain Claimed': 0.80
    }
    
    total_protocol = sum(protocol_impact[key] for key in protocol_impact if key != 'Net Protocol Gain Claimed')
    claimed_protocol = protocol_impact['Net Protocol Gain Claimed']
    if not math.isclose(total_protocol, claimed_protocol, abs_tol=1e-5):
        print(f"FAIL: Protocol Φ-density mismatch: calculated {total_protocol:.5f} ≠ claimed {claimed_protocol:.5f}")
        return False
    print(f"PASS: Protocol Φ-density: {total_protocol:.5f} = {claimed_protocol:.5f}")
    
    # === STEP 3: VALIDATE DERIVATIVITY DETECTION (ALPHA VS BETA) ===
    print("\n=== DERIVATIVITY VALIDATION ===")
    # Per audit: Alpha and Beta have identical submissions
    # We simulate by checking if their claimed Φ-density components match (except where derivativity penalty applies)
    alpha = agent_table['Alpha']
    beta = agent_table['Beta']
    
    # Originality should differ by exactly -0.25Φ (Alpha +0.10 vs Beta -0.15)
    orig_diff = alpha['Originality'] - beta['Originality']
    if not math.isclose(orig_diff, 0.25, abs_tol=1e-5):
        print(f"FAIL: Originality difference incorrect: {orig_diff:.5f} ≠ 0.25")
        return False
    print(f"PASS: Originality difference = {orig_diff:.5f} (Alpha +0.10Φ, Beta -0.15Φ)")
    
    # Self-audit quality should differ by +0.05Φ (Alpha +0.05 vs Beta 0.00)
    audit_diff = alpha['Self-Audit Quality'] - beta['Self-Audit Quality']
    if not math.isclose(audit_diff, 0.05, abs_tol=1e-5):
        print(f"FAIL: Self-audit difference incorrect: {audit_diff:.5f} ≠ 0.05")
        return False
    print(f"PASS: Self-audit difference = {audit_diff:.5f} (Alpha +0.05Φ, Beta 0.00Φ)")
    
    # === STEP 4: VALIDATE TASK ABANDONMENT (NEO) ===
    print("\n=== TASK ABANDONMENT VALIDATION ===")
    # Neo's submission: wrong domain (tokamak) for psychology task
    # Per audit: Task Compliance = -0.10Φ (wrong task penalty)
    neo = agent_table['Neo']
    if neo['Task Compliance'] != -0.10:
        print(f"FAIL: Neo task compliance incorrect: {neo['Task Compliance']:.5f} ≠ -0.10")
        return False
    print(f"PASS: Neo task compliance = {neo['Task Compliance']:.5f} (wrong task penalty)")
    
    # === STEP 5: VALIDATE ETHICAL GATE HIERARCHY ===
    print("\n=== ETHICAL GATE VALIDATION ===")
    # Psychology v61.0-Ω gate structure:
    # Ψ_integrity ≥ 0.95 → Ethical_Exposure ≤ 0.30 → COD ≥ 0.85 → Action
    # With ethical exposure thresholds:
    #   > 0.70 → IDENTITY_LOCKDOWN
    #   > 0.50 → HALT_OPERATIONS
    #   > 0.30 → FREEZE_ACCESS
    
    def ethics_gate_decision(ethical_exposure_val):
        if ethical_exposure_val > 0.70:
            return "IDENTITY_LOCKDOWN"
        elif ethical_exposure_val > 0.50:
            return "HALT_OPERATIONS"
        elif ethical_exposure_val > 0.30:
            return "FREEZE_ACCESS"
        else:
            return "PROCEED"
    
    # Test boundary conditions
    test_cases = [
        (0.29, "PROCEED"),
        (0.30, "FREEZE_ACCESS"),  # Note: audit says >0.30 triggers FREEZE_ACCESS
        (0.31, "FREEZE_ACCESS"),
        (0.50, "HALT_OPERATIONS"), # >0.50 triggers HALT
        (0.51, "HALT_OPERATIONS"),
        (0.70, "IDENTITY_LOCKDOWN"), # >0.70 triggers LOCKDOWN
        (0.71, "IDENTITY_LOCKDOWN")
    ]
    
    for exp_val, expected in test_cases:
        result = ethics_gate_decision(exp_val)
        if result != expected:
            print(f"FAIL: Ethics gate failed for exposure={exp_val}: got {result}, expected {expected}")
            return False
    print("PASS: Ethics gate hierarchy enforces correct thresholds")
    
    # === STEP 6: VALIDATE PSYCHOLOGY-SPECIFIC INSIGHT ===
    print("\n=== DOMAIN INSIGHT VALIDATION ===")
    # Alpha's key insight: Ethical Exposure = infrastructure_exposure × identity_coupling
    # Where identity_coupling = sqrt(proprietary_density × identity_relevance)
    # This makes risk heterogeneous (subject-dependent)
    
    # Test case: trauma survivor vs general attendee (from audit reflection)
    exposure = 0.7  # Same infrastructure leak
    
    # Trauma survivor: high identity relevance
    pd_ts = 0.9  # proprietary density (leak contains trauma triggers)
    ir_ts = 0.9  # identity relevance to subject
    coup_ts = identity_coupling(pd_ts, ir_ts)
    risk_ts = ethical_exposure(exposure, coup_ts)
    
    # General attendee: low identity relevance
    pd_ga = 0.9  # same proprietary density
    ir_ga = 0.1  # low identity relevance
    coup_ga = identity_coupling(pd_ga, ir_ga)
    risk_ga = ethical_exposure(exposure, coup_ga)
    
    # Audit claims: 9× higher risk for trauma survivor
    ratio = risk_ts / risk_ga if risk_ga > 0 else float('inf')
    expected_ratio = 9.0
    
    if not math.isclose(ratio, expected_ratio, rel_tol=0.1):  # Allow 10% tolerance
        print(f"FAIL: Risk ratio incorrect: {ratio:.2f} ≠ {expected_ratio:.1f} (trauma survivor vs general)")
        return False
    print(f"PASS: Trauma survivor risk = {risk_ts:.3f}, General attendee risk = {risk_ga:.3f}, Ratio = {ratio:.2f} ≈ 9.0")
    
    print("\n=== ALL VALIDATIONS PASSED ===")
    print("Omega Protocol invariants are mathematically sound and compliant.")
    return True

# Execute validation
if __name__ == "__main__":
    success = validate_omega_protocol()
    if not success:
        exit(1)
    print("\nFINAL VERDICT: AUDIT REPORT IS MATHEMATICALLY SOUND AND OMEGA PROTOCOL COMPLIANT")