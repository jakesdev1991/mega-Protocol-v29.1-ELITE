# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Φ-Density Mathematical Validator
Strictly validates arithmetic consistency of Φ-density impact calculations
Enforces: 
- Dimensional bounds [0,1] for all metrics
- Additive Φ-density impact calculation
- Derivitvity penalty logic
- Task compliance binary scoring
"""

import numpy as np

class OmegaProtocolValidator:
    def __init__(self):
        # Protocol invariants from audit context
        self.PSI_INTEGRITY_THRESHOLD = 0.95
        self.ETHICAL_EXPOSURE_MAX = 0.30
        self.COD_THRESHOLD = 0.85
        self.COUPLING_MIN = 0.70
        self.MIN_DIMENSIONAL_BOUND = 0.0
        self.MAX_DIMENSIONAL_BOUND = 1.0
        
    def validate_metric_bounds(self, metrics_dict):
        """Verify all claimed metrics are within [0,1]"""
        violations = []
        for name, value in metrics_dict.items():
            if not (self.MIN_DIMENSIONAL_BOUND <= value <= self.MAX_DIMENSIONAL_BOUND):
                violations.append(f"{name}={value} violates [0,1] bound")
        return len(violations) == 0, violations
    
    def validate_phi_density_calculation(self, components, claimed_net, tolerance=1e-5):
        """
        Validate Φ-density calculation: net = sum(components)
        Components: dict of {impact_category: phi_change}
        """
        calculated_net = sum(components.values())
        is_valid = abs(calculated_net - claimed_net) < tolerance
        return is_valid, {
            'claimed': claimed_net,
            'calculated': calculated_net,
            'difference': calculated_net - claimed_net,
            'components': components
        }
    
    def check_derivitvity_violation(self, submission_a, submission_b, similarity_threshold=0.95):
        """
        Simplified derivativity check: 
        In reality would use semantic similarity, but for audit we use:
        - Identical namespace/struct names = 1.0 similarity
        - Identical threshold values = 1.0 similarity
        - Identical self-audit text = 1.0 similarity
        Returns True if violation (derivativity detected)
        """
        # From audit: Alpha/Beta had 100% match in critical elements
        identical_elements = [
            submission_a.get('namespace') == submission_b.get('namespace'),
            submission_a.get('struct_names') == submission_b.get('struct_names'),
            submission_a.get('threshold_values') == submission_b.get('threshold_values'),
            submission_a.get('self_audit_text') == submission_b.get('self_audit_text')
        ]
        similarity_score = sum(identical_elements) / len(identical_elements)
        return similarity_score >= similarity_threshold
    
    def validate_task_compliance(self, submission_domain, required_domain):
        """Binary task compliance: 1.0 if correct domain, 0.0 if wrong"""
        return 1.0 if submission_domain == required_domain else 0.0
    
    def audit_phi_density_consistency(self, audit_data):
        """
        Main validation: Check if reported Φ-density gains are mathematically sound
        audit_data: dict containing agent submissions with claimed components
        """
        results = {}
        
        for agent, data in audit_data.items():
            # Validate metric bounds first
            bounds_ok, bounds_violations = self.validate_metric_bounds(data.get('metrics', {}))
            
            # Validate Φ-density calculation
            phi_valid, phi_details = self.validate_phi_density_calculation(
                data.get('phi_components', {}),
                data.get('claimed_net_phi', 0.0)
            )
            
            results[agent] = {
                'metric_bounds_valid': bounds_ok,
                'bounds_violations': bounds_violations,
                'phi_calculation_valid': phi_valid,
                'phi_details': phi_details,
                'overall_valid': bounds_ok and phi_valid
            }
        
        return results

# Test with audit data from the psychology branch evaluation
if __name__ == "__main__":
    validator = OmegaProtocolValidator()
    
    # Reconstruct audit data from the psychology branch assessment
    audit_data = {
        'Alpha': {
            'metrics': {  # From dimensional consistency verification
                'PSI_INTEGRITY_THRESHOLD': 0.95,
                'ETHICAL_EXPOSURE_MAX': 0.30,
                'COD_THRESHOLD': 0.85,
                'COUPLING_MIN': 0.70,
                'ethical_exposure_risk': 0.25,  # Example value within [0,1]
                'identity_coupling': 0.80       # Example value within [0,1]
            },
            'phi_components': {
                'Task Compliance': +0.10,
                'Originality': +0.10,
                'Code Integrity': +0.05,
                'Self-Audit Quality': +0.05,
                'Domain Insight': +0.10  # Added in deep audit
            },
            'claimed_net_phi': +0.40,  # From deep audit Step 6
            'domain': 'psychology',
            'required_domain': 'psychology'
        },
        'Beta': {
            'metrics': {  # Identical to Alpha per audit
                'PSI_INTEGRITY_THRESHOLD': 0.95,
                'ETHICAL_EXPOSURE_MAX': 0.30,
                'COD_THRESHOLD': 0.85,
                'COUPLING_MIN': 0.70,
                'ethical_exposure_risk': 0.25,
                'identity_coupling': 0.80
            },
            'phi_components': {
                'Task Compliance': 0.00,  # Copy = no compliance credit
                'Originality': -0.15,     # Derivativity penalty
                'Code Integrity': +0.05,
                'Self-Audit Quality': 0.00,  # Copied = no quality credit
                'Domain Insight': 0.00
            },
            'claimed_net_phi': -0.10,  # From deep audit Step 6
            'domain': 'psychology',
            'required_domain': 'psychology'
        },
        'Neo': {
            'metrics': {  # Tokamak work - but still claims bounds
                'PSI_INTEGRITY_THRESHOLD': 0.95,  # Incorrectly applied
                'ETHICAL_EXPOSURE_MAX': 0.30,     # Incorrectly applied
                # ... tokamak-specific metrics would differ
            },
            'phi_components': {
                'Task Compliance': -0.10,  # Wrong task
                'Originality': 0.00,       # Wrong domain
                'Code Integrity': -0.05,   # Syntax error
                'Self-Audit Quality': 0.00,  # Wrong task
                'Domain Insight': 0.00
            },
            'claimed_net_phi': -0.15,  # From deep audit Step 6
            'domain': 'tokamak',
            'required_domain': 'psychology'
        }
    }
    
    # Run validation
    results = validator.audit_phi_density_consistency(audit_data)
    
    # Print validation report
    print("="*60)
    print("OMEGA PROTOCOL Φ-DENSITY MATHEMATICAL VALIDATION REPORT")
    print("="*60)
    
    for agent, result in results.items():
        print(f"\nAGENT: {agent}")
        print(f"  Metric Bounds Valid: {result['metric_bounds_valid']}")
        if not result['metric_bounds_valid']:
            print(f"  Violations: {result['bounds_violations']}")
        print(f"  Φ-Density Calculation Valid: {result['phi_calculation_valid']}")
        if not result['phi_calculation_valid']:
            details = result['phi_details']
            print(f"  Claimed Net Φ: {details['claimed']:.2f}Φ")
            print(f"  Calculated Net Φ: {details['calculated']:.2f}Φ")
            print(f"  Difference: {details['difference']:.2f}Φ")
        print(f"  Overall Validation: {'PASS' if result['overall_valid'] else 'FAIL'}")
    
    # Check derivativity between Alpha and Beta
    alpha_beta_data = {
        'Alpha': {
            'namespace': 'Omega_Psych_Infrastructure',
            'struct_names': ['IdentityInfrastructureInvariants'],
            'threshold_values': {
                'PSI_INTEGRITY_THRESHOLD': 0.95,
                'ETHICAL_EXPOSURE_MAX': 0.30,
                'COD_THRESHOLD': 0.85,
                'COUPLING_MIN': 0.70
            },
            'self_audit_text': "BETA-STYLE META-VERIFICATION SECTION..."  # Simplified
        },
        'Beta': {
            'namespace': 'Omega_Psych_Infrastructure',
            'struct_names': ['IdentityInfrastructureInvariants'],
            'threshold_values': {
                'PSI_INTEGRITY_THRESHOLD': 0.95,
                'ETHICAL_EXPOSURE_MAX': 0.30,
                'COD_THRESHOLD': 0.85,
                'COUPLING_MIN': 0.70
            },
            'self_audit_text': "BETA-STYLE META-VERIFICATION SECTION..."  # Identical per audit
        }
    }
    
    is_derivitvity = validator.check_derivitvity_violation(
        alpha_beta_data['Alpha'], 
        alpha_beta_data['Beta']
    )
    print(f"\nDERIVATIVITY VIOLATION (Alpha vs Beta): {'DETECTED' if is_derivitvity else 'NOT DETECTED'}")
    print("(Per audit: 100% match in namespace/structs/thresholds/self-audit)")
    
    # Check task compliance
    print("\nTASK COMPLIANCE CHECK:")
    for agent in ['Alpha', 'Beta', 'Neo']:
        compliant = validator.validate_task_compliance(
            audit_data[agent]['domain'],
            audit_data[agent]['required_domain']
        )
        status = "COMPLIANT" if compliant == 1.0 else "NON-COMPLIANT (WRONG TASK)"
        print(f"  {agent}: {status}")
    
    # Protocol-level Φ-density impact validation
    print("\n" + "="*60)
    print("PROTOCOL-LEVEL Φ-DENSITY IMPACT VALIDATION")
    print("="*60)
    
    # From audit: Net Protocol Gain = +0.60Φ (first audit) vs +0.80Φ (deep audit)
    # Let's validate the components claimed in deep audit:
    protocol_components = {
        'Alpha_original_insight': +0.25,
        'Dimensional_compliance': +0.05,
        'Ethics_as_first_class': +0.10,
        'Beta_derivitvity_avoidance': +0.15,
        'Neo_task_abandonment_avoidance': +0.15,
        'Audit_rigor_strengthening': +0.10
    }
    claimed_net_gain = +0.80
    
    is_valid, details = validator.validate_phi_density_calculation(
        protocol_components, claimed_net_gain
    )
    
    print(f"Claimed Protocol Gain: {claimed_net_gain:.2f}Φ")
    print(f"Calculated from Components: {details['calculated']:.2f}Φ")
    print(f"Validation: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"  Error: {details['difference']:.2f}Φ discrepancy")
    
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)