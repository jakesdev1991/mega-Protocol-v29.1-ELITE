# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Invariant & Mathematical Soundness Validator
-----------------------------------------------------------
Usage:
    python validate_omega.py <path_to_derivation_text>
The script exits with status 0 only if ALL checks pass.
"""

import sys
import re
import math

# ----------------------------------------------------------------------
# CONFIGURATION – Omega Protocol required symbols
# ----------------------------------------------------------------------
REQUIRED_SYMBOLS = {
    r'\\?Phi_N',          # \Phi_N or Φ_N
    r'\\?Phi_Delta',      # \Phi_\Delta or Φ_Δ
    r'\\?psi',            # \psi or ψ
    r'\\?xi_N',           # \xi_N or ξ_N
    r'\\?xi_Delta',       # \xi_\Delta or ξ_Δ
    r'\\?J_star',         # J* (allow asterisk)
}
REQUIRED_ENTROPY = {
    r'entropy',
    r'Shannon',
    r'topological\s+impedance',
    r'conditional\s+entropy',
}
# ----------------------------------------------------------------------


def load_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def check_symbols(text: str) -> bool:
    """Return True if every required symbol appears at least once."""
    missing = []
    for pat in REQUIRED_SYMBOLS:
        if not re.search(pat, text, flags=re.IGNORECASE):
            missing.append(pat)
    if missing:
        print(f"[FAIL] Missing Omega symbols: {missing}")
        return False
    print("[PASS] All Omega symbols present.")
    return True


def check_entropy(text: str) -> bool:
    """Return True if any entropy‑related term appears."""
    found = any(re.search(pat, text, flags=re.IGNORECASE) for pat in REQUIRED_ENTROPY)
    if not found:
        print("[FAIL] No entropy / Shannon / topological impedance term found.")
        return False
    print("[PASS] Entropy reference detected.")
    return True


def extract_one_loop_coeff(text: str) -> float:
    """
    Attempt to pull the coefficient of the log term in the claimed
    one‑loop QED vacuum polarization.
    Accepts patterns like:
        + (alpha0/(3*pi))*log(...)
        - (alpha0/(3*pi))*log(...)
        + alpha0/(3π) ln(...)
    Returns the signed coefficient as a float.
    """
    # Normalise pi and π
    txt = text.replace('π', 'pi')
    # Look for a term containing alpha0/(something)*log or ln
    pattern = r'([+-]?)\s*alpha0\s*/\s*([0-9.\*]+)\s*pi\s*[*/]\s*[lg]n?\s*\('
    m = re.search(pattern, txt, flags=re.IGNORECASE)
    if not m:
        # fallback: try to capture the fraction directly after alpha0
        pattern2 = r'alpha0\s*/\s*([0-9.\*]+)\s*pi'
        m2 = re.search(pattern2, txt, flags=re.IGNORECASE)
        if not m2:
            raise ValueError("Could not locate one‑loop α₀/(…π) term.")
        # Assume positive sign if not explicitly preceded by a minus
        sign = '+' if m2.start() == 0 or txt[m2.start()-1] not in '+-' else txt[m2.start()-1]
        coeff = 1.0 / float(m2.group(1).replace('*', ''))
        return coeff if sign == '+' else -coeff

    sign, denom = m.groups()
    sign = sign or '+'
    coeff = 1.0 / float(denom.replace('*', ''))
    return coeff if sign == '+' else -coeff


def check_one_loop_sign(text: str) -> bool:
    """
    In QED with a UV cutoff (or MS-bar) the vacuum polarization
    Π_QED(q²) = + (α₀/3π) ln(−q²/m²) + … .
    Hence the coefficient of the log must be **positive**.
    """
    try:
        coeff = extract_one_loop_coeff(text)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return False

    # Tolerance for floating‑point noise
    if math.isclose(coeff, 0.0, abs_tol=1e-12):
        print("[FAIL] Extracted coefficient is zero.")
        return False
    if coeff > 0:
        print(f"[PASS] One‑loop QED coefficient = {coeff:+.6f} (positive as required).")
        return True
    else:
        print(f"[FAIL] One‑loop QED coefficient = {coeff:+.6f} (should be positive).")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_omega.py <derivation_file>")
        sys.exit(1)

    text = load_text(sys.argv[1])

    # Run all checks; any failure aborts with non‑zero exit.
    ok = True
    ok &= check_symbols(text)
    ok &= check_entropy(text)
    ok &= check_one_loop_sign(text)

    if ok:
        print("\n[RESULT] All Omega‑Protocol invariants and basic mathematical checks PASSED.")
        sys.exit(0)
    else:
        print("\n[RESULT] Validation FAILED – derivation non‑compliant.")
        sys.exit(1)


if __name__ == "__main__":
    main()