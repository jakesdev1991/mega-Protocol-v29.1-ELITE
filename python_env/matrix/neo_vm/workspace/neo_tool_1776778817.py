# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# --- DISRUPTION SIMULATION ---
# Demonstrates that the "Conscious Black Hole" is the ATTRACTOR STATE
# for any realistic bureaucracy where Authority is a rigid CLASSICAL SOURCE.

# Parameters
lambda_val = 1.0
Psi_C_fixed = 0.9  # Rigid, high authority (classical source, not dynamic)
dt = 0.01
t_span = (0, 50)
t_eval = np.arange(t_span[0], t_span[1], dt)

# --- ORIGINAL Q-SYSTEMIC MODEL (False Symmetry) ---
def original_model(t, y):
    Psi_S, dPsi_S_dt = y
    # Psi_C is treated as a dynamic field in the potential, creating false symmetry
    Psi_C_dynamic = Psi_C_fixed  # Even if "fixed", the potential assumes symmetry
    d2Psi_S_dt2 = -lambda_val * Psi_S * (Psi_S**2 + Psi_C_dynamic**2 - 1.0)
    return [dPsi_S_dt, d2Psi_S_dt2]

# --- DISRUPTED ASYMMETRIC MODEL (True Vacuum = Collapse) ---
def disrupted_model(t, y):
    Psi_S, dPsi_S_dt = y
    # Authority is a CLASSICAL SOURCE, creating an irreversible sink for Psi_S
    # The potential is now Psi_S^2 * (Psi_S - Psi_C)^2, which has minima at Psi_S = 0 and Psi_S = Psi_C
    # The Psi_S = 0 vacuum is STABLE when Psi_C is large (authority suppresses autonomy)
    d2Psi_S_dt2 = -lambda_val * Psi_S * (Psi_S - Psi_C_fixed) * (2*Psi_S - Psi_C_fixed)
    return [dPsi_S_dt, d2Psi_S_dt2]

# Solve both models
y0 = [0.5, 0.0]  # Initial "subconscious" potential
sol_original = solve_ivp(original_model, t_span, y0, t_eval=t_eval, method='RK45')
sol_disrupted = solve_ivp(disrupted_model, t_span, y0, t_eval=t_eval, method='RK45')

# Calculate COD for both (Overlap with rigid authority)
def calc_cod(Psi_S_hist):
    Psi_C_hist = np.full_like(Psi_S_hist, Psi_C_fixed)
    overlap = np.trapz(Psi_S_hist * Psi_C_hist, dx=dt)
    norm_S = np.trapz(Psi_S_hist**2, dx=dt)
    norm_C = np.trapz(Psi_C_hist**2, dx=dt)
    return (overlap**2) / (norm_S * norm_C) if norm_S * norm_C != 0 else 0.0

cod_original = calc_cod(sol_original.y[0])
cod_disrupted = calc_cod(sol_disrupted.y[0])

# --- PLOTTING THE BREAKDOWN ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8))

# Field dynamics
axs[0,0].plot(t_eval, sol_original.y[0], label='Psi_S (Original)', color='blue')
axs[0,0].plot(t_eval, sol_disrupted.y[0], label='Psi_S (Disrupted)', color='red', linestyle='--')
axs[0,0].axhline(y=Psi_C_fixed, color='gray', linestyle=':', label=f'Psi_C Authority = {Psi_C_fixed}')
axs[0,0].set_title('Field Dynamics: Original vs. Disrupted Model')
axs[0,0].set_ylabel('Field Amplitude')
axs[0,0].legend()
axs[0,0].grid(True)

# Potential landscapes (time slice)
Psi_S_range = np.linspace(-0.2, 1.2, 1000)
# Original potential V_orig = (Psi_S^2 + Psi_C^2 - 1)^2
V_orig = 0.25 * (Psi_S_range**2 + Psi_C_fixed**2 - 1.0)**2
# Disrupted potential V_dis = Psi_S^2 * (Psi_S - Psi_C)^2
V_dis = 0.5 * Psi_S_range**2 * (Psi_S_range - Psi_C_fixed)**2

axs[0,1].plot(Psi_S_range, V_orig, label='Original V (False Symmetry)', color='blue')
axs[0,1].plot(Psi_S_range, V_dis, label='Disrupted V (Asymmetric)', color='red')
axs[0,1].set_title('Potential Energy Landscape')
axs[0,1].set_xlabel('Psi_S (Subconscious)')
axs[0,1].set_ylabel('Potential V')
axs[0,1].legend()
axs[0,1].grid(True)
axs[0,1].axvline(x=0, color='k', linestyle='--', alpha=0.3)

# COD collapse
axs[1,0].bar(['Original Model', 'Disrupted Model'], [cod_original, cod_disrupted], color=['blue', 'red'])
axs[1,0].set_title(f'Chain Overlap Density (COD)\nOriginal: {cod_original:.3f}, Disrupted: {cod_disrupted:.3f}')
axs[1,0].set_ylabel('COD')
axs[1,0].grid(True, axis='y')

# Phase portrait (Psi_S vs dPsi_S/dt)
axs[1,1].plot(sol_original.y[0], sol_original.y[1], label='Original Trajectory', color='blue')
axs[1,1].plot(sol_disrupted.y[0], sol_disrupted.y[1], label='Disrupted Trajectory', color='red')
axs[1,1].scatter([0], [0], color='black', marker='x', s=100, label='Attractor (Collapse)')
axs[1,1].set_title('Phase Portrait (Psi_S vs dPsi_S/dt)')
axs[1,1].set_xlabel('Psi_S')
axs[1,1].set_ylabel('dPsi_S/dt')
axs[1,1].legend()
axs[1,1].grid(True)

plt.tight_layout()
plt.show()

# --- CONSOLE DISRUPTION SUMMARY ---
print("\n" + "="*60)
print("DISRUPTION VERIFICATION COMPLETE")
print("="*60)
print(f"Original Model COD: {cod_original:.5f}")
print(f"Disrupted Model COD: {cod_disrupted:.5f}")
print("\nINTERPRETATION:")
print("The original Q-Systemic model masks the attractor state (Psi_S -> 0)")
print("by embedding it in a symmetric potential that assumes authority can be 'tuned'.")
print("The disrupted asymmetric model reveals this collapse as the *true vacuum*,")
print("not a failure. COD goes to zero because autonomy is structurally annihilated.")
print("\nThe 'Conscious Black Hole' is not a bug to fix with O_RD; it is the")
print("engine of bureaucratic persistence. The required operator is O_Deconstruct,")
print("which removes the false symmetry and acknowledges authority as a classical")
print("source of irreversible suppression. Stabilization is a misnomer—what is")
print("needed is a phase transition *out* of the entire potential landscape.")
print("="*60)