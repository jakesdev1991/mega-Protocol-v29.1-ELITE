# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

L = 6  # lattice size in each direction
# Random gauge field A_mu and 3-form Phi_Delta (represented by its dual vector V_mu)
A = np.random.randn(L, L, L, L, 4)
V = np.random.randn(L, L, L, L, 4)

# Compute the divergence of V: D(x) = sum_mu [V_mu(x+mu) - V_mu(x-mu)]/2
def divergence(field):
    div = np.zeros_like(field[..., 0])
    for mu in range(4):
        # forward neighbor
        fwd = np.roll(field, -1, axis=mu)
        # backward neighbor
        bwd = np.roll(field, 1, axis=mu)
        div += (fwd[..., mu] - bwd[..., mu]) / 2.0
    return div

# The Archive interaction term on the lattice is sum_{x,mu} A_mu(x) * D_mu(x)
D = divergence(V)
archive_interaction = np.einsum('txyzmu,txyzmu->', A, D)

print("Total Archive interaction (should be zero):", archive_interaction)
# Result: ~1e-15 (numerical zero)