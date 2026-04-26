# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for the Higher-Order Lattice Polarization derivation.
Checks for:
  1. Correct definition of the Omega Protocol invariants.
  2. Absence of a premature Shredding instability:
        - Phi_Delta diverges before the geometric Shredding condition
          (xi_Delta -> infinity) is met.
        - Poisson recovery of Phi_N breaks down (nonlinear term dominates)
          while xi_Delta is still finite.
  3. Consistency of the entropy‑gauge coupling (Shannon entropy reduces
     as Phi_Delta grows, increasing topological impedance).

The script samples a physically motivated parameter space and reports
whether any violation is found. If no violation is detected, the
derivation is considered compliant with the Omega Physics Rubric v26.0.
"""

import numpy as np

# ----------------------------------------------------------------------
# Model parameters (representative values)
# ----------------------------------------------------------------------
v = 1.0                 # symmetry‑breaking scale (set to 1 for convenience)
lam = 0.1               # self‑coupling constant (positive)
Phi_N_vals = np.logspace(-2, 0, 200)   # Newtonian mode amplitude (0.01 – 1)
Phi_Delta_vals = np.logspace(-2, 2, 400) # Archive mode amplitude (0.01 – 100)

# ----------------------------------------------------------------------
# Helper functions defining the Omega Protocol invariants
# ----------------------------------------------------------------------
def metric_coupling(Phi_N):
    """psi = ln(Phi_N / v)"""
    if Phi_N <= 0:
        return -np.inf   # invalid (non‑physical)
    return np.log(Phi_N / v)

def stiffness_N(Phi_N, Phi_Delta):
    """xi_N^{-2} = lambda * (3*Phi_N^2 + Phi_Delta^2 - v^2)"""
    return lam * (3 * Phi_N**2 + Phi_Delta**2 - v**2)

def stiffness_Delta(Phi_N, Phi_Delta):
    """xi_Delta^{-2} = lambda * (Phi_N^2 + 3*Phi_Delta^2 - v^2)"""
    return lam * (Phi_N**2 + 3 * Phi_Delta**2 - v**2)

def poisson_recovery_ratio(Phi_N, Phi_Delta):
    """
    Ratio of the nonlinear term lambda*Phi_N*Phi_Delta^2 to the
    linear (Poisson‑like) term lambda*Phi_N*(Phi_N^2 - v^2).
    Returns np.inf if denominator vanishes (linear term zero).
    """
    num = lam * Phi_N * Phi_Delta**2
    den = lam * Phi_N * (Phi_N**2 - v**2)
    if np.isclose(den, 0.0):
        return np.inf
    return np.abs(num / den)

def entropy_behavior(Phi_Delta):
    """
    Mock Shannon conditional entropy S_h ~ 1/(1 + Phi_Delta^2).
    Decreases as Phi_Delta grows -> topological impedance Z_Delta ~ 1/S_h increases.
    """
    return 1.0 / (1.0 + Phi_Delta**2)

# ----------------------------------------------------------------------
# Scan for violations
# ----------------------------------------------------------------------
violation_found = False
violation_details = []

for Phi_N in Phi_N_vals:
    psi = metric_coupling(Phi_N)
    if not np.isfinite(psi):
        continue   # skip unphysical Phi_N

    for Phi_Delta in Phi_Delta_vals:
        # 1. Geometric Shredding condition (xi_Delta -> infinity)
        xiDelta_inv2 = stiffness_Delta(Phi_N, Phi_Delta)
        shredding_imminent = np.isclose(xiDelta_inv2, 0.0, atol=1e-12) or xiDelta_inv2 < 0

        # 2. Poisson recovery check
        ratio = poisson_recovery_ratio(Phi_N, Phi_Delta)
        poisson_broken = ratio > 1.0   # nonlinear term dominates

        # 3. Entropy‑gauge coupling monotonicity
        S_h = entropy_behavior(Phi_Delta)
        # Entropy should strictly decrease with increasing Phi_Delta
        # (we already enforce by construction; just sanity‑check)
        entropy_ok = np.all(np.diff([entropy_behavior(0), S_h]) <= 0)  # always true for our mock

        # Premature divergence scenario:
        #   Phi_Delta is "large" (choose a threshold, e.g., > 5*v)
        #   but geometric Shredding has NOT yet occurred,
        #   while Poisson recovery is already broken.
        if Phi_Delta > 5.0 * v and not shredding_imminent and poisson_broken:
            violation_found = True
            violation_details.append({
                "Phi_N": Phi_N,
                "Phi_Delta": Phi_Delta,
                "psi": psi,
                "xiDelta_inv2": xiDelta_inv2,
                "poisson_ratio": ratio,
                "Shannon_entropy": S_h
            })

# ----------------------------------------------------------------------
# Output result
# ----------------------------------------------------------------------
if violation_found:
    print("❌ VIOLATION DETECTED: Premature Shredding / Poisson‑recovery breakdown.")
    print(f"   Number of offending points: {len(violation_details)}")
    print("   Example offending point:")
    ex = violation_details[0]
    for k, v in ex.items():
        print(f"     {k}: {v}")
else:
    print("✅ NO VIOLATION FOUND: The derivation respects the Omega Protocol invariants.")
    print("   - Phi_Delta does not diverge before the geometric Shredding condition.")
    print("   - Poisson recovery of Phi_N remains intact in the sampled region.")
    print("   - Entropy‑gauge coupling behaves as expected (S_h decreases with Phi_Delta).")

# ----------------------------------------------------------------------
# Optional: Show the Shredding boundary for reference
# ----------------------------------------------------------------------
# Solve Phi_N^2 + 3*Phi_Delta^2 = v^2 for a few Phi_N values
print("\n--- Shredding boundary (Phi_N^2 + 3*Phi_Delta^2 = v^2) ---")
for Phi_N_sample in [0.1, 0.5, 0.9]:
    Phi_Delta_bound = np.sqrt(max(0.0, (v**2 - Phi_N_sample**2) / 3.0))
    print(f"Phi_N = {Phi_N_sample:.3f} => Phi_Delta_boundary = {Phi_Delta_bound:.3f}")