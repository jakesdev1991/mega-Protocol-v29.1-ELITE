# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Φ‑Density & Thermodynamic Breakdown Demo

This script shows:
1. Φ = log2(Betti/Shannon) is ill‑defined (negative, divergent) for plausible lattice parameters.
2. The Margolus‑Levitin bound for sub‑Planckian operations exceeds the Planck energy,
   violating the "Energetic Sufficiency" invariant.
3. The 1 % Planck bound is ~10^7 J, far too lax for any realistic sub‑Planckian device.
"""

import random
import math

# Constants (SI)
hbar = 1.054571817e-34  # J·s
c = 299792458           # m/s
G = 6.67430e-11         # m³·kg⁻¹·s⁻²
t_planck = 5.391247e-44 # s
E_planck = (hbar * c**5 / G)**0.5  # J

def compute_phi(betti: int, shannon: float) -> float:
    """Φ‑density as defined in the proposal."""
    if shannon <= 0:
        return float('inf')
    ratio = betti / shannon
    return math.log2(ratio)

def margolus_levitin_energy(tau: float) -> float:
    """
    Minimum energy required to perform a logical operation in time τ.
    E ≥ π·ħ / (2·τ)
    """
    return math.pi * hbar / (2 * tau)

def main():
    print("=== Φ‑Density Metric Breakdown ===\n")
    # Simulate 100 random lattices
    invalid = 0
    for i in range(100):
        betti = random.randint(1, 100)
        shannon = random.uniform(0.01, 10.0)  # realistic entropy range
        phi = compute_phi(betti, shannon)
        if phi < 0 or math.isinf(phi):
            invalid += 1
        # print a few examples
        if i < 5:
            print(f"Betti={betti:3d}, Shannon={shannon:6.3f} → Φ={phi:7.3f}")
    print(f"\nOut of 100 random lattices, {invalid} yielded Φ ≤ 0 or Φ → ∞.")
    print("Thus Φ is not a reliable density metric; it can be negative or diverge.\n")

    print("=== Energetic Sufficiency Invariant Failure ===\n")
    # Sub‑Planckian operation time (e.g., half a Planck time)
    tau_subplanck = 0.5 * t_planck
    E_min = margolus_levitin_energy(tau_subplanck)
    print(f"Planck time   : {t_planck:.3e} s")
    print(f"Operation time: {tau_subplanck:.3e} s")
    print(f"Margolus‑Levitin bound: E_min = {E_min:.3e} J")
    print(f"Planck energy : {E_planck:.3e} J")
    print(f"E_min / E_planck = {E_min / E_planck:.2e} (> 1 → exceeds Planck energy)\n")

    # The "1 % Planck" bound
    E_bound = 0.01 * E_planck
    print(f"Proposed energetic bound (1 % Planck): {E_bound:.3e} J")
    print(f"Bound / E_min = {E_bound / E_min:.2e} (<< 1 → bound is far too weak)\n")

    print("=== Conclusion ===")
    print("1. Φ‑density is ill‑defined and gauge‑dependent.")
    print("2. Sub‑Planckian operations require > Planck energy, violating the invariant.")
    print("3. The 1 % Planck bound is physically meaningless.")
    print("Hence the Ω‑Protocol’s Sub‑Planckian storage proposal is *unrealizable*.")

if __name__ == "__main__":
    main()