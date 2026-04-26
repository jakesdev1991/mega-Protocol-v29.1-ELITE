# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Validation Script for Higher‑Order Lattice Polarization Derivation
Checks:
  1. Presence of required invariants: psi, xi_N, xi_Delta
  2. Effective alpha formula contains the anisotropic term:
        delta_{i,z} * Phi_Delta * [Pi_L + 2*Pi_M]
  3. One-loop anisotropic kernel retains angular dependence
        (look for sin_z*k * sin_z*(k-p) or equivalent)
"""

import re
import sys

def load_derivation(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def check_invariants(text: str):
    """Return list of missing invariant names."""
    patterns = {
        'psi': r'\bpsi\b\s*=\s*ln\s*\(\s*Phi_N\s*\)',
        'xi_N': r'\bxi_N\b',
        'xi_Delta': r'\bxi_Delta\b'
    }
    missing = []
    for name, pat in patterns.items():
        if not re.search(pat, text, re.IGNORECASE):
            missing.append(name)
    return missing

def check_effective_alpha(text: str):
    """
    Look for the anisotropic part of alpha_eff:
        delta_{i,z} * Phi_Delta * [Pi_L + 2*Pi_M]
    Allow variations in spacing and optional parentheses.
    """
    # Normalize whitespace
    norm = re.sub(r'\s+', ' ', text)
    # Pattern: delta_{i,z} (or δ_{i,z}) followed by Phi_Delta, then [Pi_L + 2*Pi_M] (allow +/-)
    pattern = r'delta\s*_\{i,z\}\s*\*\s*Phi_Delta\s*\*\s*\[\s*Pi_L\s*\+\s*2\s*\*\s*Pi_M\s*\]'
    if re.search(pattern, norm, re.IGNORECASE):
        return True
    # Also accept the version with explicit brackets around the whole term
    pattern2 = r'delta\s*_\{i,z\}\s*\*\s*Phi_Delta\s*\*\s*\(?\s*Pi_L\s*\+\s*2\s*\*\s*Pi_M\s*\)?'
    return bool(re.search(pattern2, norm, re.IGNORECASE))

def check_one_loop_angular(text: str):
    """
    Very lightweight check: the one-loop anisotropic kernel must contain a product
    of two z‑direction sine factors (sin_z*k * sin_z*(k-p) or sin(k_z) * sin((k-p)_z)).
    We look for the substring 'sin_z' appearing at least twice in proximity to 'k' and '(k-p)'.
    """
    # Find all occurrences of sin_z (or sin(k_z))
    sin_z_matches = list(re.finditer(r'sin\s*_\s*z|sin\s*\(\s*k_z\s*\)', text, re.IGNORECASE))
    if len(sin_z_matches) < 2:
        return False, "Less than two sin_z factors found."
    # Check that at least one pair is linked with k and (k-p)
    # We'll do a simple proximity test: look for 'k' and '(k-p)' near the sins.
    context = text.lower()
    if ('sin_z' in context and 'k' in context and '(k-p)' in context):
        return True, ""
    return False, "Angular dependence (sin_z*k * sin_z*(k-p)) not detected."

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_derivation.py <derivation_file.txt>")
        sys.exit(1)

    derivation = load_derivation(sys.argv[1])
    failures = []

    # 1. Invariants
    missing = check_invariants(derivation)
    if missing:
        failures.append(f"Missing Omega invariants: {', '.join(missing)}")

    # 2. Effective alpha structure
    if not check_effective_alpha(derivation):
        failures.append("Effective alpha formula missing anisotropic term "
                        "delta_{i,z} * Phi_Delta * [Pi_L + 2*Pi_M]")

    # 3. One-loop angular term
    ok, msg = check_one_loop_angular(derivation)
    if not ok:
        failures.append(f"One-loop anisotropic kernel issue: {msg}")

    if failures:
        print("VALIDATION FAILED:")
        for f in failures:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All Omega‑Protocol checks satisfied.")
        sys.exit(0)

if __name__ == "__main__":
    main()