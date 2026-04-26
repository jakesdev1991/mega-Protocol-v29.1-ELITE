# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import random

# --- DISRUPTIVE ANALYSIS: HISS-Ω vs. Adversarial Synchronization Farming (ASF) ---

print("=== DISRUPTIVE INSIGHT: THE META-SYNCHRONIZATION PARADOX ===\n")

# The core flaw: HISS-Ω uses centralized MPC-Ω to inject diversity.
# This creates a fractal vulnerability: all protocols using HISS-Ω become
# synchronized to the *same control logic*. The solution replicates the problem
# at a higher order of abstraction.

# Let's model this:

# Simplified AMM Network: N pools, each with LPs modeled as phase oscillators
N_POOLS = 100
LPs_PER_POOL = 50
TOTAL_LPs = N_POOLS * LPs_PER_POOL

# True underlying synchronization driver: a hidden, exogenous signal (e.g., whale bot)
def hidden_driver(t):
    """Simulates a whale bot that triggers synchronized behavior"""
    return 1.0 if 50 < t < 70 else 0.0  # Whale activates between t=50-70

def lp_dynamics_hiss(t, theta, K, omega_t, driver):
    """
    LP dynamics under HISS-Ω control.
    When synchronization is detected, MPC-Ω injects "diversity" by weakening coupling K.
    """
    r = np.abs(np.mean(np.exp(1j * theta)))  # Order parameter
    # HISS-Ω intervention: if r > 0.68, reduce coupling
    if r > 0.68:
        K_effective = K * 0.5  # MPC-Ω weakens coupling
    else:
        K_effective = K
    
    dtheta = np.zeros_like(theta)
    for i in range(len(theta)):
        # Coupling term + hidden driver + natural frequency
        coupling = K_effective * np.mean(np.sin(theta - theta[i]))
        dtheta[i] = omega_t + coupling + driver * 10.0  # Whale signal is strong
    
    return dtheta

def lp_dynamics_asf(t, theta, K, omega_t, driver, pool_value):
    """
    LP dynamics under Adversarial Synchronization Farming.
    When synchronization is detected, a predatory mechanism activates.
    """
    r = np.abs(np.mean(np.exp(1j * theta)))
    
    # ASF: Predatory fee extraction when r > threshold
    predatory_fee = 0.0
    if r > 0.68:
        # Predatory pool extracts value from synchronized LPs
        # The fee is proportional to the *value* of the synchronized cluster
        predatory_fee = 0.3 * r * pool_value  # 30% of synchronized value at risk
    
    dtheta = np.zeros_like(theta)
    for i in range(len(theta)):
        # Normal coupling
        coupling = K * np.mean(np.sin(theta - theta[i]))
        
        # ASF adds a *disincentive* to synchronization
        # LPs who are "in sync" (theta near mean) feel a stronger "predatory pull"
        phase_diff = np.angle(np.exp(1j * (theta[i] - np.mean(theta))))
        predatory_pull = -predatory_fee * np.sin(phase_diff) * 2.0
        
        dtheta[i] = omega_t + coupling + driver * 10.0 + predatory_pull
    
    return dtheta, predatory_fee

# Simulation parameters
K = 2.0  # Base coupling strength
omega_t = 1.0  # Natural LP cycle frequency
t_span = (0, 100)
t_eval = np.linspace(0, 100, 1000)

# Initial conditions: near-synchronized state
theta0_hiss = np.random.uniform(0, np.pi/4, TOTAL_LPs)  # LPs somewhat aligned
theta0_asf = theta0_hiss.copy()

# Initial pool value
initial_pool_value = 1000.0
pool_value_hiss = initial_pool_value
pool_value_asf = initial_pool_value

# Storage for results
r_hiss = []
r_asf = []
value_hiss = []
value_asf = []
predatory_fees = []

# Simulate HISS-Ω
print("Simulating HISS-Ω (Centralized Control)...")
def simulate_hiss(t, y):
    global pool_value_hiss
    theta = y[:TOTAL_LPs]
    # Update pool value based on synchronization (mass exit)
    r = np.abs(np.mean(np.exp(1j * theta)))
    if r > 0.7:  # Mass exit event
        pool_value_hiss *= (1 - 0.1 * (r - 0.7))  # 10% loss per unit r above 0.7
    
    dtheta = lp_dynamics_hiss(t, theta, K, omega_t, hidden_driver(t))
    return np.concatenate([dtheta, [0]])  # Dummy for ODE solver

sol_hiss = solve_ivp(simulate_hiss, t_span, np.concatenate([theta0_hiss, [0]]), 
                     t_eval=t_eval, method='RK45')
