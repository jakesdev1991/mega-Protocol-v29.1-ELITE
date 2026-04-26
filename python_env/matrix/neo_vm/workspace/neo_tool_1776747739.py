# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.integrate as integrate

# Ground state wavefunction of quantum harmonic oscillator (sigma = 1/√2 for natural units)
def psi_ground(x, sigma=1/np.sqrt(2)):
    return (1/(np.pi**0.25 * np.sqrt(sigma))) * np.exp(-x**2/(2*sigma**2))

# Shannon differential entropy for a continuous probability distribution p(x)
def shannon_entropy(p_func, x_range=8, num_points=20000):
    xs = np.linspace(-x_range, x_range, num_points)
    p = p_func(xs)
    # Normalize to a proper probability density
    norm = np.trapz(p, xs)
    p = p / norm
    # Avoid log(0) by thresholding
    p_safe = np.where(p > 1e-15, p, 1e-15)
    S = -np.trapz(p_safe * np.log(p_safe), xs)
    return S

# Von Neumann entropy of a pure state is identically zero
def von_neumann_entropy():
    return 0.0

# Compute the entropies
S_shannon = shannon_entropy(psi_ground)
S_vn = von_neumann_entropy()

print(f"Shannon (differential) entropy: {S_shannon:.5f} bits")
print(f"Von Neumann (quantum) entropy: {S_vn} bits")
print("\nConclusion: A pure quantum vacuum has zero quantum entropy but non-zero Shannon entropy.")
print("Requiring Shannon entropy for gauge emergence is a category error that cannot be satisfied.")