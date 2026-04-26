# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol (v26.0) Compliance Validator
------------------------------------------
Checks a given text for:
 1. NO BOILERPLATE   – no markdown headings, numbered lists, or bullet points.
 2. Covariant Modes  – Φ_N and Φ_Δ must appear.
 3. Invariants       – ψ, ξ_N, ξ_Δ must be defined *and* used dynamically.
 4. Boundaries       – Shredding Event and Informational Freeze must be mentioned.
 5. Entropy Observable – at least one entropy‑related term must appear.
 6. Equation‑Level Derivation – must contain a derivation keyword.
 7. Dimensional Consistency – must contain an explicit dimensional check.
 8. Φ‑Density Impact – must contain short‑term/long‑term quantitative estimates.
"""

import re
import sys

def validate_omega(text: str) -> bool:
    violations = []

    # 1. NO BOILERPLATE
    heading_pattern = r'(?m)^\s*(\#{1,6}|\*\*.*?\*\*)\s*$'          # markdown headings or **bold**
    list_pattern    = r'(?m)^\s*\d+\.\s+'                         # "1. ", "2. "
    bullet_pattern  = r'(?m)^\s*[-*]\s+'                          # "- " or "* "
    if re.search(heading_pattern, text):
        violations.append("BOILERPLATE: markdown heading or **bold** heading detected")
    if re.search(list_pattern, text):
        violations.append("BOILERPLATE: numbered list detected")
    if re.search(bullet_pattern, text):
        violations.append("BOILERPLATE: bullet list detected")

    # 2. Covariant Modes
    if r'\Phi_N' not in text and r'\\Phi_N' not in text:
        violations.append("COVARIANT MODE: Φ_N not found")
    if r'\Phi_\Delta' not in text and r'\\Phi_\Delta' not in text:
        violations.append("COVARIANT MODE: Φ_Δ not found")

    # 3. Invariants – definition + dynamical use
    inv_defs = {
        r'\\psi\s*=':      'ψ',
        r'\\xi_N\s*^{-2}\s*=': 'ξ_N⁻²',
        r'\\xi_\Delta\s*^{-2}\s*=': 'ξ_Δ⁻²',
    }
    inv_used = {
        'ψ':   False,
        'ξ_N': False,
        'ξ_Δ': False,
    }
    for pattern, name in inv_defs.items():
        if re.search(pattern, text):
            inv_used[name] = True
    # Dynamical use: look for the invariant appearing in an expression that is not just a definition.
    # Simple heuristic: the invariant appears with an operator (+,-,*,/,^,=,<,>, etc.) elsewhere.
    dyn_patterns = {
        'ψ':   r'\\psi\s*[+\-*/^=<>]',
        'ξ_N': r'\\xi_N\s*[+\-*/^=<>]',
        'ξ_Δ': r'\\xi_\Delta\s*[+\-*/^=<>]',
    }
    for name, pat in dyn_patterns.items():
        if re.search(pat, text):
            inv_used[name] = True
    for name, used in inv_used.items():
        if not used:
            violations.append(f"INVARIANT: {name} not defined or not used dynamically")

    # 4. Boundaries
    if r'\\xi_\Delta\s*->\s*\\infty' not in text and r'\\xi_\Delta\s*→\s*∞' not in text:
        violations.append("BOUNDARY: Shredding Event (ξ_Δ→∞) not found")
    if r'\\Phi_\Delta' not in text and r'\\Phi_\Delta' not in text:
        # we already checked for Φ_Δ presence; now look for saturation language
        if not re.search(r'(saturation|saturates|at\s*\\Lambda_\Delta)', text, re.I):
            violations.append("BOUNDARY: Informational Freeze (Φ_Δ at Λ_Δ) not found")

    # 5. Entropy Observable
    entropy_terms = [
        r'entropy', r'Shannon', r'topological entanglement entropy',
        r'S_h', r'\\gamma', r'entanglement entropy'
    ]
    if not any(re.search(pat, text, re.I) for pat in entropy_terms):
        violations.append("ENTROPY: no entropy‑based observable detected")

    # 6. Equation‑Level Derivation
    derivation_keywords = [
        r'derive', r'derived', r'equation of motion', r'Euler-Lagrange',
        r'variational', r'action', r'Lagrangian', r'Hamiltonian',
        r'effective potential', r'Coleman-Weinberg', r'beta function'
    ]
    if not any(re.search(pat, text, re.I) for pat in derivation_keywords):
        violations.append("DERIVATION: no explicit equation‑level derivation detected")

    # 7. Dimensional Consistency
    dim_patterns = [
        r'dimensional.*check', r'dimension.*analysis',
        r'\\[E\\]', r'units', r'[E]\\^[0-9]', r'energy\^[0-9]',
        r'[M][L]\\^[0-9]', r'[M][L]\\^2[T]\\^[-2]'
    ]
    if not any(re.search(pat, text, re.I) for pat in dim_patterns):
        violations.append("DIMENSIONAL: no explicit dimensional consistency check found")

    # 8. Φ‑Density Impact (short‑term/long‑term numbers)
    impact_pattern = r'(short[-\s]?term|long[-\s]?term).*?[\d.]+%'
    if not re.search(impact_pattern, text, re.I):
        violations.append("Φ‑DENSITY: missing short‑term/long‑term quantitative impact")

    if violations:
        print("Ω Protocol VIOLATIONS:")
        for v in violations:
            print(f" - {v}")
        return False
    return True


if __name__ == "__main__":
    # Read the Engine output from stdin or a file supplied as first argument.
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    if validate_omega(content):
        print("✅ Engine output PASSES all Omega Protocol (v26.0) pillars.")
        sys.exit(0)
    else:
        print("❌ Engine output FAILS Omega Protocol compliance.")
        sys.exit(1)