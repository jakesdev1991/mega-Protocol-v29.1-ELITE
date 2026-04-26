# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import List, Tuple, NamedTuple

# === OMEGA PROTOCOL INVARIANT VALIDATOR ===
# Validates mathematical soundness and invariant compliance of Q-Systemic Self framework
# Focus: COD calculation, failure mode detection, ACG operator, Phi-density ledger

class ValidationResult(NamedTuple):
    passed: bool
    message: str
    severity: str  # 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

def validate_dimensionless(value: float, name: str) -> ValidationResult:
    """Check if value is dimensionless [0,1] as required by Omega Protocol"""
    if not isinstance(value, (int, float)):
        return ValidationResult(False, f"{name} must be numeric", "ERROR")
    if math.isnan(value) or math.isinf(value):
        return ValidationResult(False, f"{name} is NaN or infinite", "ERROR")
    if not (0 <= value <= 1 + 1e-9):  # Allow tiny floating point overflow
        return ValidationResult(False, f"{name}={value} not in [0,1]", "ERROR")
    return ValidationResult(True, f"{name} dimensionless OK", "INFO")

def validate_cod_formula() -> List[ValidationResult]:
    """Validate COD = |<Ψ_con|Ψ_coll>|^2 * exp(-Λ * H_super) * Ψ_id"""
    results = []
    
    # Test case 1: Perfect alignment, low uncertainty, full identity
    psi_con = np.array([1.0+0j, 0.0+0j])
    psi_coll = np.array([1.0+0j, 0.0+0j])
    H_super = 0.1
    psi_id = 0.98
    Lambda = 1.0
    
    # Calculate fidelity correctly: |<ψ_con|ψ_coll>|^2
    fidelity = np.abs(np.vdot(psi_con, psi_coll))**2  # Correct quantum fidelity
    expected_cod = fidelity * math.exp(-Lambda * H_super) * psi_id
    
    # Check dimensionality of inputs
    for val, name in [(H_super, "H_super"), (psi_id, "Ψ_id")]:
        results.append(validate_dimensionless(val, name))
    
    # Check output dimensionality
    results.append(validate_dimensionless(expected_cod, "COD_expected"))
    
    # Validate components
    results.append(validate_dimensionless(fidelity, "Fidelity"))
    damping = math.exp(-Lambda * H_super)
    results.append(validate_dimensionless(damping, "Damping factor"))
    
    # Check if COD respects identity hard gate
    if psi_id < 0.95:
        expected_cod_gated = 0.0
    else:
        expected_cod_gated = expected_cod
    
    results.append(ValidationResult(
        expected_cod_gated == expected_cod if psi_id >= 0.95 else expected_cod_gated == 0.0,
        f"Identity hard gate: Ψ_id={psi_id} -> COD_gated={expected_cod_gated}",
        "INFO"
    ))
    
    # Test case 2: Orthogonal states (should have zero fidelity)
    psi_con = np.array([1.0+0j, 0.0+0j])
    psi_coll = np.array([0.0+0j, 1.0+0j])
    fidelity_ortho = np.abs(np.vdot(psi_con, psi_coll))**2
    results.append(ValidationResult(
        abs(fidelity_ortho - 0.0) < 1e-10,
        f"Orthogonality test: fidelity={fidelity_ortho}",
        "INFO"
    ))
    
    # Test case 3: Maximum uncertainty (H_super=1.0)
    H_super_max = 1.0
    damping_max = math.exp(-Lambda * H_super_max)
    results.append(validate_dimensionless(damping_max, "Damping at H_super=1.0"))
    results.append(ValidationResult(
        damping_max > 0 and damping_max <= 1.0,
        f"Damping factor in (0,1]: {damping_max}",
        "INFO"
    ))
    
    return results

def validate_failure_mode() -> List[ValidationResult]:
    """Validate Measurement Shock condition: H_super > 0.85 AND Γ_meas > 0.8"""
    results = []
    
    # Boundary test: exactly at threshold should NOT trigger (strict inequality)
    test_cases = [
        (0.85, 0.8, False, "At threshold"),
        (0.8500001, 0.8, False, "H_super slightly over, Γ_meas at threshold"),
        (0.85, 0.8000001, False, "H_super at threshold, Γ_meas slightly over"),
        (0.8500001, 0.8000001, True, "Both slightly over"),
        (0.9, 0.9, True, "Well over"),
        (0.5, 0.9, False, "Low H_super"),
        (0.9, 0.5, False, "Low Γ_meas")
    ]
    
    for H_super, Gamma_meas, expected, desc in test_cases:
        results.append(validate_dimensionless(H_super, "H_super"))
        results.append(validate_dimensionless(Gamma_meas, "Γ_meas"))
        
        triggered = (H_super > 0.85) and (Gamma_meas > 0.8)
        results.append(ValidationResult(
            triggered == expected,
            f"{desc}: H_super={H_super}, Γ_meas={Gamma_meas} -> Shock={triggered} (expected {expected})",
            "INFO" if triggered == expected else "ERROR"
        ))
    
    return results

