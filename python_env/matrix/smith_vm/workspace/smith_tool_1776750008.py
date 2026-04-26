# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import math

def omega_protocol_check(text: str) -> dict:
    """
    Validate a proposal against the Omega Physics Rubric v26.0.
    Returns a dict with pass/fail flags and messages for each pillar.
    """
    results = {}

    # 1. NO BOILERPLATE – no markdown headings, no explicit list markers,
    #    no numbered sections, no bold/italic markup used as section labels.
    heading_pattern = r'^\s{0,3}#{1,6}\s+.+$'          # lines like ### Title
    list_pattern   = r'^\s*([-*+]\s+|\d+\.\s+).+$'    # bullet or ordered list
    bold_italic    = r'\*\*.+?\*\*|__.+?__'           # **bold** or __bold__
    results['NO_BOILERPLATE'] = {
        'pass': not (re.search(heading_pattern, text, re.M) or
                     re.search(list_pattern,   text, re.M) or
                     re.search(bold_italic,    text)),
        'msg': "Free‑form continuous narrative required."
    }

    # 2. Covariant modes – must mention Φ_N and Φ_Δ (Unicode or LaTeX)
    covariant = bool(re.search(r'Φ_N|\\Phi_N|\\\\Phi_N', text) and
                     re.search(r'Φ_Δ|\\Phi_Δ|\\\\Phi_Δ', text))
    results['COVARIANT_MODES'] = {
        'pass': covariant,
        'msg': "Both Φ_N and Φ_Δ must appear."
    }

    # 3. Invariants – ψ, ξ_N, ξ_Δ
    invariants = bool(re.search(r'ψ|\\psi', text) and
                      re.search(r'ξ_N|\\xi_N', text) and
                      re.search(r'ξ_Δ|\\xi_Δ', text))
    results['INVARIANTS'] = {
        'pass': invariants,
        'msg': "ψ, ξ_N, ξ_Δ must be present."
    }

    # 4. Boundary conditions – Shredding Event & Informational Freeze
    shredding = bool(re.search(r'Shredding\s+Event|PHI\s*→\s*0|ξ\s*→\s*0', text, re.I))
    freeze    = bool(re.search(r'Informational\s+Freeze|PHI\s*→\s*1|ξ\s*→\s*∞|xi\s*→\s*inf', text, re.I))
    results['BOUNDARIES'] = {
        'pass': shredding and freeze,
        'msg': "Both Shredding Event (PHI→0, ξ→0) and Informational Freeze (PHI→1, ξ→∞) required."
    }

    # 5. Entropy‑based observable – Shannon entropy of harmonic powers
    entropy = bool(re.search(r'Shannon\s+entropy|-\\s*\\sum.*log|I\(t\)\s*=.*entropy', text, re.I))
    results['ENTROPY_OBSERVABLE'] = {
        'pass': entropy,
        'msg': "Must define I(t) as negative Shannon entropy of harmonic powers."
    }

    # 6. Equation‑level derivation from Omega Action
    # Look for the action S[I] = ∫[½(dI/dt)² + V(I)]dt and V(I) = (λ/4)(I²−I₀²)²
    action = bool(re.search(r'S\[I\]\s*=\s*∫\s*\[\s*½\s*\(dI/dt\)\s*²\s*\+\s*V\(I\)\s*\]\s*dt', text))
    potential = bool(re.search(r'V\(I\)\s*=\s*\(λ/4\)\(\s*I²\s*-\s*I₀²\s*\)²', text))
    results['ACTION_DERIVATION'] = {
        'pass': action and potential,
        'msg': "Must start from S[I]=∫[½(dI/dt)²+V(I)]dt with V(I)=(λ/4)(I²−I₀²)²."
    }

    # 7. Dimensional consistency – simple keyword check (not full units analysis)
    dim_check = bool(re.search(r'dimensional\s+consistency|[time]⁻²|[time]⁻¹|dimensionless', text, re.I))
    results['DIMENSIONAL_CHECK'] = {
        'pass': dim_check,
        'msg': "Should include a dimensional consistency verification."
    }

    # 8. Φ‑density impact assessment – look for percentages over months or net gain
    phi_impact = bool(re.search(r'Φ‑density|Φ density|net\s*[+-]?\s*\d+%', text, re.I))
    results['PHI_IMPACT'] = {
        'pass': phi_impact,
        'msg': "Must provide a quantitative Φ‑density trajectory."
    }

    # Overall pass: all pillars must pass
    overall = all(v['pass'] for v in results.values())
    results['OVERALL'] = {'pass': overall,
                          'msg': "PASS" if overall else "FAIL – see individual pillars."}
    return results


# ----------------------------------------------------------------------
# Example usage with the Engine's original output (the one that failed)
if __name__ == "__main__":
    engine_text = r"""### Internal Thought Process
    ... (the full Engine output) ...
    ### Final Output
    ... 
    ### Reflection on Ω Protocol Φ Density Impact
    ..."""
    report = omega_protocol_check(engine_text)
    for k, v in report.items():
        if k != 'OVERALL':
            print(f"{k}: {'PASS' if v['pass'] else 'FAIL'} – {v['msg']}")
    print(f"OVERALL: {'PASS' if report['OVERALL']['pass'] else 'FAIL'} – {report['OVERALL']['msg']}")