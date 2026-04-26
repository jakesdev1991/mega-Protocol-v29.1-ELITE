# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator – Higher-Order Lattice Polarization correction
"""

import ast
import re
import math
import sys

# --------------------------------------------------------------
# Configuration (Omega Protocol tolerances)
# --------------------------------------------------------------
ALPHA0 = 1.0 / 137.035999084  # CODATA 2018 fine-structure constant
ALPHA2 = ALPHA0 ** 2          # leading vacuum‑polarization scale
C_MAX  = 10.0                 # allow up to 10×α² as a generous higher‑order bound
ENTROPY_MIN = 0.85
FORBIDDEN_TOKENS = {"JET", "DIII-D", "tokamak", "disruption", "plasma"}  # inappropriate validators

# --------------------------------------------------------------
# Helper: parse Engine output (expects a single code block)
# --------------------------------------------------------------
def extract_code_block(text: str) -> str:
    """Return the first fenced python/cpp block; if none, return whole text."""
    pattern = r"```(?:[^\n\r]*\n)?([\s\S]*?)```"
    m = re.search(pattern, text)
    return m.group(1).strip() if m else text.strip()

# --------------------------------------------------------------
# Main validation routine
# --------------------------------------------------------------
def validate(engine_output: str) -> bool:
    code = extract_code_block(engine_output)
    print("\n=== Extracted Code Block ===\n")
    print(code)
    print("\n=== Validation ===")

    ok = True

    # 1. Look for the correction constant
    const_pattern = r"constexpr\s+double\s+ALPHA_FS_CORRECTION\s*=\s*([0-9.eE+\-]+)\s*;"
    m = re.search(const_pattern, code)
    if not m:
        print("[FAIL] No ALPHA_FS_CORRECTION constexpr found.")
        return False
    claimed = float(m.group(1))
    print(f"[INFO] Claimed Δα/α = {claimed:.6e}")

    # Bound check: must be positive and not exceed C_MAX * α²
    upper_bound = C_MAX * ALPHA2
    if claimed <= 0:
        print(f"[FAIL] Correction must be > 0 (got {claimed}).")
        ok = False
    elif claimed > upper_bound:
        print(f"[FAIL] Correction exceeds allowed bound "
              f"(> {C_MAX}·α² = {upper_bound:.3e}). Got {claimed:.3e}.")
        ok = False
    else:
        print(f"[PASS] Correction within [0, {upper_bound:.3e}].")

    # 2. Dimensional sanity: exponent argument must be dimensionless
    # Look for pattern exp(-k^2/(2*Lambda^2)) or similar
    exp_pattern = r"exp\s*\(\s*-\s*([^)]+)\s*\)"
    for exp in re.findall(exp_pattern, code, flags=re.IGNORECASE):
        # Expect something like k^2/(2*Lambda^2)
        if "k^2" in exp and "Lambda" in exp:
            # We cannot know dimensions of k or Lambda here; require an explicit scale comment
            if "dimensionless" not in code.lower() and "length scale" not in code.lower():
                print("[WARN] Exponent appears dimensionful; no explicit dimensionless comment found.")
                # Not a hard fail, but note.
        else:
            print(f"[INFO] Found exponential term: exp(-{exp})")

    # 3. Orthogonal decomposition: look for Phi_N * Phi_Delta == 0 (or similar)
    ortho_patterns = [
        r"Phi_N\s*\*\s*Phi_Delta\s*==\s*0",
        r"Phi_N\s*\*\s*Phi_Delta\s*=\s*0",
        r"orthogonal.*Phi_N.*Phi_Delta",
        r"Phi_N\s*·\s*Phi_Delta\s*=\s*0",
    ]
    ortho_ok = any(re.search(p, code, re.IGNORECASE) for p in ortho_patterns)
    if ortho_ok:
        print("[PASS] Orthogonality condition (Phi_N·Phi_Delta = 0) detected.")
    else:
        print("[FAIL] No explicit orthogonal decomposition statement found.")
        ok = False

    # 4. Entropy bound: must have a variable named entropy (or H) with value >= 0.85
    entropy_patterns = [
        r"(?:entropy|H)\s*=\s*([0-9.eE+\-]+)",
        r"H\s*=\s*-\s*\\sum.*ln",
    ]
    entropy_val = None
    for pat in entropy_patterns:
        m = re.search(pat, code, re.IGNORECASE)
        if m:
            try:
                entropy_val = float(m.group(1))
                break
            except ValueError:
                pass
    if entropy_val is None:
        print("[FAIL] No explicit entropy/H assignment found.")
        ok = False
    else:
        print(f"[INFO] Entropy/H = {entropy_val:.3f}")
        if entropy_val >= ENTROPY_MIN:
            print("[PASS] Entropy bound satisfied (H ≥ 0.85).")
        else:
            print(f"[FAIL] Entropy below minimum ({ENTROPY_MIN}).")
            ok = False

    # 5. Forbidden validation tokens (category error)
    for token in FORBIDDEN_TOKENS:
        if re.search(rf"\b{token}\b", code, re.IGNORECASE):
            print(f"[FAIL] Inappropriate validation reference: '{token}'.")
            ok = False

    # Summary
    print("\n=== RESULT ===")
    if ok:
        print("VALID – Engine output satisfies minimal Omega Protocol checks.")
    else:
        print("INVALID – One or more checks failed.")
    return ok

# --------------------------------------------------------------
# If run as script, read from stdin or first argument
# --------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = f.read()
    else:
        data = sys.stdin.read()
    sys.exit(0 if validate(data) else 1)