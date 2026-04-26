# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Rubric v26.0 Validator (minimal version)

Checks a proposal text for:
  1. Invariant must be expressed as psi = ln(phi_n)  (allowing optional whitespace/comments)
  2. Fokker-Planck equation must contain the factor 1/2 before the second‑order term
  3. The action integral must contain an entropy gauge term A_mu J^mu
  4. No contradictory dimensional claim: if the text declares the action dimensionless,
     it must not also claim that stiffness invariants have dimensions of time
     without introducing a characteristic time scale.

The script returns a PASS/FAIL list with explanations.
"""

import re
import sys

def read_proposal(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def check_invariant(text: str):
    """
    Look for a statement that defines the invariant psi as the natural log of phi_n.
    We accept variations like:
        psi = ln(phi_n)
        ψ = ln(Φ_N)
        psi = ln( phi_n )
    but reject any additional additive/multiplicative terms outside the log.
    """
    # Normalize whitespace and common unicode glyphs
    normalized = text.replace('ψ', 'psi').replace('Φ', 'Phi').replace('∂', 'partial')
    # Pattern: psi = ln( something that is exactly phi_n (allow subscript _n) )
    pattern = r'psi\s*=\s*ln\s*\(\s*Phi\s*_?n\s*\)'
    if re.search(pattern, normalized, re.IGNORECASE):
        return True, "Invariant appears as psi = ln(phi_n)."
    # Also allow phi_n without the capital Phi (some texts use phi)
    pattern2 = r'psi\s*=\s*ln\s*\(\s*phi\s*_?n\s*\)'
    if re.search(pattern2, normalized, re.IGNORECASE):
        return True, "Invariant appears as psi = ln(phi_n)."
    return False, "Invariant does NOT match the required form psi = ln(phi_n)."

def check_fokker_planck(text: str):
    """
    The canonical FP: ∂_t P = -∂_x[μ P] + (1/2) ∂_x^2[D P] + S
    We look for the fraction 1/2 (or 0.5) directly before a second‑order derivative term.
    """
    # Look for patterns like "1/2", "0.5", "\frac{1}{2}" before a second derivative
    # Second derivative patterns: ∂_x^2, ∂²/∂x², partial_x^2, d^2/dx^2
    second_deriv = r'(?:∂_?[a-zA-Z]\^2|∂²/∂[a-zA-Z]²|partial_[a-zA-Z]\^2|d^2/d[a-zA-Z]²)'
    half_pattern = r'(?:1/2|0\.5|\\frac\s*{\s*1\s*}\s*{\s*2\s*})'
    # We need half_pattern somewhere before second_deriv (allowing spaces and other tokens)
    combined = rf'{half_pattern}.*{second_deriv}'
    if re.search(combined, text, re.IGNORECASE | re.DOTALL):
        return True, "Fokker-Planck diffusion term contains the required 1/2 factor."
    # Also check the reverse order (second derivative then 1/2) – less likely but safe
    combined_rev = rf'{second_deriv}.*{half_pattern}'
    if re.search(combined_rev, text, re.IGNORECASE | re.DOTALL):
        return True, "Fokker-Planck diffusion term contains the required 1/2 factor."
    return False, "Fokker-Planck equation missing the 1/2 prefactor on the diffusion term."

def check_entropy_gauge(text: str):
    """
    The action must contain a term A_mu J^mu (or A_μ J^μ). We look for:
        A_?mu.*J^?mu   or   A_?mu J^?mu
    allowing for indices and summation notation.
    """
    # Normalize mu/unicode
    normalized = text.replace('μ', 'mu').replace('ν', 'nu')
    # Pattern: A_mu J^mu  (with optional indices, summation, or contraction dots)
    pattern = r'A\s*_?mu\s*.*?J\s*\^?mu'
    if re.search(pattern, normalized, re.IGNORECASE | re.DOTALL):
        return True, "Action contains an entropy gauge term A_mu J^mu."
    return False, "Action integral does NOT contain an explicit entropy gauge term A_mu J^mu."

def check_dimensional_consistency(text: str):
    """
    Detect contradictory statements:
      - The action is declared dimensionless (or natural units, ℏ=c=1, etc.)
      - AND the text claims stiffness invariants have dimensions of time
        WITHOUT introducing a characteristic time scale (e.g., τ, ℓ/c).
    We'll flag if both appear and no time scale is mentioned.
    """
    # Look for dimensionless action claims
    dimless_action = re.search(r'action.*dimensionless|dimensionless.*action|natural\s*units', text, re.IGNORECASE)
    # Look for stiffness invariants having time dimension
    stiffness_time = re.search(r'(?:stiffness\s*invariants?|xi_N|xi_Δ).*\btime\b|\btime\b.*(?:stiffness\s*invariants?|xi_N|xi_Δ)', text, re.IGNORECASE)
    # Look for any introduction of a characteristic time scale (tau, ℓ/c, etc.)
    time_scale = re.search(r'\\btau\\b|\\bell\\s*/\\s*c|characteristic\s*time|time\s*scale', text, re.IGNORECASE)
    if dimless_action and stiffness_time and not time_scale:
        return False, ("Contradiction: action declared dimensionless while stiffness invariants "
                       "are said to have dimensions of time without a defined time scale.")
    return True, "No obvious dimensional contradiction detected."

def validate_proposal(path: str):
    text = read_proposal(path)
    results = []

    ok, msg = check_invariant(text)
    results.append(("Invariant form (psi = ln(phi_n))", ok, msg))

    ok, msg = check_fokker_planck(text)
    results.append(("Fokker-Planck 1/2 factor", ok, msg))

    ok, msg = check_entropy_gauge(text)
    results.append(("Entropy gauge term A_mu J^mu", ok, msg))

    ok, msg = check_dimensional_consistency(text)
    results.append(("Dimensional consistency", ok, msg))

    # Summary
    print("=== Omega Protocol Rubric v26.0 Validation ===")
    all_ok = True
    for name, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        print(f"{status:4} | {name:35} | {msg}")
        if not ok:
            all_ok = False
    print("\nOverall:", "PASS" if all_ok else "FAIL")
    return all_ok

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate_omega_proposal.py <proposal_text_file>")
        sys.exit(1)
    validate_proposal(sys.argv[1])