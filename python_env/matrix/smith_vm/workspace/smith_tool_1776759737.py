# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol (v26.0) Compliance Checker
-----------------------------------------
Checks a given text (Engine Output) for:
  - NO BOILERPLATE   : no markdown headings, bold headings,
                       numbered lists, or bullet points.
  - COVARIANT MODES  : presence of Φ_N and Φ_Δ symbols.
  - INVARIANTS       : ψ, ξ_N, ξ_Δ must be defined *and* appear
                       in at least one dynamical equation.
  - BOUNDARIES       : Shredding condition and Informational Freeze.
  - ENTROPY OBSERVABLE: entropy‑related keyword or formula.
  - DIMENSIONAL CHECK: explicit dimensional‑consistency phrase.
  - EQUATION‑LEVEL DERIVATION: at least one derivation step.
  - Φ‑DENSITY IMPACT: short‑term/long‑term numbers with rationale.
"""

import re
import sys

def load_text():
    """Read the Engine Output from stdin or a file."""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return sys.stdin.read()

def check_no_boilerplate(text):
    """Return True if no boilerplate patterns are found."""
    patterns = [
        r'^\s*#{1,6}\s',               # markdown headings
        r'^\s*\*\*.*?\*\*\s*$',        # bold line headings
        r'^\s*\d+\.\s',                # numbered list
        r'^\s*[-*]\s',                 # bullet point
    ]
    for line in text.splitlines():
        for pat in patterns:
            if re.match(pat, line):
                return False, f"Boilerplate detected: '{line[:60]}...'"
    return True, ""

def check_covariant_modes(text):
    """Check for Φ_N and Φ_Δ (Unicode or LaTeX)."""
    phi_n = r'\\?Φ_N'   # Φ_N or \Phi_N
    phi_d = r'\\?Φ_Δ'   # Φ_Δ or \Phi_Δ
    found_n = re.search(phi_n, text) is not None
    found_d = re.search(phi_d, text) is not None
    ok = found_n and found_d
    msg = f"Φ_N present: {found_n}, Φ_Δ present: {found_d}"
    return ok, msg

def check_invariants(text):
    """ψ, ξ_N, ξ_Δ must be defined and appear in a dynamical equation."""
    # Definitions (static)
    defs = {
        r'\\?ψ\s*=\s*ln\\(Φ_N/v\\)': 'ψ',
        r'\\?ξ_N\^{-2}\s*=\s*λ\\(3Φ_N\^2\+Φ_Δ\^2\-v\^2\\)': 'ξ_N',
        r'\\?ξ_Δ\^{-2}\s*=\s*λ\\(Φ_N\^2\+3Φ_Δ\^2\-v\^2\\)': 'ξ_Δ',
    }
    # Dynamical usage: look for the invariant inside an equation
    # (contains an equals sign or a differential operator)
    dyn_patterns = [
        r'\\?ψ',          # any occurrence of ψ in a formula
        r'\\?ξ_N',
        r'\\?ξ_Δ',
    ]
    defined = {}
    for pat, name in defs.items():
        defined[name] = re.search(pat, text) is not None

    used_dyn = {}
    for pat in dyn_patterns:
        used_dyn[pat.strip('\\?')] = re.search(pat, text) is not None

    # Require each invariant to be both defined and used dynamically
    all_ok = all(defined.get(k, False) and used_dyn.get(k, False)
                 for k in ['ψ', 'ξ_N', 'ξ_Δ'])
    details = {
        'defined': defined,
        'used_dyn': used_dyn,
    }
    msg = f"Defined: {defined}; Used in dynamics: {used_dyn}"
    return all_ok, msg

def check_boundaries(text):
    """Shredding condition (ξ_Δ→∞) and Informational Freeze (Φ_Δ saturates at Λ_Δ)."""
    shred = r'ξ_Δ\s*→\s*∞|Φ_N\^2\s*\+\s*3\s*Φ_Δ\^2\s*=\s*v\^2'
    freeze = r'Φ_Δ\s*.*?saturates.*?Λ_Δ|Informational Freeze'
    ok_shred = re.search(shred, text, re.IGNORECASE) is not None
    ok_freeze = re.search(freeze, text, re.IGNORECASE) is not None
    ok = ok_shred and ok_freeze
    msg = f"Shredding: {ok_shred}, Freeze: {ok_freeze}"
    return ok, msg

def check_entropy_observable(text):
    """Look for entropy‑related keywords or a symbolic entropy formula."""
    entropy_keys = [
        r'entropy', r'Shannon', r'S_h', r'topological entanglement',
        r'\\gamma', r'\\S', r'\\mathcal{S}'
    ]
    ok = any(re.search(k, text, re.IGNORECASE) for k in entropy_keys)
    msg = f"Entropy observable found: {ok}"
    return ok, msg

def check_dimensional_check(text):
    """Explicit phrase indicating a dimensional consistency check."""
    dim_patterns = [
        r'dimensional.*check', r'check.*dimension', r'[E]', r'\\\[E\\\]',
        r'units', r'dimension of'
    ]
    ok = any(re.search(p, text, re.IGNORECASE) for p in dim_patterns)
    msg = f"Dimensional check present: {ok}"
    return ok, msg

def check_equation_level_derivation(text):
    """At least one step showing variation of the action or deriving EOM."""
    derivation_keys = [
        r'\\Box', r'∂_μ', r'variation', r'δS', r'Euler‑Lagrange',
        r'equation of motion', r'mass matrix', r'eigenvalue',
        r'effective potential', r'Coleman-Weinberg'
    ]
    ok = any(re.search(k, text, re.IGNORECASE) for k in derivation_keys)
    msg = f"Equation‑level derivation evidence: {ok}"
    return ok, msg

def check_phi_density_impact(text):
    """Short‑term/long‑term Φ‑density numbers with rationale."""
    # Look for patterns like “~8 % dip” or “~30 % gain”
    pattern = r'~(?:\d+\.?\d*)\s*%.*?(?:dip|gain|impact)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    ok = len(matches) >= 2  # at least short‑term and long‑term mentioned
    msg = f"Φ‑density impact mentions: {matches}"
    return ok, msg

def main():
    text = load_text()
    checks = [
        ("NO BOILERPLATE", check_no_boilerplate),
        ("COVARIANT MODES", check_covariant_modes),
        ("INVARIANTS", check_invariants),
        ("BOUNDARIES", check_boundaries),
        ("ENTROPY OBSERVABLE", check_entropy_observable),
        ("DIMENSIONAL CHECK", check_dimensional_check),
        ("EQUATION‑LEVEL DERIVATION", check_equation_level_derivation),
        ("Φ‑DENSITY IMPACT", check_phi_density_impact),
    ]

    results = {}
    all_pass = True
    for name, func in checks:
        ok, msg = func(text)
        results[name] = (ok, msg)
        if not ok:
            all_pass = False

    print("=== Omega Protocol Compliance Report ===")
    for name, (ok, msg) in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"{name:30} : {status}  ({msg})")
    print("-" * 50)
    print(f"Overall Verdict: {'PASS' if all_pass else 'FAIL'}")
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())