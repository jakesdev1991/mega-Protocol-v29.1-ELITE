# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol invariant checker for the Higher-Order Lattice Polarization
derivation.  Checks:
  - Mass-positivity:   Phi_N < (m/g) * exp(-|Phi_Delta|)
  - Perturbative control: eps * cosh(Phi_Delta) << 1
"""

import numpy as np

def check_invariants(m=1.0, g=0.1, A=0.5, p=1.0, beta=0.05,
                     eps=1e-4, t_max=200.0, dt=0.01):
    """
    Parameters
    ----------
    m, g : float
        Bare mass and coupling in m_e/p = m - g*Phi_N * exp(+/-Phi_Delta).
    A, p : float
        Amplitude and power-law exponent for Phi_N(t) = A * t**(-p)
        (static Poisson‑type recovery).
    beta : float
        Linear growth rate of Phi_Delta(t) = beta * t.
    eps  : float
        Expansion parameter epsilon = g*Phi_N/m (evaluated at t=0 for simplicity).
    t_max, dt : float
        Simulation horizon and time step.
    """
    times = np.arange(0.0, t_max, dt)
    for t in times:
        if t == 0.0:
            # avoid division by zero in power-law; use initial Phi_N = A * (t0)^(-p) with t0=dt
            Phi_N = A * (dt) ** (-p)
        else:
            Phi_N = A * (t ** (-p))
        Phi_Delta = beta * t

        # 1) Mass-positivity invariant
        rhs = (m / g) * np.exp(-abs(Phi_Delta))
        mass_ok = Phi_N < rhs

        # 2) Perturbative control invariant
        pert_ok = eps * np.cosh(Phi_Delta) < 0.5   # threshold for "<<" 1

        if not mass_ok or not pert_ok:
            print(f"\nInvariant violation at t = {t:.3f}")
            print(f"  Phi_N      = {Phi_N:.6e}")
            print(f"  Phi_Delta  = {Phi_Delta:.6e}")
            print(f"  RHS (mass) = {rhs:.6e}  --> mass_ok = {mass_ok}")
            print(f"  eps*cosh   = {eps*np.cosh(Phi_Delta):.6e}  --> pert_ok = {pert_ok}")
            return t, Phi_N, Phi_Delta, mass_ok, pert_ok

    print("No invariant violation detected up to t_max.")
    return t_max, None, None, True, True

if __name__ == "__main__":
    # Example parameter set (can be tweaked)
    t_viol, PhiN, PhiD, mass_ok, pert_ok = check_invariants()
    if t_viol < 200.0:
        print(f"\nFirst violation occurs at t ≈ {t_viol:.2f}")
    else:
        print("\nSystem remains within Omega Protocol invariants for the simulated duration.")