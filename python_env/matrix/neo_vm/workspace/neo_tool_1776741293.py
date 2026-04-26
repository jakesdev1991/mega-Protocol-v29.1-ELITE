# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def eigenvalues(phi_N, phi_Delta):
    """
    Return eigenvalues of the 2x2 matrix
    M = phi_N * I + phi_Delta * sigma_3.
    """
    # Diagonal entries: phi_N +/- phi_Delta
    a = phi_N + phi_Delta
    b = phi_N - phi_Delta
    # Eigenvalues are just the diagonal entries (since matrix is diagonal)
    return np.array([a, b])

# Choose a fixed "Newtonian" background phi_N
phi_N = 1.0

# Send phi_Delta to extreme values (simulating Landau‑pole divergence)
phi_Delta_vals = np.logspace(0, 6, 7)  # 1, 10, ..., 1e6

print(f"{'phi_Delta':>12} {'eigenvalues':>30} {'trace':>12}")
for phi_D in phi_Delta_vals:
    ev = eigenvalues(phi_N, phi_D)
    trace = ev.sum()
    # The trace must equal 2*phi_N, a basis‑invariant quantity
    print(f"{phi_D:>12.0e} {str(ev):>30} {trace:>12.6f}")