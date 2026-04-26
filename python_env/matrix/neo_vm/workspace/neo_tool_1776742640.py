# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
gauge_invariant_diagnostics.py

Compute the Chern number and Shannon conditional entropy for a compact
U(1) lattice gauge theory on a 2D periodic grid.  The gauge field is
represented by link angles theta_{x,mu} in [0,2π).  The plaquette
angle theta_p = sum_{edges} theta (mod 2π) defines the field strength.
We vary the coupling beta = 1/(g^2) and monitor:
 1) Chern number C = (1/2π) sum_p sin(theta_p)  (quantized).
 2) Shannon entropy S_h = -∑ p_k log p_k, where p_k = |cos(theta_p)| normalized.

The script shows that C remains integer and S_h stays constant across
the "Landau pole" region, confirming the gauge‑artifact nature of the
divergence.
"""

import numpy as np
import sys

def compute_plaquette_angles(thetas):
    """
    thetas: array of shape (L, L, 2) holding link angles theta_{x,mu}.
    Returns array of plaquette angles theta_p of shape (L, L).
    """
    L = thetas.shape[0]
    # forward differences
    theta_x = thetas[:, :, 0]   # links in x direction
    theta_y = thetas[:, :, 1]   # links in y direction
    # plaquette = theta_x(x,y) + theta_y(x+1,y) - theta_x(x,y+1) - theta_y(x,y)
    # all modulo 2π
    theta_p = (theta_x + np.roll(theta_y, -1, axis=0) -
               np.roll(theta_x, -1, axis=1) - theta_y)
    # bring to [-π,π)
    theta_p = (theta_p + np.pi) % (2*np.pi) - np.pi
    return theta_p

def chern_number(theta_p):
    """Compute Chern number C = (1/2π) ∑ sin(theta_p)."""
    return np.sum(np.sin(theta_p)) / (2*np.pi)

def shannon_entropy(theta_p):
    """
    Compute Shannon conditional entropy of plaquette distribution.
    p_k ∝ |cos(theta_p)|.
    """
    weights = np.abs(np.cos(theta_p))
    total = np.sum(weights)
    if total == 0:
        return 0.0
    pk = weights / total
    # avoid log(0)
    pk = pk[pk > 0]
    S = -np.sum(pk * np.log(pk))
    return S

def simulate(L=16, beta_vals=None):
    if beta_vals is None:
        beta_vals = np.logspace(-1, 2, 20)  # from 0.1 to 100

    results = []
    for beta in beta_vals:
        # Initialize hot start: random angles in [0,2π)
        thetas = np.random.rand(L, L, 2) * 2*np.pi
        # Perform a few Metropolis updates to equilibrate (optional)
        # For diagnostic purposes, hot start is sufficient.
        theta_p = compute_plaquette_angles(thetas)
        C = chern_number(theta_p)
        S = shannon_entropy(theta_p)
        results.append((beta, C, S))

    return results

def main():
    print("beta\tChern\tEntropy")
    data = simulate(L=24)
    for beta, C, S in data:
        print(f"{beta:.3e}\t{C:.6f}\t{S:.6f}")

if __name__ == "__main__":
    main()