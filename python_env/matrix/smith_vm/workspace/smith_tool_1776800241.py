# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

def validate_omega_protocol_compliance(engine_output: str) -> dict:
    """
    Validates Engine output against Omega Protocol invariants and mathematical soundness.
    Checks for:
    1. Presence of required invariants: ψ = ln(Φ_N), ξ_N, ξ_Δ
    2. Absence of known one-loop anisotropic term error (angle dependence loss)
    3. Structural consistency of tensor decomposition
    
    Returns dict with compliance flags and actionable feedback.
    """
    # Normalize LaTeX whitespace and common variants
    normalized = re.sub(r'\\[\[\]]', '', engine_output)  # Remove bracket commands
    normalized = re.sub(r'\\s+', ' ', normalized)       # Collapse whitespace
    normalized = re.sub(r'\\{([^}]*)\\}', r'\1', normalized)  # Remove LaTeX braces
    
    # === INVARIANT COMPLIANCE CHECK (Omega Physics Rubric v26.0) ===
    invariant_patterns = [
        (r'\\psi\s*=\s*\\ln\s*\(\s*\\Phi_N\s*\)', "ψ = ln(Φ_N)"),
        (r'\\xi_N', "ξ_N"),
        (r'\\xi_\\s*\\\\Delta', "ξ_Δ"),  # Handles \xi_\Delta, \xi_ {Delta}, etc.
        (r'psi\s*=\s*ln\s*\(\s*Phi_N\s*\)', "psi = ln(Phi_N)"),  # Plain text fallback
        (r'xi_N', "xi_N"),
        (r'xi_Delta', "xi_Delta")
    ]
    
    invariant_flags = {}
    for pattern, label in invariant_patterns:
        invariant_flags[label] = bool(re.search(pattern, normalized, re.IGNORECASE))
    
    all_invariants_present = all(invariant_flags.values())
    
    # === MATHEMATICAL SOUNDNESS CHECK ===
    # 1. One-loop anisotropic term: Must retain angular dependence after trace
    oneloop_correct = True
    # Known incorrect pattern from Scrutiny audit: bracket reduces to m²-only
    incorrect_oneloop_pattern = r'\\delta_{\\mu z}\\delta_{\\nu z}.*\\\\sin k\\\\cdot\\\\sin\\(k-p\\).*-\\\\delta_{\\mu z}\\delta_{\\nu z}\\(.*\\\\sin k\\\\cdot\\\\sin\\(k-p\\).* - m^2\\)'
    if re.search(incorrect_oneloop_pattern, normalized, re.IGNORECASE):
        oneloop_correct = False
    
    # 2. Tensor decomposition: Must include all 4 components (T, L, M, P)
    tensor_components = {
        'transverse': r'Pi_T.*\\(delta_{\\\\mu\\\\nu}-p_\\\\mu p_\\\\nu/p^2\\)',
        'longitudinal': r'Pi_L.*n_\\\\mu n_\\\\nu',
        'mixed': r'Pi_M.*\\(p_\\\\mu n_\\\\nu \\+ n_\\\\mu p_\\\\nu\\)',
        'pure': r'Pi_P.*p_\\\\mu p_\\\\nu/p^2'
    }
    tensor_flags = {k: bool(re.search(v, normalized, re.IGNORECASE)) for k, v in tensor_components.items()}
    tensor_complete = all(tensor_flags.values())
    
    # 3. Effective alpha_formula: Must show directional dependence via Φ_Δ
    alpha_formula_correct = bool(re.search(
        r'alpha_eff\\^i.*=.*alpha_0.*/.*1.*\\+.*Pi_T.*\\+.*delta_i.*z.*Phi_\\\\Delta.*\\[.*Pi_L.*\\+.*2.*Pi_M\\]',
        normalized, re.IGNORECASE
    ))
    
    # === PROTOCOL-LEVEL CONSISTENCY CHECK ===
    # Check for entropy-gauge coupling: S_pair = -Tr ln S_F → S_1 = -(Π_L + 2Π_M)
    entropy_gauge_correct = bool(re.search(
        r'S_pair.*=.*S_0.*\\+.*Phi_\\\\Delta.*S_1.*|S_1.*=.*-\\s*\\(Pi_L.*\\+.*2.*Pi_M\\)',
        normalized, re.IGNORECASE
    ))
    
    # === COMPOSITE JUDGMENT ===>
    math_sound = oneloop_correct and tensor_complete and alpha_formula_correct and entropy_gauge_correct
    protocol_compliant = all_invariants_present and math_sound
    
    # Generate specific feedback
    feedback = []
    if not all_invariants_present:
        missing = [label for label, present in invariant_flags.items() if not present]
        feedback.append(f"MISSING INVARIANTS: {', '.join(missing)}. Required by Rubric v26.0 for Φ_N/Φ_Δ coupling.")
    if not oneloop_correct:
        feedback.append("ONE-LOOP ERROR: Anisotropic term loses angular dependence (bracket reduces to m²-only). Must retain sin_z k sin_z(k-p) structure.")
    if not tensor_complete:
        missing_comp = [k for k, v in tensor_flags.items() if not v]
        feedback.append(f"INCOMPLETE TENSOR: Missing components {', '.join(missing_comp)} in Π_μν decomposition.")
    if not alpha_formula_correct:
        feedback.append("ALPHA_FORMULA ERROR: Directional coupling missing Φ_Δ[Π_L + 2Π_M] term for z-direction.")
    if not entropy_gauge_correct:
        feedback.append("ENTROPY_GAUGE ERROR: S_1 ≠ -(Π_L + 2Π_M) breaks entropy-coupling consistency.")
    
    return {
        'invariant_compliant': all_invariants_present,
        'math_sound': math_sound,
        'protocol_compliant': protocol_compliant,
        'feedback': feedback,
        'details': {
            'invariants': invariant_flags,
            'oneloop_correct': oneloop_correct,
            'tensor_components': tensor_flags,
            'alpha_formula_correct': alpha_formula_correct,
            'entropy_gauge_correct': entropy_gauge_correct
        }
    }

# Example usage (in VM, engine_output would be provided by Engine):
# result = validate_omega_protocol_compliance(engine_output)
# if not result['protocol_compliant']:
#     print("PROTOCOL VIOLATION DETECTED:")
#     for msg in result['feedback']:
#         print(f"  - {msg}")
# else:
#     print("OUTPUT COMPLIANT WITH OMEGA PROTOCOL")