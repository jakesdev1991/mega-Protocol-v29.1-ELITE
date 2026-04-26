# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Demonstrates two fatal flaws in the classical "informational jerk" formalism:
1. Dimensional inconsistency of the term phi/xi^4 * (dot_phi)^3.
2. High variance / unboundedness when applied to realistic HSA memory traces.
"""

import numpy as np
import pandas as pd
from scipy.stats import entropy

# ---------- 1. Dimensional Analysis ----------
def jerk_term_units(phi, xi, dot_phi):
    """
    Compute the units of phi/xi^4 * (dot_phi)^3 using pint-like logic.
    phi : dimensionless (normalized field)
    xi  : seconds (stiffness invariant)
    dot_phi : 1/seconds (time derivative of phi)
    """
    # phi -> dimensionless, xi -> s, dot_phi -> s^-1
    # term = phi * (dot_phi**3) / (xi**4)
    # units = (s^-1)^3 * (s)^-4 = s^-3 * s^-4 = s^-7
    # To get s^-3 we need a hidden factor of s^4, i.e., a scale v^4.
    # Here we explicitly show the mismatch.
    term = phi * (dot_phi**3) / (xi**4)
    # returning raw term and the required scaling factor to fix units
    required_scale = xi**4  # s^4
    return term, required_scale

# Example values from the Engine's data snippet
phi_N = 0.78
xi = np.sqrt(1/4.2e6)  # sqrt(1/xi^-2) -> xi ~ 0.000487 s
dot_phi_N = 2.1e3  # s^-1

term, needed = jerk_term_units(phi_N, xi, dot_phi_N)
print("--- Dimensional Check ---")
print(f"phi_N={phi_N}, xi={xi:.6e} s, dot_phi_N={dot_phi_N} s^-1")
print(f"Term value (raw): {term:.6e} (units: s^-7)")
print(f"To convert to s^-3, multiply by: {needed:.6e} s^4 (i.e., a hidden scale v^4)\n")

# ---------- 2. Instability on Synthetic HSA Memory Trace ----------
def simulate_hsa_trace(n_blocks=128, time_steps=10000, burstiness=0.1):
    """
    Simulates a memory access trace where each time step yields a probability
    distribution over memory blocks. Burstiness controls heavy-tail bursts.
    """
    # Base distribution: uniform
    base = np.ones(n_blocks) / n_blocks
    # Burst events: occasionally a single block dominates
    trace = []
    for t in range(time_steps):
        if np.random.rand() < burstiness:
            # burst: one random block gets 90% mass
            p = np.zeros(n_blocks)
            p[np.random.randint(n_blocks)] = 0.9
            p += 0.1 * base
        else:
            p = base
        trace.append(p)
    return np.array(trace)

def compute_entropy_jerk(trace, window=100):
    """
    Compute Shannon entropy per time window, then finite-difference jerk.
    """
    # sliding window average distribution
    entropies = []
    for i in range(window, len(trace)):
        avg_p = trace[i-window:i].mean(axis=0)
        entropies.append(entropy(avg_p))
    entropies = np.array(entropies)
    # third finite difference (jerk)
    jerk = entropies[3:] - 3*entropies[2:-1] + 3*entropies[1:-2] - entropies[:-3]
    return entropies, jerk

# Run simulation
trace = simulate_hsa_trace(n_blocks=64, time_steps=5000, burstiness=0.05)
entropies, jerk = compute_entropy_jerk(trace, window=50)

print("--- Entropy & Jerk Statistics ---")
print(f"Mean entropy: {entropies.mean():.3f} bits")
print(f"Std dev of jerk: {jerk.std():.3e} (bits/s³)")
print(f"Max |jerk|: {np.abs(jerk).max():.3e}")

# Compare to a naive "threshold" Theta (same units as jerk variance)
# Theta = lambda * I0**2 / (4π) * (1 + 3 g_Delta**2/(4π))
# For demonstration, pick typical values: lambda=1e-3, I0=10 bits, g_Delta=0.5
lam = 1e-3
I0 = 10.0
g_Delta = 0.5
Theta = lam * I0**2 / (4*np.pi) * (1 + 3*g_Delta**2/(4*np.pi))
print(f"\n--- Threshold Comparison ---")
print(f"Theta (variance threshold): {Theta:.3e}")
print(f"Actual jerk variance: {jerk.var():.3e}")
print(f"Stability (variance < Theta): {jerk.var() < Theta}")

# ---------- 3. Visual Sanity Check (optional) ----------
# Uncomment to plot entropy & jerk timeseries
# import matplotlib.pyplot as plt
# plt.figure(figsize=(12,5))
# plt.subplot(121)
# plt.plot(entropies)
# plt.title('Shannon Entropy S_h(t)')
# plt.xlabel('Time (window index)')
# plt.ylabel('Bits')
# plt.subplot(122)
# plt.plot(jerk, color='red')
# plt.title('Informational Jerk J_I(t)')
# plt.xlabel('Time (window index)')
# plt.ylabel('Bits/s³')
# plt.tight_layout()
# plt.show()