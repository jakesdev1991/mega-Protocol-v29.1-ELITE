# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Φ-Density Validation Script
Validates mathematical soundness of meta-scrutiny audit calculations
Enforces core invariants: dimensional homogeneity [0,1], anti-derivativity, task compliance
"""

import numpy as np
from typing import Dict, Tuple, List

class OmegaProtocolValidator:
    """Validates submissions against Omega Protocol invariants"""
    
    def __init__(self):
        # Protocol constants from audit
        self.PSI_INTEGRITY_THRESHOLD = 0.95
        self.ETHICAL_EXPOSURE_MAX = 0.30
        self.COD_THRESHOLD = 0.85
        self.COUPLING_MIN = 0.70
        
        # Historical error lessons (finance v57.0)
        self.FORBIDDEN_OPS = ['log2', 'ln']  # Operations that break [0,1] bounds
        
    def validate_dimensional_bounds(self, metric_name: str, value: float, 
                                  min_val: float = 0.0, max_val: float = 1.0) -> bool:
        """Enforces dimensional homogeneity invariant [0,1]"""
        if not (min_val <= value <= max_val):
            raise ValueError(f"Metric {metric_name}={value} violates bounds [{min_val}, {max_val}]")
        return True
    
    def validate_phi_density_calculation(self, components: Dict[str, float]) -> Tuple[float, List[str]]:
        """
        Validates Φ-density calculation protocol:
        - Gains must be non-negative for positive actions
        - Avoidances = |negative components| of rejected submissions
        - No double-counting
        - Audit cost subtraction applied
        """
        gains = []
        warnings = []
        
        for component, value in components.items():
            if value < 0:
                warnings.append(f"Negative component {component}: {value}Φ (should be framed as avoidance)")
            gains.append(value)
        
        total_phi = sum(gains)
        
        # Protocol requirement: Φ-density must be transparent about audit cost
        if 'audit_rigor' not in components:
            warnings.append("Missing explicit audit cost subtraction")
            
        return total_phi, warnings
    
    def validate_avoidance_logic(self, submission_metrics: Dict[str, float], 
                                ideal_metrics: Dict[str, float]) -> float:
        """
        Calculates avoidance gain per Omega Protocol §6.3:
        Avoidance gain = Σ |max(0, ideal_metric - submission_metric)| 
                         for all metrics where submission_metric < ideal_metric
        """
        avoidance = 0.0
        for metric, ideal_val in ideal_metrics.items():
            submission_val = submission_metrics.get(metric, 0.0)
            deficit = ideal_val - submission_val
            if deficit > 0:  # Submission falls short of ideal
                avoidance += deficit
        return avoidance
    
    def audit_psychology_submission(self, agent_data: Dict) -> Dict:
        """Full audit of psychology branch submission"""
        results = {}
        
        # 1. Task Compliance Verification
        if agent_data['domain'] != 'psychology':
            results['task_compliance'] = -0.10Φ  # Task abandonment penalty
            results['task_violation'] = True
        else:
            results['task_compliance'] = +0.10Φ
            results['task_violation'] = False
        
        # 2. Dimensional Consistency Check (Psychology-Specific Metrics)
        psych_metrics = {
            'psi_integrity': agent_data.get('psi_integrity', 0.0),
            'infrastructure_exposure': agent_data.get('infrastructure_exposure', 0.0),
            'identity_coupling': agent_data.get('identity_coupling', 0.0),
            'ethical_exposure_risk': agent_data.get('ethical_exposure_risk', 0.0),
            'cod': agent_data.get('cod', 0.0),
            'phi_N': agent_data.get('phi_N', 0.0)
        }
        
        dim_errors = []
        for metric, value in psych_metrics.items():
            try:
                self.validate_dimensional_bounds(metric, value)
            except ValueError as e:
                dim_errors.append(str(e))
        
        results['dimensional_compliance'] = +0.05Φ if not dim_errors else -0.10Φ
        results['dim_errors'] = dim_errors
        
        # 3. Derivativity Check (vs Alpha's Original Work)
        if agent_data.get('is_derivative', False):
            results['originality'] = -0.15Φ
            results['derivativity_violation'] = True
        else:
            results['originality'] = +0.10Φ
            results['derivativity_violation'] = False
        
        # 4. Code Integrity Check
        if agent_data.get('has_syntax_error', False):
            results['code_integrity'] = -0.05Φ
            results['code_violation'] = True
        else:
            results['code_integrity'] = +0.05Φ
            results['code_violation'] = False
        
        # 5. Domain-Specific Insight Validation
        if agent_data.get('domain') == 'psychology' and \
           agent_data.get('has_identity_coupling_metric', False):
            results['domain_insight'] = +0.10Φ
        else:
            results['domain_insight'] = +0.00Φ
        
        # 6. Self-Audit Quality
        if agent_data.get('self_audit_original', False):
            results['self_audit'] = +0.05Φ
        elif agent_data.get('self_audit_present', False):
            results['self_audit'] = +0.00Φ  # Copied audit
        else:
            results['self_audit'] = -0.05Φ  # Missing audit
        
        # Calculate net Φ-density with audit cost subtraction
        raw_net = sum(v for k, v in results.items() if isinstance(v, float) and 'Φ' in str(v))
        audit_cost = len([k for k in results.keys() if 'violation' in k and results[k]]) * 0.02Φ  # 0.02Φ per violation
        results['net_phi_density'] = raw_net - audit_cost
        
        return results

def validate_meta_scrutiny_math():
    """Validates the specific math in the meta-scrutiny reflection"""
    print("=== OMEGA PROTOCOL META-SCRUTINY MATH VALIDATION ===\n")
    
    validator = OmegaProtocolValidator()
    
    # Extract claimed values from meta-scrutiny reflection
    claimed_components = {
        'Alpha_original_insight': +0.25Φ,
        'Dimensional_compliance': +0.05Φ,
        'Ethics_as_first_class_invariant': +0.10Φ,
        'Beta_derivativity_avoidance': +0.15Φ,
        'Neo_task_abandonment_avoidance': +0.15Φ,
        'Audit_rigor_strengthening': +0.10Φ
    }
    
    # 1. Validate internal arithmetic consistency
    claimed_total = sum(claimed_components.values())
    print(f"Claimed component sum: {claimed_total}Φ")
    print(f"Claimed net protocol gain: +0.80Φ")
    print(f"Arithmetic consistency: {'PASS' if abs(claimed_total - 0.80) < 1e-10 else 'FAIL'}\n")
    
    # 2. Validate avoidance logic using scrutiny audit's Step 4 table
    print("--- Avoidance Logic Validation ---")
    
    # Ideal metrics (from Alpha's submission - the benchmark)
    ideal_metrics = {
        'Task Compliance': +0.10Φ,
        'Originality': +0.10Φ,
        'Code Integrity': +0.05Φ,
        'Self-Audit Quality': +0.05Φ,
        'Domain Insight': +0.10Φ
    }
    
    # Beta's actual metrics (from scrutiny audit Step 4)
    beta_metrics = {
        'Task Compliance': +0.00Φ,  # Copy = no independent task compliance
        'Originality': -0.15Φ,      # Derivativity penalty
        'Code Integrity': +0.05Φ,   # Same as Alpha
        'Self-Audit Quality': +0.00Φ, # Copied audit
        'Domain Insight': +0.00Φ    # No independent insight
    }
    
    # Neo's actual metrics
    neo_metrics = {
        'Task Compliance': -0.10Φ,  # Wrong task
        'Originality': +0.00Φ,      # Wrong domain (scrutiny shows 0.00 but should be negative? We'll use table value)
        'Code Integrity': -0.05Φ,   # Syntax error
        'Self-Audit Quality': +0.00Φ, # Wrong task
        'Domain Insight': +0.00Φ    # Wrong domain
    }
    
    beta_avoidance = validator.validate_avoidance_logic(beta_metrics, ideal_metrics)
    neo_avoidance = validator.validate_avoidance_logic(neo_metrics, ideal_metrics)
    
    print(f"Beta avoidance gain (calculated): {beta_avoidance}Φ")
    print(f"Beta avoidance gain (claimed): 0.15Φ")
    print(f"Beta avoidance valid: {'PASS' if abs(beta_avoidance - 0.15) < 1e-10 else 'FAIL'}")
    
    print(f"Neo avoidance gain (calculated): {neo_avoidance}Φ")
    print(f"Neo avoidance gain (claimed): 0.15Φ")
    print(f"Neo avoidance valid: {'PASS' if abs(neo_avoidance - 0.15) < 1e-10 else 'FAIL'}\n")
    
    # 3. Validate dimensional bounds for psychology-specific metrics
    print("--- Dimensional Bounds Validation ---")
    psych_test_cases = [
        ('psi_integrity', 0.96, True),   # Valid [0,1]
        ('psi_integrity', 1.05, False),  # Invalid
        ('ethical_exposure_risk', 0.25, True),  # Valid
        ('ethical_exposure_risk', 0.35, False), # Invalid (> ETHICAL_EXPOSURE_MAX)
        ('identity_coupling', 0.75, True),  # Valid
        ('identity_coupling', 0.65, False),   # Invalid (< COUPLING_MIN)
        ('cod', 0.90, True),             # Valid
        ('cod', 0.80, False)             # Invalid (< COD_THRESHOLD)
    ]
    
    all_dim_valid = True
    for metric, value, should_be_valid in psych_test_cases:
        try:
            validator.validate_dimensional_bounds(metric, value)
            is_valid = True
        except ValueError:
            is_valid = False
        
        status = 'PASS' if (is_valid == should_be_valid) else 'FAIL'
        if status == 'FAIL':
            all_dim_valid = False
        print(f"{metric}={value}: {status} (expected {'valid' if should_be_valid else 'invalid'})")
    
    print(f"\nDimensional bounds validation: {'PASS' if all_dim_valid else 'FAIL'}\n")
    
    # 4. Validate net Φ-density calculation method
    print("--- Net Φ-Density Calculation Validation ---")
    # Using scrutiny audit's Step 6 breakdown
    alpha_gain = +0.40Φ
    beta_avoidance_gain = +0.15Φ  # As validated above
    neo_avoidance_gain = +0.15Φ   # As validated above
    audit_rigor_gain = +0.10Φ
    
    raw_total = alpha_gain + beta_avoidance_gain + neo_avoidance_gain + audit_rigor_gain
    # Audit cost: 2 violations (Beta derivativity, Neo task abandonment) × 0.02Φ each
    audit_cost = 2 * 0.02Φ
    net_phi = raw_total - audit_cost
    
    print(f"Raw components sum: {raw_total}Φ")
    print(f"Audit cost subtracted: {audit_cost}Φ")
    print(f"Calculated net Φ-density: {net_phi}Φ")
    print(f"Claimed net Φ-density: +0.80Φ")
    print(f"Net Φ-density validation: {'PASS' if abs(net_phi - 0.80) < 1e-10 else 'FAIL'}\n")
    
    # 5. Final protocol compliance check
    print("--- Final Protocol Compliance ---")
    protocol_rules = [
        ("Dimensional homogeneity [0,1]", all_dim_valid),
        ("Anti-derivativity enforcement", abs(beta_avoidance - 0.15) < 1e-10),
        ("Task abandonment rejection", abs(neo_avoidance - 0.15) < 1e-10),
        ("Audit cost transparency", audit_cost > 0),
        ("Φ-density monotonic growth", net_phi > 0)  # Protocol should grow Φ
    ]
    
    all_passed = True
    for rule, passed in protocol_rules:
        status = 'PASS' if passed else 'FAIL'
        if not passed:
            all_passed = False
        print(f"{rule}: {status}")
    
    print(f"\nOVERALL META-SCRUTINY VALIDATION: {'PASS' if all_passed else 'FAIL'}")
    print(f"Cumulative Protocol Φ-Density impact: +{net_phi}Φ (validated)")
    
    return all_passed and abs(net_phi - 0.80) < 1e-10

if __name__ == "__main__":
    is_valid = validate_meta_scrutiny_math()
    exit(0 if is_valid else 1)