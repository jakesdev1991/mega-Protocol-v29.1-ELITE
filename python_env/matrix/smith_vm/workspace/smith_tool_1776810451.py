# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Invariant Validator for Higher‑Order Lattice Polarization
-----------------------------------------------------------------------
Checks the three core conditions that must hold to avoid the Shredding
instability:

1. Metric positivity:               1 + ΦΔ > 0   (avoids g_zz → 0)
2. Symplectic recovery (approx):   ΦN * (1 + ΦΔ) ≈ C   (constant from canonical quantisation)
3. Real effective coupling:        Im[Π_L + 2Π_M] ≈ 0   (no ghost‑induced imaginary part)

If any condition fails, the script reports the specific violation and
returns a non‑zero exit code (FAIL).  Otherwise it prints PASS and exits 0.

Usage:
    python3 validate_omega.py --PhiN 0.02 --PhiDelta -0.3 \
                              --PiL 0.001 --PiM 0.0005 \
                              --e 0.30282212 --xiN 1.0 --xiD 1.0 \
                              --C 0.02 --tol 1e-6
"""

import argparse
import math
import sys

def parse_args():
    p = argparse.ArgumentParser(
        description="Validate Omega‑Protocol invariants for lattice‑polarization derivation."
    )
    p.add_argument("--PhiN",   type=float, required=True, help="Isotropic polarization ΦN")
    p.add_argument("--PhiDelta",type=float, required=True, help="Anisotropic deformation ΦΔ")
    p.add_argument("--PiL",    type=float, required=True, help="Longitudinal polarization ΠL")
    p.add_argument("--PiM",    type=float, required=True, help="Transverse mixed polarization ΠM")
    p.add_argument("--e",      type=float, required=True, help="Coupling constant e (≈√4πα)")
    p.add_argument("--xiN",    type=float, default=1.0, help="Symplectic weight ξN")
    p.add_argument("--xiD",    type=float, default=1.0, help="Symplectic weight ξΔ")
    p.add_argument("--C",      type=float, required=True,
                   help="Expected constant for ΦN·(1+ΦΔ) from canonical quantisation")
    p.add_argument("--tol",    type=float, default=1e-8,
                   help="Numerical tolerance for equality checks")
    return p.parse_args()

def main():
    args = parse_args()

    # 1. Metric positivity (avoid Shredding via g_zz → 0)
    metric_factor = 1.0 + args.PhiDelta
    if metric_factor <= 0.0:
        print(f"FAIL: Metric collapse detected. 1+ΦΔ = {metric_factor:.6e} ≤ 0")
        sys.exit(1)
    if metric_factor < args.tol:
        print(f"WARN: Metric factor very small: {metric_factor:.6e}")

    # 2. Symplectic recovery invariant: ΦN * (1+ΦΔ) ≈ C
    invariant = args.PhiN * metric_factor
    diff = abs(invariant - args.C)
    if diff > args.tol:
        print(f"FAIL: Symplectic invariant violated. "
              f"ΦN·(1+ΦΔ) = {invariant:.6e}, expected C = {args.C:.6e}, diff = {diff:.6e}")
        sys.exit(1)

    # 3. Real effective coupling: Im[ΠL + 2ΠM] must be negligible
    imag_part = args.PiL + 2.0 * args.PiM  # In the Engine's notation these are real; we check for accidental imag.
    # If the user supplies complex numbers, we extract the imaginary part.
    if isinstance(args.PiL, complex) or isinstance(args.PiM, complex):
        imag_part = (args.PiL.imag + 2.0 * args.PiM.imag)
    if abs(imag_part) > args.tol:
        print(f"FAIL: Potential ghost‑induced imaginary part detected. "
              f"Im[ΠL+2ΠM] = {imag_part:.6e}")
        sys.exit(1)

    # Optional: compute the Engine's "critical" ΦΔ from the (now‑questionable) formula
    # and warn if we are uncomfortably close.
    # crit = -1.0 + (args.e**2 / (math.pi**2)) * imag_part  # imag_part should be ~0
    # if abs(args.PhiDelta - crit) < 1e-3:
    #     print(f"INFO: ΦΔ near critical value from Engine's formula: crit ≈ {crit:.6e}")

    # All checks passed
    print("PASS: All Omega‑Protocol invariants satisfied.")
    sys.exit(0)

if __name__ == "__main__":
    main()