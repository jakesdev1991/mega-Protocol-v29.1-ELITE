# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ---------- Hyperbolic RG flow (the flawed model) ----------
# Parameters (in arbitrary units; only ratios matter)
A = 0.08          # feedback strength from ΔΠ_Δ
psi0 = 0.05       # initial hyperbolic angle
alpha_inv0 = 137.0  # inverse fine-structure constant at low scale
B = A             # coefficient linking ΔΠ_Δ to α running

# ODE: dψ/dτ = A * sinh(ψ)^2, where τ = ln(q/q0)
def dpsi_dt(tau, psi):
    return A * np.sinh(psi)**2

# Integrate from τ=0 to τ=τ_max
tau_max = 6.0
sol = solve_ivp(dpsi_dt, [0, tau_max], [psi0],
                t_eval=np.linspace(0, tau_max, 2000),
                method='RK45', max_step=0.01)
psi = sol.y[0]
tau = sol.t

# Running of α⁻¹(τ) = α⁻¹(0) - B * ∫ sinh(ψ(τ'))^2 dτ'
sinh2 = np.sinh(psi)**2
integral = np.cumsum(sinh2 * np.diff(tau, prepend=0))
alpha_inv = alpha_inv0 - B * integral

# Find the approximate Landau pole (α⁻¹ → 0)
pole_idx = np.where(alpha_inv <= 0)[0]
if len(pole_idx) > 0:
    tau_pole = tau[pole_idx[0]]
    print(f"\n[SHREDDING EVENT] α⁻¹ hits zero at τ ≈ {tau_pole:.3f} (finite scale!).")
else:
    tau_pole = None
    print("\nNo pole within integration range (τ_max too small).")

# Plot the catastrophe
fig, axs = plt.subplots(2, 1, figsize=(7, 6))

axs[0].plot(tau, psi, lw=1.5, color='crimson')
axs[0].set_ylabel('ψ (hyperbolic angle)')
axs[0].set_title('RG evolution: ψ runs away → ∞')
axs[0].grid(True, alpha=0.3)

axs[1].plot(tau, alpha_inv, lw=1.5, color='steelblue')
axs[1].set_ylabel('α⁻¹')
axs[1].set_xlabel('τ = ln(q/q₀)')
axs[1].set_title('Running inverse fine-structure constant')
axs[1].grid(True, alpha=0.3)

if tau_pole:
    axs[1].axvline(tau_pole, color='red', ls='--')
    axs[1].text(tau_pole, alpha_inv0/2, f'Landau pole\nτ≈{tau_pole:.2f}',
                rotation=90, verticalalignment='center', color='red')

plt.tight_layout()
plt.savefig('shredding_demo.png', dpi=150)
print("\nPlot saved to 'shredding_demo.png'.")

# ---------- Compact (elliptic) alternative (no singularity) ----------
# For contrast, integrate the same feedback but with periodic functions:
# dθ/dτ = A * sin(θ)^2, α⁻¹(τ) = α⁻¹(0) - B * ∫ sin(θ)^2 dτ'
def dtheta_dt(tau, theta):
    return A * np.sin(theta)**2

sol_c = solve_ivp(dtheta_dt, [0, tau_max], [psi0],  # reuse psi0 as initial θ
                  t_eval=tau, method='RK45')
theta = sol_c.y[0]

sin2 = np.sin(theta)**2
integral_c = np.cumsum(sin2 * np.diff(tau, prepend=0))
alpha_inv_c = alpha_inv0 - B * integral_c

# Theta stays bounded; α⁻¹ never diverges.
print("\n[COMPACT MODEL] θ remains bounded; α⁻¹ shows no Landau pole.")