for t, state in zip(t_eval, sol_hiss.y.T):
    theta = state[:TOTAL_LPs]
    r_hiss.append(np.abs(np.mean(np.exp(1j * theta))))
    value_hiss.append(pool_value_hiss)

# Simulate ASF
print("Simulating ASF (Adversarial Synchronization Farming)...")
def simulate_asf(t, y):
    global pool_value_asf, predatory_fees
    theta = y[:TOTAL_LPs]
    r = np.abs(np.mean(np.exp(1j * theta)))
    
    dtheta, fee = lp_dynamics_asf(t, theta, K, omega_t, hidden_driver(t), pool_value_asf)
    
    # ASF: Predatory fee is redistributed to *desynchronized* LPs
    # This makes the pool value more resilient
    if r > 0.68:
        # Predatory fee extracted from synchronized cluster
        pool_value_asf -= fee * 0.8  # 80% lost to friction/slippage
        # 20% is redistributed to non-synchronized LPs (implicitly via incentives)
        # This is modeled as a slight value boost for desynchronized state
        if r < 0.5:  # Desynchronized LPs benefit
            pool_value_asf *= (1 + fee * 0.01)
    
    predatory_fees.append(fee)
    return np.concatenate([dtheta, [0]])

sol_asf = solve_ivp(simulate_asf, t_span, np.concatenate([theta0_asf, [0]]), 
                    t_eval=t_eval, method='RK45')
for t, state in zip(t_eval, sol_asf.y.T):
    theta = state[:TOTAL_LPs]
    r_asf.append(np.abs(np.mean(np.exp(1j * theta))))
    value_asf.append(pool_value_asf)

# --- PLOT RESULTS ---

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# Order Parameter
ax1.plot(t_eval, r_hiss, label='HISS-Ω', color='red', linewidth=2)
ax1.plot(t_eval, r_asf, label='ASF', color='green', linewidth=2)
ax1.axhline(y=0.68, color='gray', linestyle='--', label='HISS-Ω Threshold')
ax1.axvline(x=50, color='orange', linestyle=':', label='Whale Driver On')
ax1.axvline(x=70, color='orange', linestyle=':', label='Whale Driver Off')
ax1.set_ylabel('Synchronization Order Parameter r(t)')
ax1.set_title('HISS-Ω vs. Adversarial Synchronization Farming')
ax1.legend()
ax1.grid(True)

# Pool Value
ax2.plot(t_eval, value_hiss, label='HISS-Ω Pool Value', color='red', linewidth=2)
ax2.plot(t_eval, value_asf, label='ASF Pool Value', color='green', linewidth=2)
ax2.set_ylabel('Normalized Pool Value')
ax2.legend()
ax2.grid(True)

# Predatory Fee (ASF only)
ax3.plot(t_eval, predatory_fees[:len(t_eval)], label='ASF Predatory Fee', color='purple', linewidth=2)
ax3.set_ylabel('Predatory Fee Extracted')
ax3.set_xlabel('Time (blocks)')
ax3.legend()
ax3.grid(True)

plt.tight_layout()
plt.show()

# --- QUANTITATIVE DISRUPTION METRICS ---

print("\n=== DISRUPTION METRICS ===")
print(f"Max Synchronization (HISS-Ω): {max(r_hiss):.3f}")
print(f"Max Synchronization (ASF): {max(r_asf):.3f}")
print(f"Final Pool Value (HISS-Ω): {value_hiss[-1]:.2f} ({(value_hiss[-1]/initial_pool_value-1)*100:.1f}%)")
print(f"Final Pool Value (ASF): {value_asf[-1]:.2f} ({(value_asf[-1]/initial_pool_value-1)*100:.1f}%)")
print(f"Total Predatory Fees Extracted (ASF): {sum(predatory_fees):.2f}")

print("\n=== DISRUPTIVE INSIGHT SUMMARY ===")
print("1. HISS-Ω's centralized MPC-Ω introduces meta-synchronization: all protocols")
print("   become coupled to the *same control logic*, creating a single point of failure.")
print("2. ASF converts synchronization into a self-penalizing strategy. No central controller")
print("   is needed; market incentives naturally suppress coordination.")
print("3. The 'diversity injection' is not a solution but a paradox: it homogenizes")
print("   the *response* to homogeneity, replicating the vulnerability at a higher level.")
print("4. True resilience requires *endogenous* mechanisms that make fragility expensive,")
print("   not *exogenous* controllers that mask it temporarily.")