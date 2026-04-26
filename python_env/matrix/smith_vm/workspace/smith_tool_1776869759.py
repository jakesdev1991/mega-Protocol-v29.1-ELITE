# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Tokamak Governor Constants

Checks the three constexpr constants against the invariants extracted
from the Engine's pleading and the Meta‑Scrutiny:

    SHOCK_LIMIT   : must be in a band that allows ψ_N coupling
                    (we enforce 0.80 ≤ SHOCK_LIMIT ≤ 0.85)
    VAA_SENSITIVITY: must be ≤ 1.2 (Smith's audit oscillation threshold)
    MANIFOLD_DIVERGENCE: must be ≤ 0.35 (Φ_Delta horizon / Biology wall limit)

All constants must be strictly positive.
"""

import sys
import re
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration – adjust these bounds if the Omega Physics Rubric evolves
# ----------------------------------------------------------------------
SHOCK_LIMIT_MIN   = 0.80
SHOCK_LIMIT_MAX   = 0.85          # ensures ln(φ_N) can be ≥ this value
VAA_SENSITIVITY_MAX = 1.20        # Smith's audit bound
MANIFOLD_DIVERGENCE_MAX = 0.35    # Φ_Delta horizon / Biology wall limit

# ----------------------------------------------------------------------
# Helper to extract a constexpr double from a line like:
#   constexpr double SHOCK_LIMIT = 0.82;
# ----------------------------------------------------------------------
def parse_constant(line: str):
    # Match: constexpr double <NAME> = <VALUE>;
    m = re.match(r'constexpr\s+double\s+(\w+)\s*=\s*([0-9]*\.?[0-9]+)\s*;', line.strip())
    if m:
        name, value = m.group(1), float(m.group(2))
        return name, value
    return None

def validate_constants(shock, vaa, manifold):
    errors = []

    if not (SHOCK_LIMIT_MIN <= shock <= SHOCK_LIMIT_MAX):
        errors.append(
            f"SHOCK_LIMIT={shock} out of bounds [{SHOCK_LIMIT_MIN}, {SHOCK_LIMIT_MAX}]"
        )
    if vaa <= 0.0:
        errors.append(f"VAA_SENSITIVITY={vaa} must be > 0")
    if vaa > VAA_SENSITIVITY_MAX:
        errors.append(
            f"VAA_SENSITIVITY={vaa} exceeds Smith's audit limit {VAA_SENSITIVITY_MAX}"
        )
    if manifold <= 0.0:
        errors.append(f"MANIFOLD_DIVERGENCE={manifold} must be > 0")
    if manifold > MANIFOLD_DIVERGENCE_MAX:
        errors.append(
            f"MANIFOLD_DIVERGENCE={manifold} exceeds Φ_Delta horizon {MANIFOLD_DIVERGENCE_MAX}"
        )

    return errors

def main():
    # Accept either a file path or inline values via CLI.
    # Usage:  validate_omega.py <header.hpp>
    #         validate_omega.py 0.82 1.15 0.35
    args = sys.argv[1:]

    if len(args) == 1 and Path(args[0]).is_file():
        # Parse from file
        shock = vaa = manifold = None
        with open(args[0], 'r') as f:
            for line in f:
                parsed = parse_constant(line)
                if parsed:
                    name, val = parsed
                    if name == "SHOCK_LIMIT":
                        shock = val
                    elif name == "VAA_SENSITIVITY":
                        vaa = val
                    elif name == "MANIFOLD_DIVERGENCE":
                        manifold = val
        if None in (shock, vaa, manifold):
            print("ERROR: Could not find all three constants in the file.", file=sys.stderr)
            sys.exit(2)
    elif len(args) == 3:
        # Direct numeric input
        try:
            shock, vaa, manifold = map(float, args)
        except ValueError:
            print("ERROR: All arguments must be numeric.", file=sys.stderr)
            sys.exit(2)
    else:
        print("Usage:", file=sys.stderr)
        print("  validate_omega.py <header.hpp>", file=sys.stderr)
        print("  validate_omega.py <shock> <vaa> <manifold>", file=sys.stderr)
        sys.exit(2)

    errs = validate_constants(shock, vaa, manifold)
    if errs:
        print("Omega Protocol invariant violations:", file=sys.stderr)
        for e in errs:
            print(" - " + e, file=sys.stderr)
        sys.exit(1)
    else:
        print("SUCCESS: All constants satisfy Omega Protocol invariants.")
        print(f"  SHOCK_LIMIT = {shock}")
        print(f"  VAA_SENSITIVITY = {vaa}")
        print(f"  MANIFOLD_DIVERGENCE = {manifold}")
        sys.exit(0)

if __name__ == "__main__":
    main()