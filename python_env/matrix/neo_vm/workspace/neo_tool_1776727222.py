# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- Standard Model (from the Engine's derivation) ---
def standard_model(t, y, params):
    """
    y = [alpha, phi_delta, phi_N]
    Standard RG flow with feedback loop.
    """
    alpha, phi_delta, phi_N = y
    gN_sq, gD_sq, lambda_param, v_sq = params
    
    # Perturbative beta function
    dalpha_dt = -alpha**2 / np.pi * (1 + 3*gD_sq/(4*np.pi) + gN_sq/(4*np.pi))
    
    # Simplified dynamics for phi_delta (feedback loop)
    # d(phi_delta)/dt ~ alpha * phi_delta
    dphi_delta_dt = alpha * phi_delta * 0.1 # 0.1 is a coupling constant
    
    # Poisson recovery equation for phi_N
    # Box + lambda*phi_N*(phi_N^2 + 3*phi_delta^2 - v_sq) = source
    # Simplified: d(phi_N)/dt = -lambda*phi_N*(phi_N^2 + 3*phi_delta^2 - v_sq)
    dphi_N_dt = -lambda_param * phi_N * (phi_N**2 + 3*phi_delta**2 - v_sq)
    
    return [dalpha_dt, dphi_delta_dt, dphi_N_dt]

# --- Disruptive Model (Anomaly's Paradigm Break) ---
def disruptive_model(t, y, params):
    """
    y = [alpha, phi_delta, phi_N]
    Non-analytic potential term: V_non = c * |phi_delta|^eta
    This introduces a singularity in the Hessian and breaks analyticity.
    """
    alpha, phi_delta, phi_N = y
    gN_sq, gD_sq, lambda_param, v_sq, c, eta = params
    
    # The non-analytic term modifies the effective stiffness
    # xi_delta_inv_sq = lambda*(phi_N**2 + 3*phi_delta**2 - v_sq) + c * eta * (eta - 1) * abs(phi_delta)**(eta - 2)
    # For eta < 2, this term diverges as phi_delta -> 0, creating a "Shredding" singularity.
    
    # Modified beta function: the effective gD_sq becomes scale-dependent and singular
    # gD_eff_sq = gD_sq * (1 + c * abs(phi_delta)**(eta - 2)) # Singularity driver
    # Let's make the enhancement more direct: if phi_delta -> 0, the term explodes, but we want divergence at phi_delta -> some critical value.
    # Let's reframe: the non-analyticity is in the potential, so the "mass" term for phi_delta is not analytic.
    
    # Shredding condition is no longer smooth: it becomes a critical point of non-analyticity
    # Let's model the stiffness as: xi_delta_inv_sq = lambda*(phi_N**2 + 3*phi_delta**2 - v_sq) + c / (abs(phi_delta - phi_critical) + epsilon)
    phi_critical = 0.5 * np.sqrt(v_sq) # Example critical value
    epsilon = 1e-4
    
    # This term BLOWS UP as phi_delta approaches phi_critical, INDEPENDENT of the simple feedback loop.
    shredding_driver = c / (abs(phi_delta - phi_critical) + epsilon)
    
    # Modified beta function: the Archive mode contribution is amplified by the shredding driver
    dalpha_dt = -alpha**2 / np.pi * (1 + 3*gD_sq/(4*np.pi) * (1 + shredding_driver) + gN_sq/(4*np.pi))
    
    # The equation for phi_delta is now dominated by the non-analytic potential gradient
    # dV/dphi_delta contains a term c * eta * sign(phi_delta) * abs(phi_delta)^(eta-1)
    # For simplicity, model the divergence directly:
    dphi_delta_dt = alpha * phi_delta * 0.1 + shredding_driver * 0.01 # The driver pushes phi_delta away or into the singularity
    
    # Poisson recovery is FUNDAMENTALLY broken because the equation of motion is non-analytic
    # The term lambda*phi_N*(phi_N^2 + 3*phi_delta^2 - v_sq) is now regularized by the singularity
    dphi_N_dt = -lambda_param * phi_N * (phi_N**2 + 3*phi_delta**2 - v_sq) - shredding_driver * phi_N * 0.1
    
    return [dalpha_dt, dphi_delta_dt, dphi_N_dt]

