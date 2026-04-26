# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Compliance Validator for Adversarial Fusion Integrity (v82.0-Ω)
# Validates active integration of Omega Physics Rubric (v26.0) and dimensional consistency

import re
import math

def validate_omega_compliance(cpp_code):
    """
    Validates that the C++ code actively integrates Omega Physics Rubric invariants
    and maintains dimensional compliance for tokamak branch tasks.
    
    Returns:
        dict: Validation results with pass/fail status and specific violations
    """
    results = {
        "covariant_modes": False,
        "psi_coupling_active": False,
        "stiffness_terms_active": False,
        "boundary_conditions": False,
        "entropy_as_driver": False,
        "dimensional_consistency": True,  # Assume true until proven otherwise
        "derivativity_avoidance": True,   # Assume true until proven otherwise
        "violations": [],
        "warnings": []
    }
    
    # Normalize code for analysis (remove comments, extra whitespace)
    code_no_comments = re.sub(r'//.*|/\*[\s\S]*?\*/', '', cpp_code)
    code_lines = [line.strip() for line in code_no_comments.split('\n') if line.strip()]
    
    # =============================================================================
    # CHECK 1: COVARIANT MODE DECOMPOSITION (ACTIVE INTEGRATION)
    # =============================================================================
    # Look for phi_N and phi_Delta as SEPARATE state variables in AdversarialFusionState
    state_struct_pattern = r'struct\s+AdversarialFusionState\s*\{[^}]*\}'
    state_struct_match = re.search(state_struct_pattern, cpp_code, re.DOTALL)
    
    if state_struct_match:
        state_block = state_struct_match.group(0)
        # Check for explicit phi_N and phi_Delta declarations
        has_phi_n = re.search(r'double\s+phi_N\s*;', state_block)
        has_phi_delta = re.search(r'double\s+phi_Delta\s*;', state_block)
        
        if has_phi_n and has_phi_delta:
            results["covariant_modes"] = True
        else:
            results["violations"].append("Missing active covariant mode decomposition: Requires both phi_N and phi_Delta as state variables")
    else:
        results["violations"].append("Could not locate AdversarialFusionState struct")
    
    # =============================================================================
    # CHECK 2: PSI-METRIC COUPLING AS ACTIVE FORCE (NOT DECORATIVE)
    # =============================================================================
    # Find psi calculation AND verify it's used in state evolution
    psi_calc_pattern = r'(?:double\s+)?psi\s*=\s*log\s*\(\s*phi_N\s*\+\s*[\d.]+e?[-\+]?\d*\s*\)'
    psi_calc_matches = re.findall(psi_calc_pattern, cpp_code, re.IGNORECASE)
    
    if psi_calc_matches:
        # Check if psi is used in any state update expression (not just calculated)
        psi_usage_pattern = r'psi\s*[\*\/\+\-]\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=+\-*/]|\bstate\.[a-zA-Z_][a-zA-Z0-9_]*\s*[=+\-*/].*psi'
        psi_used_in_update = False
        
        for line in code_lines:
            if re.search(psi_usage_pattern, line, re.IGNORECASE) and 'Operate' in line:
                psi_used_in_update = True
                break
                
            # Also check for psi in risk calculations that feed into state updates
            if re.search(r'psi', line, re.IGNORECASE) and ('risk' in line.lower() or 'integrity' in line.lower()):
                # Verify this risk calculation actually updates state
                if any(keyword in line for keyword in ['state.', '=', '+=', '-=', '*=', '/=']):
                    psi_used_in_update = True
                    break
        
        if psi_used_in_update:
            results["psi_coupling_active"] = True
        else:
            results["violations"].append("Psi-metric coupling is decorative: psi calculated but not actively used in state evolution")
    else:
        results["violations"].append("Missing psi-metric coupling calculation: Requires psi = ln(phi_N + ε)")
    
    # =============================================================================
    # CHECK 3: STIFFNESS TERMS AS ACTIVE STABILITY GOVERNORS
    # =============================================================================
    # Find xi_N and xi_Delta usage in stability/risk calculations that affect state
    xi_pattern = r'xi_[NΔ]'
    xi_matches = re.findall(xi_pattern, cpp_code)
    
    if len(xi_matches) >= 2:  # Found both xi_N and xi_Delta
        # Check if they're used in expressions that influence state updates
        xi_used_in_dynamics = False
        for line in code_lines:
            if re.search(xi_pattern, line) and any(op in line for op in ['=', '+=', '-=', '*=', '/=', '>', '<']):
                # Verify it's not just in a comment or reflection
                if not line.strip().startswith('//') and 'reflection' not in line.lower():
                    xi_used_in_dynamics = True
                    break
        
        if xi_used_in_dynamics:
            results["stiffness_terms_active"] = True
        else:
            results["violations"].append("Stiffness terms (xi_N, xi_Δ) are decorative: present but not actively governing stability")
    else:
        results["violations"].append("Missing stiffness terms: Requires both xi_N and xi_Δ for stability gradients")
    
    # =============================================================================
    # CHECK 4: BOUNDARY CONDITIONS AS STATE TRIGGERS
    # =============================================================================
    # Look for horizon/boundary checks that trigger state transitions
    boundary_keywords = [
        r'Shredding\s+Event',
        r'Informational\s+Freeze',
        r'horizon',
        r'boundary.*threshold',
        r'phi_Delta\s*[>≥]\s*[\d.]+',
        r'phi_Delta\s*[<≤]\s*[\d.]+'
    ]
    
    boundary_triggered = False
    for keyword in boundary_keywords:
        if re.search(keyword, cpp_code, re.IGNORECASE):
            # Check if it's in an active conditional that modifies state
            for line in code_lines:
                if re.search(keyword, line, re.IGNORECASE) and any(op in line for op in ['if', 'while']):
                    # Look for state modification in the same or next few lines
                    line_idx = code_lines.index(line)
                    for i in range(line_idx, min(line_idx+5, len(code_lines))):
                        if re.search(r'state\.[a-zA-Z_][a-zA-Z0-9_]*\s*[=+\-*/]', code_lines[i]):
                            boundary_triggered = True
                            break
                    if boundary_triggered:
                        break
            if boundary_triggered:
                break
    
    if boundary_triggered:
        results["boundary_conditions"] = True
    else:
        results["violations"].append("Missing active boundary conditions: Requires horizon triggers (Shredding Event/Informational Freeze) that modify state")
    
    # =============================================================================
    # CHECK 5: ENTROPY AS STATE VARIABLE DRIVER (NOT JUST PENALTY)
    # =============================================================================
    # Find Shannon entropy calculation AND verify it drives state transitions
    entropy_pattern = r'entropy\s*=\s*-.*\*log\s*\(.*\)\s*\+\s*.*\*log\s*\(.*\)'
    entropy_matches = re.findall(entropy_pattern, cpp_code, re.IGNORECASE)
    
    if entropy_matches:
        # Check if entropy is used in state update (not just in a penalty/exponential)
        entropy_used_as_driver = False
        for line in code_lines:
            if 'entropy' in line.lower() and any(op in line for op in ['=', '+=', '-=', '*=', '/=']):
                # Verify it's not just in an exponential penalty like exp(-k*entropy)
                if not re.search(r'exp\s*\([^)]*entropy', line, re.IGNORECASE):
                    entropy_used_as_driver = True
                    break
        
        if entropy_used_as_driver:
            results["entropy_as_driver"] = True
        else:
            results["violations"].append("Entropy is decorative: calculated but not used as state variable driver")
    else:
        results["violations"].append("Missing entropy calculation: Requires Shannon entropy as state variable driver")
    
    # =============================================================================
    # CHECK 6: DIMENSIONAL CONSISTENCY (NO LOG2 VIOLATIONS)
    # =============================================================================
    # Check for illegal log2() on metrics that should be in [0,1]
    illegal_log2_patterns = [
        r'log2\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\s*[+\-*/]\s*[a-zA-Z_][a-zA-Z0-9_]*\s*)*\)',
        r'log\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\s*[+\-*/]\s*[a-zA-Z_][a-zA-Z0-9_]*\s*)*\)\s*/\s*log\s*\(\s*2\s*\)'
    ]
    
    for pattern in illegal_log2_patterns:
        if re.search(pattern, cpp_code):
            results["dimensional_consistency"] = False
            results["violations"].append("Dimensional violation: Illegal log2() transform on metric that must remain [0,1]")
            break
    
    # =============================================================================
    # CHECK 7: DERIVATIVITY AVOIDANCE (NO SIMPLE REPLICATION OF V81.0)
    # =============================================================================
    # Check for adversarial integrity metrics that are NOT in v81.0
    v81_metrics = ['fusion_fidelity', 'mode_preservation', 'conservative_bound_compliance']
    v82_metrics = ['fusion_integrity_index', 'adversarial_surface', 'anomaly_score', 
                   'tampering_probability', 'verification_efficacy', 'weight_manipulation_risk', 
                   'mode_injection_risk']
    
    v81_found = any(metric in cpp_code for metric in v81_metrics)
    v82_found = any(metric in cpp_code for metric in v82_metrics)
    
    if v81_found and not v82_found:
        results["derivativity_avoidance"] = False
        results["violations"].append("Derivativity violation: Appears to replicate v81.0 without adversarial integrity extension")
    elif v81_found and v82_found:
        # Check if v82 metrics are actually used (not just declared)
        v82_used = False
        for metric in v82_metrics:
            if re.search(rf'{metric}\s*[=+\-*/]', cpp_code) or re.search(rf'state\.{metric}', cpp_code):
                v82_used = True
                break
        
        if not v82_used:
            results["derivativity_avoidance"] = False
            results["violations"].append("Derivativity risk: v82.0 metrics declared but not actively used in integrity calculations")
    
    # =============================================================================
    # FINAL ASSESSMENT
    # =============================================================================
    all_checks_passed = all([
        results["covariant_modes"],
        results["psi_coupling_active"],
        results["stiffness_terms_active"],
        results["boundary_conditions"],
        results["entropy_as_driver"],
        results["dimensional_consistency"],
        results["derivativity_avoidance"]
    ])
    
    results["overall_compliant"] = all_checks_passed
    results["phi_density_impact"] = 0.38 if all_checks_passed else 0.00  # Honest accounting
    
    return results

# Example usage (in actual VM, cpp_code would be the user's submitted solution)
# validation_result = validate_omega_compliance(cpp_code)
# print(f"Compliant: {validation_result['overall_compliant']}")
# print(f"Φ-Density Impact: {validation_result['phi_density_impact']}Φ")
# for violation in validation_result['violations']:
#     print(f"VIOLATION: {violation}")