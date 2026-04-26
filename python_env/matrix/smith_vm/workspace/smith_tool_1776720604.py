# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol invariant validator for the Higher-Order Lattice Polarization
derivation.  Checks:
  1. Mass-positivity:   Phi_N < (m/g) * exp(-|Phi_Delta|)
  2. Perturbative control: eps * cosh(Phi_Delta) < threshold
where eps = g * Phi_N / m.
"""

import numpy as np

# ------------------- Model parameters (choose realistic values) -------------------
m   = 1.0          # bare mass scale (sets units)
g   = 0.1          # coupling constant
PhiN0 = 0.5        # initial consensus field amplitude
p   = 1.0          # power-law decay exponent for Phi_N(t) = PhiN0 * (1 + t/t0)^(-p)
t0  = 1.0          # characteristic time for power-law decay
beta = 0.2         # linear growth rate of Phi_Delta: Phi_Delta(t) = beta * t
# Perturbative threshold (conservative)
pert_thresh = 0.1  # we require eps*cosh(Phi_Delta) < pert_thresh
# Simulation settings
t_max = 50.0       # max simulation time
dt    = 0.01       # time step

# ------------------- Helper functions -------------------
def Phi_N(t):
    """Power‑law decay (static Poisson‑type recovery)."""
    return PhiN0 * (1.0 + t / t0) ** (-p)

def Phi_Delta(t):
    """Linear growth (can be changed to exponential if desired)."""
    return beta * t

def mass_positivity_holds(t):
    """Return True if Phi_N < (m/g) * exp(-|Phi_Delta|)."""
    lhs = Phi_N(t)
    rhs = (m / g) * np.exp(-abs(Phi_Delta(t)))
    return lhs < rhs

def perturbative_holds(t):
    """Return True if eps * cosh(Phi_Delta) < pert_thresh."""
    eps = g * Phi_N(t) / m
    return eps * np.cosh(Phi_Delta(t)) < pert_thresh

# ------------------- Main loop -------------------
violation_time = None
violation_type = None

times = np.arange(0.0, t_max, dt)
for t in times:
    if not mass_positivity_holds(t):
        violation_time = t
        violation_type = "mass-positivity"
        break
    if not perturbative_holds(t):
        violation_time = t
        violation_type = "perturbative"
        break

# ------------------- Output -------------------
if violation_time is None:
    print(f"No invariant violation detected up to t = {t_max:.2f}")
else:
    print(f"Invariant violation at t = {violation_time:.3f}")
    print(f"  Type: {violation_type}")
    print(f"  Phi_N   = {Phi_N(violation_time):.6e}")
    print(f"  Phi_D   = {Phi_Delta(violation_time):.6e}")
    print(f"  RHS of mass-positivity = {(m/g)*np.exp(-abs(Phi_Delta(violation_time))):.6e}")
    print(f"  eps*cosh = {(g*Phi_N(violation_time)/m)*np.cosh(Phi_Delta(violation_time)):.6e}")