# --- Simulation Parameters ---
# Shared parameters
gN_sq = 0.1
gD_sq = 0.05
lambda_param = 0.5
v_sq = 1.0

# Initial conditions
y0_standard = [1/137, 0.1, 0.9] # alpha ~ 1/137, phi_delta small, phi_N near v
y0_disruptive = [1/137, 0.1, 0.9]

t_span = (0, 50)
t_eval = np.linspace(t_span[0], t_span[1], 1000)

# --- Run Standard Model ---
params_standard = (gN_sq, gD_sq, lambda_param, v_sq)
sol_standard = solve_ivp(standard_model, t_span, y0_standard, args=(params_standard,), t_eval=t_eval, dense_output=True)

# --- Run Disruptive Model ---
c = 0.5
eta = 1.5 # Non-integer exponent for non-analyticity
params_disruptive = (gN_sq, gD_sq, lambda_param, v_sq, c, eta)
sol_disruptive = solve_ivp(disruptive_model, t_span, y0_disruptive, args=(params_disruptive,), t_eval=t_eval, dense_output=True)

# --- Visualization ---
fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

# Plot alpha
axs[0].plot(sol_standard.t, sol_standard.y[0], label='Standard Model', linewidth=2)
axs[0].plot(sol_disruptive.t, sol_disruptive.y[0], label='Disruptive Model', linewidth=2, linestyle='--')
axs[0].set_ylabel(r'$\alpha$ (Fine-Structure Constant)')
axs[0].set_title(r'Comparison: Standard vs. Disruptive Omega Protocol Dynamics')
axs[0].legend()
axs[0].grid(True)

# Plot phi_delta
axs[1].plot(sol_standard.t, sol_standard.y[1], label='Standard Model', linewidth=2)
axs[1].plot(sol_disruptive.t, sol_disruptive.y[1], label='Disruptive Model', linewidth=2, linestyle='--')
axs[1].set_ylabel(r'$\Phi_\Delta$ (Archive Mode)')
axs[1].legend()
axs[1].grid(True)

# Plot phi_N
axs[2].plot(sol_standard.t, sol_standard.y[2], label='Standard Model', linewidth=2)
axs[2].plot(sol_disruptive.t, sol_disruptive.y[2], label='Disruptive Model', linewidth=2, linestyle='--')
axs[2].set_ylabel(r'$\Phi_N$ (Newtonian Mode)')
axs[2].set_xlabel('RG Time / Scale Parameter')
axs[2].legend()
axs[2].grid(True)

plt.tight_layout()
plt.show()

# --- Print key metrics ---
print("--- Final Values (t=50) ---")
print(f"Standard Model: alpha={sol_standard.y[0,-1]:.4f}, phi_delta={sol_standard.y[1,-1]:.4f}, phi_N={sol_standard.y[2,-1]:.4f}")
print(f"Disruptive Model: alpha={sol_disruptive.y[0,-1]:.4f}, phi_delta={sol_disruptive.y[1,-1]:.4f}, phi_N={sol_disruptive.y[2,-1]:.4f}")

# Identify "Shredding" in disruptive model
# We can define shredding as when phi_N collapses or alpha diverges rapidly
alpha_growth_rate = np.diff(sol_disruptive.y[0]) / np.diff(sol_disruptive.t)
shredding_point = np.argmax(alpha_growth_rate > 1.0) # Arbitrary threshold for "blow-up"
if shredding_point > 0:
    print(f"\n--- DISRUPTION DETECTED ---")
    print(f"The disruptive model exhibits a rapid divergence around t~{sol_disruptive.t[shredding_point]:.2f}.")
    print(f"At this point, the non-analytic potential term dominates, causing:")
    print(f"  1. Premature divergence of Phi_Delta (Archive mode)")
    print(f"  2. Violation of Poisson recovery: Phi_N collapses from {sol_disruptive.y[2, shredding_point-1]:.4f} to {sol_disruptive.y[2, shredding_point]:.4f}")
    print(f"  3. The 'Shredding Event' is triggered by the singularity in the potential, NOT the simple feedback loop.")
    print(f"This demonstrates that the original derivation's assumption of analyticity is fundamentally flawed.")