# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for the Higher‑Order Lattice Polarization derivation.

Checks:
  1. Individual fermion mass positivity  (m_e > 0, m_p > 0)
  2. Effective mass reality (m_eff real and > 0)
  3. Perturbative expansion parameter < 1
  4. Lattice anisotropy spacing positivity for all directions
  5. Poisson‑recovery source term well‑defined (no zero lattice spacing)

Usage:
    python omega_validator.py  --PhiN <value> --PhiDelta <value> \
                               --g <value> --m <value> \
                               --epsilons <list> [--Q2 <value>] [--alpha0 <value>]

If all checks pass, the script exits with code 0 (PASS). Otherwise it prints
the violated condition(s) and exits with code 1 (FAIL).
"""

import argparse
import math
import sys
from typing import List

def parse_args():
    p = argparse.ArgumentParser(description="Omega Protocol validator")
    p.add_argument("--PhiN", type=float, required=True, help="Φ_N (scalar field)")
    p.add_argument("--PhiDelta", type=float, required=True, help="Φ_Δ (anisotropy field)")
    p.add_argument("--g", type=float, required=True, help="Coupling g")
    p.add_argument("--m", type=float, required=True, help="Bare mass m")
    p.add_argument("--epsilons", type=float, nargs="+", required=True,
                   help="List of anisotropy coefficients ε_i (must sum to zero)")
    p.add_argument("--Q2", type=float, default=0.0,
                   help="Spacelike momentum squared Q^2 (default 0 for static check)")
    p.add_argument("--alpha0", type=float, default=1/137.0,
                   help="Bare fine‑structure constant α0")
    return p.parse_args()

def mass_positivity(PhiN: float, PhiDelta: float, g: float, m: float) -> bool:
    """Both m_e and m_p must be > 0."""
    me = m - g * PhiN * math.exp(+PhiDelta)
    mp = m - g * PhiN * math.exp(-PhiDelta)
    return me > 0 and mp > 0

def effective_mass(PhiN: float, PhiDelta: float, g: float, m: float) -> float:
    """m_eff = sqrt(m_e * m_p) – returns real positive value if masses positive."""
    me = m - g * PhiN * math.exp(+PhiDelta)
    mp = m - g * PhiN * math.exp(-PhiDelta)
    prod = me * mp
    if prod <= 0:
        raise ValueError(f"Product m_e*m_p = {prod} ≤ 0 → m_eff not real")
    return math.sqrt(prod)

def expansion_parameter(PhiN: float, PhiDelta: float, g: float, m: float) -> float:
    """Exact loop expansion parameter that appears in the vacuum‑polarisation series:
       ε_eff = (g Φ_N / m) * cosh(Φ_Δ) = ε * cosh(Φ_Δ)."""
    eps = g * PhiN / m
    return eps * math.cosh(PhiDelta)

def lattice_spacings(PhiDelta: float, a0: float, epsilons: List[float]) -> List[float]:
    """a_i = a0 * (1 + ε_i * Φ_Δ)."""
    return [a0 * (1.0 + ei * PhiDelta) for ei in epsilons]

def poisson_source_well_def(epsilons: List[float], PhiDelta: float, a0: float) -> bool:
    """The source term for Φ_N involves ∇^2 Φ_N ∝ δm_eff.
       If any lattice spacing goes to zero, the momentum measure diverges → ill‑posed.
       We simply require all a_i > 0."""
    spacings = lattice_spacings(PhiDelta, a0, epsilons)
    return all(s > 0 for s in spacings)

def main():
    args = parse_args()

    # Basic sanity: ε_i must sum to zero (as per the ansatz)
    if not math.isclose(sum(args.epsilons), 0.0, abs_tol=1e-12):
        print(f"FAIL: Σ ε_i = {sum(args.epsilons)} ≠ 0 (required by ansatz).")
        sys.exit(1)

    # 1. Mass positivity
    if not mass_positivity(args.PhiN, args.PhiDelta, args.g, args.m):
        print("FAIL: Individual fermion mass positivity violated.")
        sys.exit(1)

    # 2. Effective mass reality & positivity
    try:
        m_eff = effective_mass(args.PhiN, args.PhiDelta, args.g, args.m)
    except ValueError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    if m_eff <= 0:
        print(f"FAIL: Effective mass m_eff = {m_eff} ≤ 0.")
        sys.exit(1)

    # 3. Perturbative expansion parameter < 1
    eps_eff = expansion_parameter(args.PhiN, args.PhiDelta, args.g, args.m)
    if eps_eff >= 1.0:
        print(f"FAIL: Expansion parameter ε_eff = {eps_eff:.6f} ≥ 1 (perturbation breaks down).")
        sys.exit(1)

    # 4. Lattice anisotropy – choose a convenient a0 = 1 (scale‑independent check)
    a0 = 1.0
    spacings = lattice_spacings(args.PhiDelta, a0, args.epsilons)
    if any(s <= 0 for s in spacings):
        print(f"FAIL: Lattice spacing non‑positive for some direction: {spacings}")
        sys.exit(1)

    # 5. Poisson‑recovery source term well‑defined
    if not poisson_source_well_def(args.epsilons, args.PhiDelta, a0):
        print("FAIL: Poisson‑recovery source ill‑posed (zero lattice spacing detected).")
        sys.exit(1)

    # Optional: show the one‑loop vacuum‑polarisation coefficient for given Q2
    if args.Q2 > 0:
        coeff = args.alpha0 * args.Q2 / (90.0 * math.pi * m_eff**2)
        print(f"INFO: One‑loop Π(-Q^2)-Π(0) coefficient = {coeff:.6e} (Q^2={args.Q2})")

    print("PASS: All Omega Protocol invariants satisfied.")
    sys.exit(0)

if __name__ == "__main__":
    main()