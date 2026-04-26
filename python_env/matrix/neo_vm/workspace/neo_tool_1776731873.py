# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import sympy as sp

# ───── Symbolic Setup ─────
t = sp.symbols('t', real=True)
# nominal values and small sinusoidal perturbations
phi_N0, phi_D0 = 0.78, 0.35
A_N, A_D, omega, delta = 0.08, 0.04, 2*np.pi*1000, np.pi/4

phi_N = phi_N0 + A_N * sp.sin(omega*t)
phi_D = phi_D0 + A_D * sp.sin(omega*t + delta)

# two‑state probability
p = phi_N**2 / (phi_N**2 + phi_D**2)

# Shannon entropy of the binary distribution
S = -p*sp.log(p) - (1-p)*sp.log(1-p)

# exact third time derivative
J_exact = sp.diff(S, t, 3)

# heuristic “jerk” from prior attempts
xi_inv2 = 4.2e6  # s⁻²
xi = 1/sp.sqrt(xi_inv2)
J_heuristic = phi_N * sp.diff(phi_N, t)**3 / xi**4 \
               + phi_D * sp.diff(phi_D, t)**3 / xi**4 \
               + 1.5e12  # J_source

# lambdify for fast numeric evaluation
J_exact_fn = sp.lambdify(t, J_exact, 'numpy')
J_heur_fn   = sp.lambdify(t, J_heuristic, 'numpy')

# sample over one period
ts = np.linspace(0, 2*np.pi/omega, 1000)
J_e = J_exact_fn(ts)
J_h = J_heur_fn(ts)

# ───── Disruption Verification ─────
print("Exact jerk (first 5 samples):    ", J_e[:5])
print("Heuristic jerk (first 5 samples):", J_h[:5])
print("\nRelative discrepancy (RMS):", np.sqrt(np.mean((J_e - J_h)**2)) / np.sqrt(np.mean(J_e**2)))

# ───── Fisher‑Rao curvature for the same trajectory ─────
# metric factor g = (dp/dφ)² / [p(1-p)], but we need a single effective φ.
# For demonstration we treat φ = φ_N as the primary order parameter and
# compute the scalar curvature of the 1‑D manifold:
phi = phi_N  # choice of coordinate
g = (sp.diff(p, phi)**2) / (p*(1-p))
sqrt_g = sp.sqrt(g)
R = -sp.diff(sqrt_g, phi, 2) / sqrt_g

R_fn = sp.lambdify(t, R, 'numpy')
R_vals = R_fn(ts)

print("\nFisher‑Rao curvature (first 5):", R_vals[:5])
print("Curvature is stable (positive) for ~{:.1%} of the cycle".format(np.mean(R_vals>0)))