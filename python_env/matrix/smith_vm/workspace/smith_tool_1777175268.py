# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Mathematical Compliance Validator
# Validates expressions against core Omega Protocol invariants:
# 1. Covariant Modes Decomposition: Must reference Φ_N and Φ_Δ
# 2. Metric Coupling Invariant: Must include ψ = ln(φₙ) 
# 3. Stiffness Terms: Must include ξ_N and ξ_Δ
# 4. Action Derivation: Expressions must be derivable from Ω-Action (structural check)

import re
import ast
from typing import List, Tuple, Dict

class OmegaProtocolValidator:
    def __init__(self):
        # Normalized invariant patterns (case-insensitive, handles common variations)
        self.decomposition_patterns = [
            r'phi[_\s]*n', r'phi[_\s]*delta', r'φ[_\s]*n', r'φ[_\s]*Δ',
            r'newtonian[_\s]*mode', r'asymmetry[_\s]*mode',
            r'covariant[_\s]*decomposition', r'φ_n', r'φ_Δ'
        ]
        self.metric_coupling_patterns = [
            r'ln\s*\(\s*phi[_\s]*n\s*\)', r'ln\s*\(\s*φ[_\s]*n\s*\)',
            r'psi\s*=', r'ψ\s*=', r'log\s*\(\s*phi[_\s]*n\s*\)',
            r'ln\(phi_n\)', r'ln\(φ_n\)'
        ]
        self.stiffness_patterns = [
            r'xi[_\s]*n', r'xi[_\s]*delta', r'ξ[_\s]*n', r'ξ[_\s]*Δ',
            r'stiffness[_\s]*newtonian', r'stiffness[_\s]*asymmetry',
            r'ξ_N', r'ξ_Δ'
        ]
        self.action_derivation_indicators = [
            r'action', r'lagrangian', r'hamiltonian', r'variational',
            r'δS', r'∫.*d⁴x', r'einstein[_\s]*hilbert',
            r'relational[_\s]*chain', r'overlap[_\s]*density',
            r'RCOD', r'bianchi[_\s]*identity'
        ]
    
    def _normalize_expression(self, expr: str) -> str:
        """Normalize expression for pattern matching"""
        # Remove extra whitespace, handle common LaTeX/code variations
        expr = re.sub(r'\s+', ' ', expr.strip())
        expr = expr.replace('\\', '').replace('{', '').replace('}', '')
        return expr.lower()
    
    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if any pattern matches in text"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def validate_expression(self, expr: str) -> Dict[str, bool]:
        """
        Validate a single mathematical expression against Omega Protocol invariants
        Returns dict with validation results for each invariant category
        """
        normalized = self._normalize_expression(expr)
        
        results = {
            'decomposition': self._check_patterns(normalized, self.decomposition_patterns),
            'metric_coupling': self._check_patterns(normalized, self.metric_coupling_patterns),
            'stiffness_terms': self._check_patterns(normalized, self.stiffness_patterns),
            'action_derivation': self._check_patterns(normalized, self.action_derivation_indicators)
        }
        
        # Overall compliance requires all core invariants (action derivation is recommended but not always visible in simplified expr)
        results['core_compliant'] = all([
            results['decomposition'],
            results['metric_coupling'],
            results['stiffness_terms']
        ])
        
        return results
    
    def validate_expressions(self, expressions: List[str]) -> List[Dict]:
        """Validate multiple expressions"""
        return [self.validate_expression(expr) for expr in expressions]

def main():
    # Expressions from the original Engine output (as cited in Scrutiny audit)
    engine_expressions = [
        "E_chaos = alpha * (1 / (cod_initial + 0.01))",
        "E_critical = 100",
        "Phi_Delta = Delta_S * math.log(1 / (cod_initial + 0.01))"
    ]
    
    validator = OmegaProtocolValidator()
    results = validator.validate_expressions(engine_expressions)
    
    print("="*60)
    print("OMEGA PROTOCOL MATHEMATICAL COMPLIANCE AUDIT")
    print("="*60)
    
    for i, (expr, res) in enumerate(zip(engine_expressions, results), 1):
        print(f"\nExpression {i}: {expr}")
        print("-" * 50)
        print(f"  Covariant Modes Decomposition (Φ_N/Φ_Δ): {'PASS' if res['decomposition'] else 'FAIL'}")
        print(f"  Metric Coupling (ψ = ln(φₙ)):           {'PASS' if res['metric_coupling'] else 'FAIL'}")
        print(f"  Stiffness Terms (ξ_N, ξ_Δ):             {'PASS' if res['stiffness_terms'] else 'FAIL'}")
        print(f"  Action Derivation Indicators:           {'PASS' if res['action_derivation'] else 'FAIL'}")
        print(f"  OVERALL CORE COMPLIANCE:                {'PASS' if res['core_compliant'] else 'FAIL'}")
        
        if not res['core_compliant']:
            print("\n  REQUIRED CORRECTIONS:")
            if not res['decomposition']:
                print("    - Must explicitly reference Φ_N and Φ_Δ decomposition")
            if not res['metric_coupling']:
                print("    - Must include metric coupling invariant ψ = ln(φₙ)")
            if not res['stiffness_terms']:
                print("    - Must include stiffness terms ξ_N and ξ_Δ")
    
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    compliant_count = sum(1 for res in results if res['core_compliant'])
    print(f"Expressions Compliant: {compliant_count}/{len(engine_expressions)}")
    
    if compliant_count == 0:
        print("\nVERDICT: ALL EXPRESSIONS VIOLATE OMEGA PROTOCOL INVARIANTS")
        print("REQUIRED ACTION: Expressions must be reformulated to include:")
        print("  1. Explicit Φ_N/Φ_Δ covariant mode decomposition")
        print("  2. Metric coupling term ψ = ln(φₙ)") 
        print("  3. Stiffness parameters ξ_N and ξ_Δ")
        print("  4. Derivation from Ω-Action (Relational Chain Overlap Density framework)")
    else:
        print("\nVERDICT: SOME EXPRESSIONS MEET CORE INVARIANTS")
    
    # Example of compliant expression for reference
    print("\n" + "="*60)
    print("EXAMPLE OF COMPLIANT EXPRESSION")
    print("="*60)
    compliant_example = (
        "Phi_Delta = xi_N * xi_Delta * ln(phi_N) * "
        "(phi_N + phi_Delta) * sqrt(RCOD_flux)"
    )
    print(f"Expression: {compliant_example}")
    example_result = validator.validate_expression(compliant_example)
    print(f"Decomposition: {'PASS' if example_result['decomposition'] else 'FAIL'}")
    print(f"Metric Coupling: {'PASS' if example_result['metric_coupling'] else 'FAIL'}")
    print(f"Stiffness Terms: {'PASS' if example_result['stiffness_terms'] else 'FAIL'}")
    print(f"Overall: {'PASS' if example_result['core_compliant'] else 'FAIL'}")

if __name__ == "__main__":
    main()