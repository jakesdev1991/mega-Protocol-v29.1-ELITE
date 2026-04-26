# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 Compliance Validator
-----------------------------------------
Checks an Engine derivation for:
  - Tier‑0 invariants: ψ, xi_N, xi_Delta, entropy term
  - Correct integral scaling (Jacobian Λ³ and denominator (Λ*q*v)²)
  - Absence of boilerplate numbered‑list headings without math
Returns COMPLIANT or NON‑COMPLIANT with a brief diagnostic.
"""

import re
import sys

def validate_engine_output(text: str) -> tuple[bool, list[str]]:
    errors = []

    # 1. Required symbols (case‑insensitive)
    required = {
        r'\\psi': r'ψ',               # allow \psi or ψ
        r'xi_N': r'ξ_N',
        r'xi_Delta': r'ξ_Δ',
        r'entropy': r'entropy',       # will look for Shannon or topological impedance later
    }
    for pattern, label in required.items():
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"Missing required symbol/term: {label}")

    # 2. Entropy specificity – must mention Shannon conditional entropy or topological impedance
    entropy_ok = (
        re.search(r'Shannon\s+conditional\s+entropy', text, re.IGNORECASE) or
        re.search(r'topological\s+impedance', text, re.IGNORECASE)
    )
    if not entropy_ok:
        errors.append("Entropy term not specific enough (requires 'Shannon conditional entropy' or 'topological impedance')")

    # 3. Integral scaling check
    # Look for the integral definition line (approximate)
    integral_pattern = re.compile(
        r'\\int\s*_0\s*\^\s*Lambda\s*[\{\[](.*?)[\}\]]\s*d\^3k',  # ∫₀^Λ [...] d³k
        re.IGNORECASE | re.DOTALL
    )
    m = integral_pattern.search(text)
    if m:
        integrand = m.group(1)
        # Expected after substitution: Jacobian Λ**3 and denominator (Λ*q*v)**2
        # We simply check that Λ appears with power >=3 somewhere in the integrand
        # and that the denominator contains (Λ*q*v)² or equivalent.
        if not re.search(r'Lambda\s*\*\*\s*3|Lambda\^3|Lambda³', integrand):
            errors.append("Integral missing Jacobian factor Λ³ after k=Λq substitution")
        if not re.search(r'\(Lambda\s*\*\s*q\s*\*\s*v\)\s*\*\*\s*2|\(Lambda\s*q\s*v\)\^2', integrand, re.IGNORECASE):
            errors.append("Integral denominator missing (Λ·q·v)² factor after substitution")
    else:
        errors.append("Could not locate the main integral definition ∫₀^Λ [...] d³k")

    # 4. Boilerplate detection: numbered list headings without math
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Matches "1. Something" or "2. Something" etc.
        if re.match(r'^\d+\.\s+[A-Z]', stripped):
            # Check the same line or the next few lines for a math token (=, ∫, ∑, ∂, ∇, Λ, ξ, ψ)
            window = " ".join(lines[i:i+3])
            if not re.search(r'[=∫∑∂∇Λξψ]|\\\\begin\{equation\}|\\\\$', window):
                errors.append(
                    f"Boilerplate‑style heading at line {i+1}: '{stripped}' lacks accompanying mathematics"
                )

    compliant = len(errors) == 0
    return compliant, errors

def main():
    # Read the Engine output from stdin (or replace with a hard‑coded string for testing)
    engine_text = sys.stdin.read()
    if not engine_text.strip():
        print("Error: No input provided.", file=sys.stderr)
        sys.exit(1)

    ok, errs = validate_engine_output(engine_text)
    if ok:
        print("COMPLIANT")
    else:
        print("NON‑COMPLIANT")
        for e in errs:
            print(f" - {e}")

if __name__ == "__main__":
    main()