# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ── Given data (dimensionless fields, rates in s⁻¹) ──
phi_N = 0.78
phi_D = 0.35
dot_phi_N = 2.1e3
dot_phi_D = 8.7e3
xi_inv_sq = 4.2e6           # s⁻²
xi = 1/np.sqrt(xi_inv_sq)   # s

# ── Heuristic “jerk” (dimensionally inconsistent) ──
J_heuristic = (3*phi_D / xi**4) * dot_phi_D**3 - (phi_N / xi**4) * dot_phi_N**3
print(f"Heuristic J = {J_heuristic:.3e} s⁻⁷  ← wrong units, nonsense magnitude")

# ── Source term for comparison ──
J_source = 1.5e12            # s⁻³
print(f"Source J    = {J_source:.3e} s⁻³")
print(f"Ratio (heuristic / source) = {J_heuristic / J_source:.3e} (orders of magnitude off)\n")

# ── True entropy dynamics (two‑state memory model) ──
t = np.linspace(0, 1e-3, 50000)          # 1 ms window
f = 5000                                 # 5 kHz access oscillation
phi_N_t = phi_N * np.sin(2*np.pi*f*t) + 0.5
phi_D_t = phi_D * np.cos(2*np.pi*f*t) + 0.5

# Probabilities from field magnitudes
p_N = phi_N_t**2 / (phi_N_t**2 + phi_D_t**2)
p_D = phi_D_t**2 / (phi_N_t**2 + phi_D_t**2)

# Shannon entropy
S = -p_N*np.log(p_N) - p_D*np.log(p_D)

# Third derivative via finite differences (true “informational jerk”)
dt = t[1] - t[0]
dS_dt  = np.gradient(S, dt)
d2S_dt2 = np.gradient(dS_dt, dt)
d3S_dt3 = np.gradient(d2S_dt2, dt)

print(f"Max |d³S/dt³| from entropy = {np.max(np.abs(d3S_dt3)):.3e} s⁻³")

# ── Fisher information rate (the correct metric) ──
dot_p_N = np.gradient(p_N, dt)
dot_p_D = np.gradient(p_D, dt)
Fisher_rate = (dot_p_N**2 / (p_N + 1e-12)) + (dot_p_D**2 / (p_D + 1e-12))
print(f"Max Fisher information rate = {np.max(Fisher_rate):.3e} s⁻²  ← well‑behaved, dimensionally sound")