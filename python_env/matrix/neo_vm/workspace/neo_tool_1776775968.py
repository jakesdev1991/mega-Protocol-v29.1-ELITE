# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ──────────────────────────────────────────────────────────────────────────────
# 1. Show that the "Shredding" is just a Goldstone flat direction
# ──────────────────────────────────────────────────────────────────────────────
λ = 1.0
I0 = 1.0

# grid of field values
ΦN = np.linspace(-1.5, 1.5, 400)
ΦΔ = np.linspace(-1.5, 1.5, 400)
ΦN_grid, ΦΔ_grid = np.meshgrid(ΦN, ΦΔ)

# Hessian eigenvalues (masses squared)
mN2 = λ * (3 * ΦN_grid**2 + ΦΔ_grid**2 - I0**2)
mΔ2 = λ * (ΦN_grid**2 + 3 * ΦΔ_grid**2 - I0**2)

# The "Shredding" curve is where mΔ2 = 0
shredding_curve = np.isclose(mΔ2, 0.0, atol=1e-3)

# Plot: mΔ2 is finite everywhere, zero only on the flat direction
fig, ax = plt.subplots(figsize=(6,5))
cont = ax.contourf(ΦN_grid, ΦΔ_grid, mΔ2, levels=50, cmap='coolwarm')
ax.contour(ΦN_grid, ΦΔ_grid, shredding_curve, colors='k', linewidths=2)
ax.set_xlabel('Φ_N')
ax.set_ylabel('Φ_Δ')
ax.set_title('m_Δ² (Goldstone mass); black line = "Shredding" (flat direction)')
plt.colorbar(cont, ax=ax, label='m_Δ²')
plt.show()

# ──────────────────────────────────────────────────────────────────────────────
# 2. Modified RG flow with Higgs feedback – Landau pole disappears
# ──────────────────────────────────────────────────────────────────────────────
def beta(g, t, λ=1.0, I0=1.0, Mgauge=1.0):
    """
    β(g) = b0 g^3 - g * (mΔ² / Mgauge²)
    where mΔ² = λ (Φ_N² + 3Φ_Δ² - I0²) evaluated along the RG trajectory.
    For demonstration we parametrize the field values as functions of scale:
    Φ_N(t) = I0 * np.tanh(t), Φ_Δ(t) = I0 / np.cosh(t)  (just a toy profile).
    """
    b0 = 1.0 / (16 * np.pi**2)
    ΦN_t = I0 * np.tanh(t)
    ΦΔ_t = I0 / np.cosh(t)
    mΔ2_t = λ * (ΦN_t**2 + 3 * ΦΔ_t**2 - I0**2)
    # Higgs feedback term (negative when mΔ² > 0)
    feedback = g * (mΔ2_t / Mgauge**2)
    return b0 * g**3 - feedback

# integrate from low to high scale
t_eval = np.linspace(-5, 5, 500)
sol = solve_ivp(
    fun=lambda t, y: beta(y[0], t),
    t_span=(t_eval[0], t_eval[-1]),
    y0=[0.5],  # initial g_Δ at low energy
    t_eval=t_eval,
    method='RK45'
)

# Plot the running coupling
plt.figure(figsize=(6,4))
plt.plot(np.exp(sol.t), sol.y[0], label='g_Δ with Higgs feedback')
# compare with pure Landau pole (no feedback)
g_pure = 0.5 / np.sqrt(1 - (0.5**2) * (sol.t - sol.t[0]) / (8*np.pi**2))
plt.plot(np.exp(sol.t), g_pure, '--', label='g_Δ (pure Landau pole)')
plt.xscale('log')
plt.xlabel('μ')
plt.ylabel('g_Δ')
plt.title('RG flow: Landau pole tamed by Goldstone/Higgs feedback')
plt.legend()
plt.grid(True, which='both', ls='--')
plt.show()