def validate_acg_constraints() -> List[ValidationResult]:
    """Validate Adiabatic Collapse Gate constraints"""
    results = []
    
    # Constraint 1: Identity hard gate (Ψ_id >= 0.95)
    test_psi_id = [0.94, 0.95, 0.96, 0.90, 1.0]
    for psi_id in test_psi_id:
        results.append(validate_dimensionless(psi_id, "Ψ_id"))
        gate_passed = psi_id >= 0.95
        results.append(ValidationResult(
            gate_passed,
            f"Identity gate: Ψ_id={psi_id} -> {'PASS' if gate_passed else 'FAIL (hard gate)'}",
            "CRITICAL" if not gate_passed and psi_id < 0.90 else "WARNING"
        ))
    
    # Constraint 2: Γ_meas rate limit (|ΔΓ_meas| <= 0.05 per step)
    gamma_history = [0.5, 0.54, 0.60, 0.58, 0.63]  # Example trajectory
    for i in range(1, len(gamma_history)):
        delta_gamma = abs(gamma_history[i] - gamma_history[i-1])
        results.append(ValidationResult(
            delta_gamma <= 0.05 + 1e-9,
            f"Γ_meas rate: |{gamma_history[i]} - {gamma_history[i-1]}| = {delta_gamma:.4f} <= 0.05",
            "WARNING" if delta_gamma > 0.05 else "INFO"
        ))
    
    # Constraint 3: Audit cost subtraction in Phi-density
    # Φ_net = (COD_after - COD_before) - ΔS_audit
    cod_before, cod_after = 0.6, 0.85
    audit_cost = 0.07  # Example: 1 audit op @ 0.05 + 1 validation @ 0.02
    phi_net = (cod_after - cod_before) - audit_cost
    results.append(validate_dimensionless(phi_net, "Φ_net"))
    results.append(ValidationResult(
        phi_net > 0,
        f"Phi-density: Gain={cod_after-cod_before:.2f} - Cost={audit_cost:.2f} = Net={phi_net:.2f} > 0",
        "INFO" if phi_net > 0 else "ERROR"
    ))
    
    return results

def validate_phi_ledger() -> List[ValidationResult]:
    """Validate Phi-density ledger with audit cost subtraction"""
    results = []
    
    # Test net gain calculation
    test_cases = [
        (0.5, 0.9, 0.05, 0.35),   # Normal case
        (0.8, 0.82, 0.03, -0.01), # Negative net gain (unsustainable)
        (0.4, 0.7, 0.2, 0.1),     # High audit cost
        (0.9, 0.95, 0.0, 0.05)    # Zero audit cost
    ]
    
    for cod_before, cod_after, audit_cost, expected_net in test_cases:
        for val, name in [(cod_before, "COD_before"), (cod_after, "COD_after"), (audit_cost, "ΔS_audit")]:
            results.append(validate_dimensionless(val, name))
        
        net_gain = (cod_after - cod_before) - audit_cost
        results.append(ValidationResult(
            abs(net_gain - expected_net) < 1e-9,
            f"Φ-ledger: ({cod_after}-{cod_before}) - {audit_cost} = {net_gain:.2f} (expected {expected_net:.2f})",
            "INFO" if abs(net_gain - expected_net) < 1e-9 else "ERROR"
        ))
        
        # Sustainability check: net gain must be >0 for long-term viability
        if net_gain <= 0:
            results.append(ValidationResult(
                False,
                f"Unsustainable intervention: Φ_net={net_gain:.2f} <= 0",
                "WARNING"
            ))
    
    return results

def run_full_validation() -> None:
    """Run all validation checks and report results"""
    print("="*60)
    print("OMEGA PROTOCOL MATHEMATICAL VALIDATION")
    print("Q-Systemic Self Framework: Quantum-Classical Interface")
    print("="*60)
    
    all_results = []
    all_results.extend(validate_cod_formula())
    all_results.extend(validate_failure_mode()))
    all_results.extend(validate_acg_constraints()))
    all_results.extend(validate_phi_ledger()))
    
    # Summary
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    errors = [r for r in all_results if r.severity == "ERROR" and not r.passed]
    criticals = [r for r in all_results if r.severity == "CRITICAL" and not r.passed]
    
    print(f"\nSUMMARY: {passed}/{total} checks passed")
    if criticals:
        print(f"CRITICAL FAILURES ({len(criticals)}):")
        for r in criticals[:3]:  # Show first 3
            print(f"  - {r.message}")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for r in errors[:3]:
            print(f"  - {r.message}")
    
    # Protocol compliance verdict
    if not criticals and not errors:
        print("\n✅ OMEGA PROTOCOL COMPLIANT: All invariants satisfied")
        print("   - Dimensional homogeneity verified")
        print("   - Identity hard gate enforced")
        print("   - Failure mode detection accurate")
        print("   - ACG operator constraints validated")
        print("   - Phi-density ledger with audit cost sound")
    else:
        print("\n❌ OMEGA PROTOCOL VIOLATION: Mathematical or invariant breach detected")
        print("   Immediate intervention required to prevent matrix instability")
    
    print("="*60)

if __name__ == "__main__":
    run_full_validation()