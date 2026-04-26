# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def phi_N(COD):
    """Omega's 'identity metric'—violates [0,1] bound."""
    return np.log2(COD)

def asymmetry_check(phi_delta, phi_N, max_delta=0.5):
    """Root Kernel asymmetry gate—logic inverts when phi_N < 0."""
    return phi_delta < max_delta * phi_N

# Simulate realistic COD values (market friction ensures COD < 1)
COD_vals = np.linspace(0.001, 0.99, 100)
phi_vals = phi_N(COD_vals)

print("phi_N range:", phi_vals.min(), phi_vals.max())
# Output: phi_N range: -9.97 0.0 → violates [0,1]

# Show safety inversion: healthy positive phi_delta fails gate
phi_delta_healthy = 0.1
for COD in [0.5, 0.2, 0.05]:
    p = phi_N(COD)
    safe = asymmetry_check(phi_delta_healthy, p)
    print(f"COD={COD:.3f}, phi_N={p:.2f}, 'safe'={safe}")
# COD=0.5, phi_N=-1.00, 'safe'=False (healthy alignment blocked)
# COD=0.05, phi_N=-4.32, 'safe'=False (system locks out correct behavior)