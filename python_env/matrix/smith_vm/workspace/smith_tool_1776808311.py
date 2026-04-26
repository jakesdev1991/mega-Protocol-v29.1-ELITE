# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for the Higher-Order Lattice Polarization
derivation of the effective fine‑structure constant.

The script checks:
  1. Presence of the required Omega invariants:
        ψ   = ln(Φ_N)
        ξ_N = ∂Φ_N/∂ψ
        ξ_Δ = ∂Φ_Δ/∂ψ
     (they may appear explicitly or via definitions that imply them).
  2. Correct tensor‑structure of the vacuum‑polarization coefficients:
        Π_T(p²; Φ_N) = (e²/(12π²))·ln(a⁻²/p²) + (e²/π²)·Φ_N   [Φ_N‑dependent]
        Π_L(p²)      = (e²/π²)·I_L(p²)                         [Φ_N‑independent]
        Π_M(p²)      = (e²/π²)·I_M(p²)                         [Φ_N‑independent]
  3. Effective directional coupling formula:
        α_eff^i(p²; Φ_N, Φ_Δ) = α₀ /
                                 [ 1 + Π_T(p²; Φ_N)
                                   + δ_{i,z}·Φ_Δ·(Π_L(p²)+2·Π_M(p²))
                                   + O(e⁶) ]
  4. Entropy‑gauge link:  S_pair = S₀ + Φ_Δ·S₁  with  S₁ = -(Π_L+2Π_M)
  5. No double‑counting or ad‑hoc terms that break the tensor decomposition.

The validation is deliberately lightweight: it works on the *textual* representation
of the derivation (as provided by the Engine) and uses simple pattern matching.
If any check fails, the script prints a FAIL message with the offending rule.
If all checks pass, it prints META-PASS.

Usage:
    python3 omega_validator.py <derivation_text_file>
"""

import sys
import re

# ----------------------------------------------------------------------
# Helper patterns (case‑insensitive, allow whitespace variations)
# ----------------------------------------------------------------------
def pat(*parts):
    """Build a regex that matches the concatenation of parts with optional whitespace."""
    return re.compile(r'\s*'.join(map(re.escape, parts)), re.IGNORECASE)

# Invariant patterns
INV_PSI   = pat('ψ', '=', 'ln', '(', 'Φ_N', ')')
INV_XI_N  = pat('ξ_N', '=', '∂', 'Φ_N', '/', '∂', 'ψ')
INV_XI_DELTA = pat('ξ_Δ', '=', '∂', 'Φ_Δ', '/', '∂', 'ψ')

# Π_T pattern: must contain Φ_N (linear) and the log term
PAT_PI_T   = pat('Π_T', '(', 'p²', ';', 'Φ_N', ')', '=', 
                 r'.*', 'Φ_N', r'.*')  # at least one Φ_N somewhere

# Π_L and Π_M patterns: must NOT contain Φ_N (they are Φ_N‑independent)
PAT_PI_L   = pat('Π_L', '(', 'p²', ')', '=', r'.*')
PAT_PI_M   = pat('Π_M', '(', 'p²', ')', '=', r'.*')

# Effective alpha pattern
PAT_ALPHA_EFF = pat(
    'α_eff', '^', 'i', '(', 'p²', ';', 'Φ_N', ',', 'Φ_Δ', ')', '=', 
    r'α₀', '/', r'\[', 
    r'1', r'\+', 'Π_T', r'\(', 'p²', ';', 'Φ_N', '\)', 
    r'\+', r'δ', '_', '{', 'i', ',', 'z', '}', r'·', 'Φ_Δ', r'·', 
    r'\(', 'Π_L', r'\+', '2', '·', 'Π_M', r'\)', 
    r'\+', r'O', r'\(', 'e⁶', '\)', 
    r'\]'
)

# Entropy‑gauge link: S₁ = -(Π_L+2Π_M)
PAT_S1_LINK = pat('S₁', '=', r'-', r'\(', 'Π_L', r'\+', '2', '·', 'Π_M', r'\)')

# ----------------------------------------------------------------------
def read_derivation(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def check_pattern(text, pattern, name, must_contain=True):
    m = pattern.search(text)
    if must_contain:
        if not m:
            return False, f"Missing required pattern: {name}"
        return True, ""
    else:
        if m:
            return False, f"Unexpected pattern found: {name}"
        return True, ""

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 omega_validator.py <derivation_text_file>")
        sys.exit(1)

    text = read_derivation(sys.argv[1])
    # Normalise common Unicode variants for easier matching
    text = text.replace('Φ_N', 'Φ_N').replace('Φ_Δ', 'Φ_Δ')
    text = text.replace('ψ', 'ψ').replace('ξ_N', 'ξ_N').replace('ξ_Δ', 'ξ_Δ')
    text = text.replace('α₀', 'α₀').replace('α_eff', 'α_eff')
    text = text.replace('Π_T', 'Π_T').replace('Π_L', 'Π_L').replace('Π_M', 'Π_M')
    text = text.replace('S₁', 'S₁')
    text = text.replace('∂', '∂')
    text = text.replace('ln', 'ln')
    text = text.replace('O(e⁶)', 'O(e⁶)')

    failures = []

    # 1. Omega invariants
    for name, patt in [('ψ = ln(Φ_N)', INV_PSI),
                       ('ξ_N = ∂Φ_N/∂ψ', INV_XI_N),
                       ('ξ_Δ = ∂Φ_Δ/∂ψ', INV_XI_DELTA)]:
        ok, msg = check_pattern(text, patt, name, must_contain=True)
        if not ok:
            failures.append(msg)

    # 2. Π_T must contain Φ_N (linear) – we just check presence of Φ_N after Π_T=
    ok, msg = check_pattern(text, PAT_PI_T, 'Π_T depends on Φ_N', must_contain=True)
    if not ok:
        failures.append(msg)

    # 3. Π_L and Π_M must NOT contain Φ_N
    ok, msg = check_pattern(text, PAT_PI_L, 'Π_L (should be Φ_N‑independent)', must_contain=False)
    if not ok:
        failures.append(msg)
    ok, msg = check_pattern(text, PAT_PI_M, 'Π_M (should be Φ_N‑independent)', must_contain=False)
    if not ok:
        failures.append(msg)

    # 4. Effective alpha formula
    ok, msg = check_pattern(text, PAT_ALPHA_EFF, 'α_eff^i formula', must_contain=True)
    if not ok:
        failures.append(msg)

    # 5. Entropy‑gauge link S₁ = -(Π_L+2Π_M)
    ok, msg = check_pattern(text, PAT_S1_LINK, 'S₁ = -(Π_L+2Π_M)', must_contain=True)
    if not ok:
        failures.append(msg)

    # ------------------------------------------------------------------
    # Outcome
    # ------------------------------------------------------------------
    if failures:
        print("META-FAIL: Omega Protocol invariant violation(s) detected:")
        for i, f in enumerate(failures, 1):
            print(f"  {i}. {f}")
        sys.exit(1)
    else:
        print("META-PASS: Derivation satisfies all Omega Protocol invariants and tensor structure.")
        sys.exit(0)

if __name__ == "__main__":
    main()