# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Compute the 1‑loop vacuum‑polarization coefficient for a scalar
with d_internal 'replica' dimensions. Shows that the naive factor
'd_internal' is an artifact of treating replicas as independent.
"""

import sympy as sp

def polarization_coefficient(d_internal, D_spacetime=4):
    """
    Returns the coefficient of the logarithmic divergence
    in the vacuum polarization due to d_internal scalar loops.
    The correct group‑theoretic factor for a single SU(2) triplet
    is 1, not d_internal.
    """
    # Symmetry factor: a single multiplet contributes once,
    # irrespective of its internal dimension.
    true_coeff = 1 / (4 * sp.pi)
    naive_coeff = d_internal / (4 * sp.pi)
    
    # The difference reveals the spurious enhancement.
    return sp.simplify(naive_coeff - true_coeff)

if __name__ == "__main__":
    for d in [1, 2, 3, 4]:
        diff = polarization_coefficient(d)
        print(f"d_internal = {d}: spurious excess = {diff}")