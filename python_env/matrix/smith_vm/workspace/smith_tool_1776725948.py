# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import sys

def validate_bsm_proposal(text):
    """
    Validates the Biological Gauge Symmetry Monitoring (BGSM-Ω) proposal against Omega Protocol invariants.
    Returns a dictionary with validation results and a compliance score.
    """
    # Initialize validation checks
    checks = {
        'action': False,
        'covariant_derivative': False,
        'potential': False,
        'fluctuation_operator': False,
        'phi_n_phi_delta': False,
        'invariants': False,
        'boundaries': False,
        'entropy_gauge': False,
        'no_ginni': True,  # Assume passes unless Gini found
        'control_law': False,
        'equation_level_derivation': False  # Will be inferred from presence of derivations
    }
    
    # Normalize text for easier matching (remove extra whitespace, handle LaTeX)
    normalized = re.sub(r'\s+', ' ', text)
    
    # 1. Check for Biological Omega Action
    action_pattern = r'\\mathcal{S}_{\text{bio}}.*\\int d\^4x.*\\sqrt{-g}.*\\frac{1}{2} g^{\mu\nu} D_\mu\phi D_\nu\phi - V\(phi\)'
    if re.search(action_pattern, normalized, re.IGNORECASE):
        checks['action'] = True
    
    # 2. Check for gauge-covariant derivative definition
    cov_deriv_pattern = r'D_\mu\s*=\s*\\partial_\mu\s*[-–]\s*i\s*e\s*A_\mu'
    if re.search(cov_deriv_pattern, normalized, re.IGNORECASE):
        checks['covariant_derivative'] = True
    
    # 3. Check for quartic potential V(ϕ)
    potential_pattern = r'V\(\phi\)\s*=\s*\\frac{m\^2}{2}\phi\^2\s*[+]\s*\\frac{\lambda}{4}\phi\^4'
    if re.search(potential_pattern, normalized, re.IGNORECASE):
        checks['potential'] = True
    
    # 4. Check for fluctuation operator and effective mass
    flux_op_pattern = r'\\delta\^2 \mathcal{S}_{\text{bio}}/\\delta\phi\^2.*\|_{\phi=\phi_0}.*=-\partial_\mu\partial^\mu\s*[+]\s*m_{\text{eff}}\^2'
    mass_eff_pattern = r'm_{\text{eff}}\^2\s*=\s*m\^2\s*[+]\s*3\lambda\phi_0\^2'
    if re.search(flux_op_pattern, normalized, re.IGNORECASE) and re.search(mass_eff_pattern, normalized, re.IGNORECASE):
        checks['fluctuation_operator'] = True
    
    # 5. Check for Φ_N and Φ_Δ definitions (correlation functions)
    phi_n_pattern = r'\\Phi_N\s*=\s*\\frac{1}{V}\\int d\^3x.*\\langle \delta\phi_{\text{hom}}.*\delta\phi_{\text{hom}}.*\\rangle'
    phi_delta_pattern = r'\\Phi_\Delta\s*=\s*\\frac{1}{V}\\int d\^3x.*\\langle \delta\phi_{\text{top}}.*\delta\phi_{\text{top}}.*\\rangle'
    if re.search(phi_n_pattern, normalized, re.IGNORECASE) and re.search(phi_delta_pattern, normalized, re.IGNORECASE):
        checks['phi_n_phi_delta'] = True
    
    # 6. Check for invariants ψ, ξ_N, ξ_Δ
    psi_pattern = r'\\psi\s*=\s*\\ln\(\\xi/\\xi_0\)'
    xi_n_pattern = r'\\xi_N\s*=\s*\\[.*\\partial\^2 V_{\text{eff}}/\\partial \Phi_N\^2.*\\]'
    xi_delta_pattern = r'\\xi_\Delta\s*=\s*\\[.*\\partial\^2 V_{\text{eff}}/\\partial \Phi_\Delta\^2.*\\]'
    if re.search(psi_pattern, normalized, re.IGNORECASE) and \
       re.search(xi_n_pattern, normalized, re.IGNORECASE) and \
       re.search(xi_delta_pattern, normalized, re.IGNORECASE):
        checks['invariants'] = True
    
    # 7. Check for boundaries (Shredding Event and Informational Freeze)
    shredding_pattern = r'Shredding Event.*m_{\text{eff}}\\^2\s*=\s*0'
    freeze_pattern = r'Informational Freeze.*m_{\text{eff}}\\^2\s*->\s*\\\\inf'
    if re.search(shredding_pattern, normalized, re.IGNORECASE) and \
       re.search(freeze_pattern, normalized, re.IGNORECASE):
        checks['boundaries'] = True
    
    # 8. Check for entropy gauge (Shannon entropy) and absence of Gini
    shannon_pattern = r'S_h\s*=\s*-\\sum_i p_i \\ln p_i'
    gini_pattern = r'Gini\s*coefficient'
    if re.search(shannon_pattern, normalized, re.IGNORECASE):
        checks['entropy_gauge'] = True
    if re.search(gini_pattern, normalized, re.IGNORECASE):
        checks['no_ginni'] = False
    
    # 9. Check for gauge-invariant control law
    control_law_pattern = r'dT/dt\s*=\s*-\\gamma\\s*\\partial m_{\text{eff}}\\^2/\\partial T'
    if re.search(control_law_pattern, normalized, re.IGNORECASE):
        checks['control_law'] = True
    
    # 10. Check for equation-level derivation (inferred from presence of key derivations)
    # If we have action, fluctuation operator, and invariants derived, assume equation-level
    if checks['action'] and checks['fluctuation_operator'] and checks['invariants']:
        checks['equation_level_derivation'] = True
    
    # Calculate compliance score (weighted)
    weights = {
        'action': 0.1,
        'covariant_derivative': 0.1,
        'potential': 0.1,
        'fluctuation_operator': 0.1,
        'phi_n_phi_delta': 0.1,
        'invariants': 0.1,
        'boundaries': 0.1,
        'entropy_gauge': 0.1,
        'no_ginni': 0.05,  # Bonus for avoiding Gini
        'control_law': 0.1,
        'equation_level_derivation': 0.05
    }
    
    score = sum(weights[key] * (1 if checks[key] else 0) for key in weights)
    score = min(score, 1.0)  # Cap at 1.0
    
    # Determine if proposal passes Omega Protocol (threshold: 0.85)
    passes = score >= 0.85
    
    return {
        'checks': checks,
        'score': score,
        'passes': passes,
        'feedback': generate_feedback(checks, score)
    }

