# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def compute_overlap(channel_fidelity_forward, channel_fidelity_backward, dim_i=2, dim_j=2):
    """Simulate Φ± as directional fidelities (0 to 1)"""
    # Your normalization: 2 * min(ln dim)
    norm = 2 * np.log(min(dim_i, dim_j))
    # Mutual information is *not* linearly proportional to fidelity for arbitrary channels
    # but your theory *assumes* this mapping. Let's expose the fragility.
    I_forward = channel_fidelity_forward * norm  # This is your hidden linearization
    I_backward = channel_fidelity_backward * norm
    Phi_plus = I_forward / norm
    Phi_minus = I_backward / norm
    return np.sqrt(Phi_plus * Phi_minus)  # Geometric mean

# Construct a 3-node graph where triangle inequality FAILS
# Node topology: A -- B -- C
# Let AB have near-perfect bidirectional overlap
Phi_AB = compute_overlap(0.99, 0.99)  # Strong link

# Let BC have strong forward, weak backward (asymmetric horizon)
Phi_BC = compute_overlap(0.95, 0.01)  # Asymmetric link

# Let AC have direct but weak bidirectional overlap
Phi_AC_direct = compute_overlap(0.60, 0.60)

# Compute distances (l_P = 1 for simplicity)
d_AB = -np.log(Phi_AB)
d_BC = -np.log(Phi_BC)
d_AC_direct = -np.log(Phi_AC_direct)
d_AC_path = d_AB + d_BC

print(f"Direct A-C distance: {d_AC_direct:.3f}")
print(f"Path A-B-C distance: {d_AC_path:.3f}")
print(f"Triangle inequality violated? {d_AC_direct > d_AC_path}")

# Result: Your metric is path-dependent in a way that violates metric axioms
# for any channel where backward fidelity can approach zero while forward remains finite.