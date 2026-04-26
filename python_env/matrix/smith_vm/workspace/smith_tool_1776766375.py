# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol RG validator for the (Phi_N, Phi_Delta) system.
Detects premature Shredding (finite‑scale divergence) and checks
the Poisson‑recovery invariant (Phi_N > 0).
"""

import numpy as np
from scipy.integrate import solve_ivp

def rg_system(L, y, eta_N, eta_Delta, kappa, gamma=0.0, I0=1.0):
    """
    y[0] = Phi_N, y[1] = Phi_Delta
    gamma = entropy‑gauge damping coefficient (>=0)
    """
    PhiN, PhiD = y
    # RG beta‑functions with optional gauge damping
    beta_N = eta_N * PhiN * (1 - (PhiN**2)/(I0**2)) - kappa * PhiD**2
    beta_D = eta_Delta * PhiD * (1 - (PhiD**2)/(I0**2)) + kappa * PhiN * PhiD - gamma * PhiD
    return [beta_N, beta_D]

def validate_flow(eta_N, eta_Delta, kappa,
                 gamma=0.0,
                 PhiN0=0.1, PhiD0=0.1,
                 L_start=0.0, L_stop=20.0,
                 max_step=1e-3,
                 bound=1e6):
    """
    Integrates d y/d L = RG. Returns (is_bounded, reason).
    is_bounded = True  → no premature Shredding up to L_stop.
    """
    def event_blowup(L, y):
        # stop if either component exceeds bound in magnitude
        return np.max(np.abs(y)) - bound
    event_blowup.terminal = True
    event_blowup.direction = 0

    sol = solve_ivp(rg_system,
                    [L_start, L_stop],
                    [PhiN0, PhiD0],
                    args=(eta_N, eta_Delta, kappa, gamma),
                    max_step=max_step,
                    events=[event_blowup],
                    rtol=1e-9, atol=1e-12)

    if sol.t_events[0].size > 0:
        Lc = sol.t_events[0][0]
        PhiN_c, PhiD_c = sol.y_events[0][0]
        reason = (f"Blow‑up at Lc={Lc:.4f}: "
                  f"Phi_N={PhiN_c:.3e}, Phi_Delta={PhiD_c:.3e}")
        return False, reason

    # Additionally check Poisson‑recovery invariant: Phi_N must stay >0
    if np.any(sol.y[0] <= 0):
        idx = np.where(sol.y[0] <= 0)[0][0]
        Lneg = sol.t[idx]
        reason = (f"Phi_N became non‑positive at L={Lneg:.4f} "
                  f"(value={sol.y[0][idx]:.3e})")
        return False, reason

    return True, "Flow remained bounded and Phi_N>0 up to L_stop."

# ----------------------------------------------------------------------
# Example usage: test the original Shredding parameter set
if __name__ == "__main__":
    eta_N   = 0.1          # arbitrary positive Newtonian coupling
    eta_D   = -0.2         # <-- triggers the cubic drive (Shredding)
    kappa   = 0.05
    gamma   = 0.0          # no entropy‑gauge damping (as in the derivation)

    bounded, msg = validate_flow(eta_N, eta_D, kappa, gamma=gamma,
                                 PhiN0=0.05, PhiD0=0.05,
                                 L_stop=30.0)
    print("Shredding test (no gauge):", bounded)
    print(msg)

    # Now add a modest entropy‑gauge damping term
    gamma = 0.1
    bounded2, msg2 = validate_flow(eta_N, eta_D, kappa, gamma=gamma,
                                   PhiN0=0.05, PhiD0=0.05,
                                   L_stop=30.0)
    print("\nWith entropy‑gauge damping (gamma=0.1):", bounded2)
    print(msg2)