def generate_feedback(checks, score):
    """Generate concise feedback based on validation results."""
    failed = [k for k, v in checks.items() if not v]
    if not failed:
        return "EXCELLENT: All Omega Protocol invariants satisfied. Proposal is mathematically sound and compliant."
    
    feedback = []
    if 'action' in failed:
        feedback.append("Missing or incomplete biological Omega Action formulation.")
    if 'covariant_derivative' in failed:
        feedback.append("Gauge-covariant derivative not properly defined (should include entropy gradient).")
    if 'potential' in failed:
        feedback.append("Quartic potential V(ϕ) not correctly specified.")
    if 'fluctuation_operator' in failed:
        feedback.append("Fluctuation operator or effective mass derivation incomplete.")
    if 'phi_n_phi_delta' in failed:
        feedback.append("Φ_N and Φ_Δ not derived as eigenmodes from fluctuation operator.")
    if 'invariants' in failed:
        feedback.append("Invariants ψ, ξ_N, ξ_Δ not derived from curvature analysis.")
    if 'boundaries' in failed:
        feedback.append("Shredding Event/Informational Freeze boundaries not tied to m_eff²=0/∞.")
    if 'entropy_gauge' in failed:
        feedback.append("Shannon entropy gauge not properly formulated.")
    if not checks['no_ginni']:
        feedback.append("CRITICAL: Gini coefficient detected (violates entropy gauge requirement).")
    if 'control_law' in failed:
        feedback.append("Gauge-invariant control law missing or incorrect.")
    if 'equation_level_derivation' in failed:
        feedback.append("Lacks clear equation-level derivation from action principle.")
    
    return f"DEFICIENT ({score*100:.0f}% compliant): {'; '.join(feedback)}"

def main():
    # Read proposal text from stdin (assumed to be the Engine's refined biology proposal)
    proposal_text = sys.stdin.read()
    
    if not proposal_text.strip():
        print("ERROR: No input provided. Please pipe the proposal text to this script.", file=sys.stderr)
        sys.exit(1)
    
    result = validate_bsm_proposal(proposal_text)
    
    # Output validation results
    print("=== OMEGA PROTOCOL VALIDATION REPORT ===")
    print(f"Compliance Score: {result['score']*100:.1f}%")
    print(f"Status: {'PASS' if result['passes'] else 'FAIL'}")
    print("\nDetailed Checks:")
    for check, passed in result['checks'].items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check.replace('_', ' ').title()}")
    print("\nFeedback:")
    print(result['feedback'])
    
    # Exit with failure code if non-compliant (for automation)
    if not result['passes']:
        sys.exit(1)

if __name__ == "__main__":
    main()