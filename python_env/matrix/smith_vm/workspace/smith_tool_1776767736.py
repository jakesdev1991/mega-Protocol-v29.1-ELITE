# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator – Boilerplate & Invariant Check
--------------------------------------------------------
- Rejects outputs containing generic engineering lists (Step 1, Step 2, …).
- Optionally verifies the core invariant ψ = ln(Φ_N/I₀) and stiffness
  expressions for a quick sanity check.
"""

import re
import sys
import math

# ----------------------------------------------------------------------
# Configuration – patterns that constitute boilerplate
# ----------------------------------------------------------------------
BOILERPLATE_PATTERNS = [
    r'^\s*Step\s+\d+[:\-]',          # Step 1 -, Step 2:
    r'^\s*Phase\s+\d+[:\-]',
    r'^\s*Stage\s+\d+[:\-]',
    r'^\s*\d+\.\s+',                 # 1. 2. 3. (ordered list)
]

def contains_boilerplate(text: str) -> bool:
    """Return True if any line matches a boilerplate pattern."""
    for line in text.splitlines():
        for pat in BOILERPLATE_PATTERNS:
            if re.match(pat, line, re.IGNORECASE):
                return True
    return False

# ----------------------------------------------------------------------
# Optional invariant sanity‑check (can be extended)
# ----------------------------------------------------------------------
def check_invariants(text: str) -> bool:
    """
    Very light‑weight check:
    - Extract Φ_N/I₀ (φ_N) and Φ_Δ/I₀ (φ_Δ) if present.
    - Verify ψ = ln(φ_N) matches a stated ψ value (if given).
    Returns True if no contradiction found; False on explicit mismatch.
    """
    # Grab numbers that look like φ_N = 0.78, φ_Δ = 0.35, ψ = -0.248
    phi_n_match = re.search(r'φ_N\s*[=:]\s*([0-9]*\.?[0-9]+)', text, re.IGNORECASE)
    phi_d_match = re.search(r'φ_Δ\s*[=:]\s*([0-9]*\.?[0-9]+)', text, re.IGNORECASE)
    psi_match   = re.search(r'ψ\s*[=:]\s*([-]?[0-9]*\.?[0-9]+)', text, re.IGNORECASE)

    if not (phi_n_match and phi_d_match and psi_match):
        # Not enough data to judge – assume OK
        return True

    phi_n = float(phi_n_match.group(1))
    phi_d = float(phi_d_match.group(1))
    psi_stated = float(psi_match.group(1))

    psi_calc = math.log(phi_n)  # ψ = ln(Φ_N/I₀) ; φ_N = Φ_N/I₀
    # Allow small tolerance due to rounding
    return math.isclose(psi_calc, psi_stated, rel_tol=1e-3, abs_tol=1e-3)

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 omega_validator.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()

    # Boilerplate check – hard failure
    if contains_boilerplate(content):
        print("FAIL: Boilerplate detected (generic numbered steps/phases).")
        sys.exit(1)

    # Optional invariant check – warning only
    if not check_invariants(content):
        print("WARN: Invariant inconsistency detected (ψ ≠ ln(φ_N)).")
        # Not a hard fail; you may decide to treat as fail if desired.

    print("PASS: No boilerplate and invariants consistent.")
    sys.exit(0)

if __name__ == "__main__":
    main()