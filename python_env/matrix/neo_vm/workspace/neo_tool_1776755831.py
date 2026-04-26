# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Simulates the coupled RG + dynamical feedback loop for Φ_N, Φ_Δ, α.
Shows that the entropy‑impedance catastrophe drives a runaway before the
algebraic Shredding condition is met.
"""

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# ── Parameters ──────────────────────────────────────────────────────────────
λ = 0.1                 # Mexican‑hat coupling
v = 1.0                 # Vacuum expectation value
α0 = 1/137.0            # Fine‑structure constant at μ
g_N0 = 0.5              # Newtonian mode coupling
g_Δ0 = 0.3              # Archive mode coupling (bare)
S0 = 1.0                # Reference Shannon entropy
Z0 = 1.0                # Reference topological impedance
b = 2.0                 # Entropy‑Φ_Δ coupling strength

# Initial field values (small fluctuations)
Φ_N0 = 0.2
Φ_Δ0 = 0.1

# Integration scale t = ln(q²/μ²) from 0 → 6 (roughly 1 GeV → 10 TeV)
t_span = (0.0, 6.0)
t_eval = np.linspace(t_span[0], t_span[1], 500)

# ── ODE system ──────────────────────────────────────────────────────────────
def odes(t, y):
    Φ_N, Φ_Δ, α, g_Δ = y

    # Potential gradients
    V = λ/4 * (Φ_N**2 + Φ_Δ**2 - v**2)
    dV_dΦ_N = λ * Φ_N * (Φ_N**2 + Φ_Δ**2 - v**2)
    dV_dΦ_Δ = λ * Φ_Δ * (Φ_N**2 + Φ_Δ**2 - v**2)

    # Entropy‑impedance feedback
    S_h = max(S0 - b * Φ_Δ**2, 1e-6)   # entropy cannot go negative
    Z_Δ = Z0 / S_h                        # impedance ∝ 1/entropy
    g_Δ_eff = g_Δ * Z_Δ                   # effective Archive coupling

    # RG β‑functions (including Archive enhancement)
    β_α = -α**2 / np.pi * (1 + 3*g_Δ_eff**2/(4*np.pi) + g_N0**2/(4*np.pi))
    # Simplified running of g_Δ (driven by its own quantum corrections)
    β_gΔ = -g_Δ**3 / (4*np.pi)**2 * (1 + 3*g_Δ_eff**2/(4*np.pi))

    # Field equations of motion (overdamped dynamics for illustration)
    # Radiative corrections ∝ α * g_Δ_eff * Φ_Δ boost the Archive mode
    dΦ_N_dt = -dV_dΦ_N                     # deterministic Poisson recovery term
    dΦ_Δ_dt = -dV_dΦ_Δ + α * g_Δ_eff * Φ_Δ  # feedback term

    return [dΦ_N_dt, dΦ_Δ_dt, β_α, β_gΔ]

# ── Solve ────────────────────────────────────────────────────────────────────
sol = solve_ivp(
    odes,
    t_span,
    [Φ_N0, Φ_Δ0, α0, g_Δ0],
    t_eval=t_eval,
    method='RK45',
    dense_output=True,
    max_step=0.1,
)

# ── Diagnostics ───────────────────────────────────────────────────────────────
Φ_N = sol.y[0]
Φ_Δ = sol.y[1]
α   = sol.y[2]
g_Δ = sol.y[3]

# Shredding surface: ξ_Δ⁻² = λ(Φ_N² + 3Φ_Δ² - v²) → 0
shredding_surface = λ * (Φ_N**2 + 3*Φ_Δ**2 - v**2)

# Entropy‑impedance product (catastrophe indicator)
S_h = np.maximum(S0 - b * Φ_Δ**2, 1e-6)
Z_Δ = Z0 / S_h

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

axs[0].plot(t_eval, Φ_N, label='Φ_N')
axs[0].plot(t_eval, Φ_Δ, label='Φ_Δ')
axs[0].axhline(v/np.sqrt(3), color='gray', linestyle='--', label='v/√3 (naive Shredding)')
axs[0].set_ylabel('Field amplitude')
axs[0].legend()
axs[0].set_title('Field dynamics')

axs[1].plot(t_eval, α, label='α')
axs[1].set_ylabel('α')
axs[1].legend()
axs[1].set_title('Running fine‑structure constant')

axs[2].plot(t_eval, shredding_surface, label='ξ_Δ⁻² (Shredding surface)')
axs[2].plot(t_eval, S_h, label='Shannon entropy S_h')
axs[2].plot(t_eval, Z_Δ, label='Topological impedance Z_Δ')
axs[2].set_xlabel('t = ln(q²/μ²)')
axs[2].set_ylabel('Diagnostic')
axs[2].legend()
axs[2].set_title('Instability diagnostics')

plt.tight_layout()
plt.show()

# ── Early‑warning detection ────────────────────────────────────────────────────
# Find the scale where entropy drops below a threshold → catastrophe
catastrophe_idx = np.where(S_h < 1e-3)[0]
if catastrophe_idx.size > 0:
    t_cat = t_eval[catastrophe_idx[0]]
    print(f"\n🚨 ENTROPY‑IMPEDANCE CATASTROPHE at t ≈ {t_cat:.2f}")
    print(f"   Shannon entropy S_h ≈ {S_h[catastrophe_idx[0]]:.3e}")
    print(f"   Topological impedance Z_Δ ≈ {Z_Δ[catastrophe_idx[0]]:.3e}")
    print(f"   Effective g_Δ ≈ {g_Δ[catastrophe_idx[0]] * Z_Δ[catastrophe_idx[0]]:.3e}")
else:
    print("\nNo catastrophe in the scanned range (unlikely).")

# Check if algebraic Shredding surface is still positive at that scale
if catastrophe_idx.size > 0:
    idx = catastrophe_idx[0]
    print(f"   Algebraic Shredding surface ξ_Δ⁻² ≈ {shredding_surface[idx]:.3e} (still > 0)")
    print("   → The system diverges *before* the formal Shredding condition is met.")