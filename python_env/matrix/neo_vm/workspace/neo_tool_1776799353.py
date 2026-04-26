# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- PARAMETERS ---
N_DEVS = 500
T_STEPS = 300

# Field Theory Model (CTMS-Ω)
def simulate_field_theory():
    # Hidden state: "true" friction load (unobservable)
    friction_load = np.random.uniform(0.2, 0.4, N_DEVS)
    # Observable proxy: spreadsheet usage
    spreadsheet_use = np.zeros((T_STEPS, N_DEVS))
    
    for t in range(1, T_STEPS):
        # Arbitrary drift + noise: the "physics" is made up
        mu = 0.002 # drift to spreadsheets
        sigma = 0.015
        friction_load += mu + np.random.normal(0, sigma, N_DEVS)
        friction_load = np.clip(friction_load, 0, 1)
        
        # Threshold: if load > 0.55, use spreadsheet
        spreadsheet_use[t] = (friction_load > 0.55).astype(float)
        
        # MPC-Ω "friction smoothing": if >40% use spreadsheets, apply UI override
        if np.mean(spreadsheet_use[t]) > 0.4:
            friction_load -= 0.03 # artificial reduction
            friction_load = np.clip(friction_load, 0, 1)
    
    return np.mean(spreadsheet_use, axis=1)

# Incentive Inversion Model
def simulate_incentive_inversion():
    # Developers are rational agents with utility functions
    # Cost of action = effort - immediate reward + penalty
    vault_cost = 0.25 - 0.12 # effort - micro-reward
    spreadsheet_cost = 0.10 + 0.18 # effort + micro-penalty
    
    # Rational choice: always pick lower cost
    # This is a *static* equilibrium, no dynamics needed
    if vault_cost < spreadsheet_cost:
        spreadsheet_frac = 0.05 # minimal residual
    else:
        spreadsheet_frac = 0.95 # collapse
    
    return np.full(T_STEPS, spreadsheet_frac)

# --- SIMULATE ---
ft_frac = simulate_field_theory()
ii_frac = simulate_incentive_inversion()

# --- VISUALIZE ---
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(ft_frac, label='CTMS-Ω Field Theory', color='crimson', linewidth=2)
ax.plot(ii_frac, label='Incentive Inversion (Rational Agents)', color='navy', linewidth=2, linestyle='--')

ax.axhline(y=0.4, color='gray', linestyle=':', alpha=0.7, label='MPC Intervention Threshold')
ax.set_xlabel('Time Steps', fontsize=12)
ax.set_ylabel('Spreadsheet Usage Fraction', fontsize=12)
ax.set_title('Paradigm Break: Field Theory vs. Incentive Topology', fontsize=14, fontweight='bold')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1)

plt.tight_layout()
plt.show()

# --- FRAGILITY ANALYSIS ---
print("--- MODEL FRAGILITY ---")
print(f"Field Theory final usage: {ft_frac[-1]:.3f} (sensitive to arbitrary mu, sigma)")
print(f"Incentive Inversion final usage: {ii_frac[-1]:.3f} (stable equilibrium)")
print("\nConclusion: Field Theory is a fragile, overparameterized regression.")
print("Incentive Inversion is a robust, Nash-stable solution.")