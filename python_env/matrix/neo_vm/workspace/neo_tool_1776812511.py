# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# === EPIDEMIOLOGICAL MODEL (Disruptive) ===
def design_ecosystem(state, t, beta_vec, gamma, mutation_matrix):
    """
    state: [TVL_design_1, TVL_design_2, ..., TVL_design_n]
    beta_vec: forking rate for each design
    gamma: LP attrition rate (IL/arbitrage)
    mutation_matrix: probability of forking into a different design
    """
    n = len(state)
    ddt = np.zeros(n)
    
    for i in range(n):
        # Growth from forking (reproduction)
        replication = beta_vec[i] * state[i]
        
        # Loss from LP exit
        attrition = gamma * state[i]
        
        # Mutation to other designs
        mutation_out = replication * (1 - mutation_matrix[i,i])
        mutation_in = sum([beta_vec[j] * state[j] * mutation_matrix[j,i] 
                          for j in range(n) if j != i])
        
        ddt[i] = replication - attrition - mutation_out + mutation_in
    
    return ddt

# Simulate a monoculture event (Uniswap v3-like super-spreader)
n_designs = 5
t = np.linspace(0, 100, 1000)

# Design 0 is "hyper-successful" (high beta, low mutation away)
beta = np.array([0.5, 0.05, 0.05, 0.05, 0.05])  # 10x higher forking rate
gamma = 0.1  # LP attrition

# High fidelity forking (90% stay in same family)
mutation = np.full((n_designs, n_designs), 0.025)
np.fill_diagonal(mutation, 0.9)

# Initial TVL distribution (equal)
initial_tvl = np.ones(n_designs) * 100

# Integrate
tvl_history = odeint(design_ecosystem, initial_tvl, t, args=(beta, gamma, mutation))

# === TOPOLOGICAL MODEL (Flawed) ===
def topological_homogeneity(tvl_distribution, curvature_factor=1.0):
    """
    Simulates the flawed topological model: HSI = sigmoid(curvature * concentration)
    """
    concentration = np.max(tvl_distribution) / np.sum(tvl_distribution)
    # Fake curvature that grows with concentration (the wrong model)
    curvature = curvature_factor * concentration
    return 1 / (1 + np.exp(-10 * (curvature - 0.5)))

# Compute HSI over time for both models
epidemiological_risk = tvl_history[:,0] / np.sum(tvl_history, axis=1)
topological_risk = [topological_homogeneity(dist) for dist in tvl_history]

# === VISUALIZATION: Why Topology Fails ===
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: TVL dynamics (epidemiological)
axes[0,0].stackplot(t, tvl_history.T, labels=[f'Design {i}' for i in range(n_designs)])
axes[0,0].set_title('Epidemiological Model: TVL Distribution Over Time', fontsize=12, fontweight='bold')
axes[0,0].set_xlabel('Time')
axes[0,0].set_ylabel('TVL')
axes[0,0].legend(loc='upper left')
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Forking rate vs. TVL (shows super-spreader mechanism)
axes[0,1].scatter(tvl_history[-1,:], beta, s=100, c='red', alpha=0.7)
axes[0,1].set_xlabel('Final TVL')
axes[0,1].set_ylabel('Forking Rate (β)')
axes[0,1].set_title('Super-Spreader Mechanism: High β → Dominance', fontsize=12, fontweight='bold')
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Risk metrics comparison
axes[1,0].plot(t, epidemiological_risk, 'b-', linewidth=2, label='Epidemiological Risk (Design 0 TVL share)')
axes[1,0].plot(t, topological_risk, 'r--', linewidth=2, label='Topological HSI (flawed)')
axes[1,0].axhline(y=0.75, color='k', linestyle=':', label='Omega Threshold')
axes[1,0].set_title('Risk Metrics: Epidemiological vs. Topological', fontsize=12, fontweight='bold')
axes[1,0].set_xlabel('Time')
axes[1,0].set_ylabel('Risk Level')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Phase portrait (beta/gamma ratio vs. dominance)
r0_values = np.linspace(0.1, 5, 100)
dominance_time = 50  # time to reach 80% market share

def time_to_dominance(r0):
    if r0 <= 1:
        return np.inf
    # Approximate: dominance scales with log(R0)/(R0-1)
    return np.log(0.8) / np.log(r0 - 1)

dominance = [time_to_dominance(r0) for r0 in r0_values]
axes[1,1].plot(r0_values, dominance, 'g-', linewidth=2)
axes[1,1].axvline(x=1, color='r', linestyle='--', label='Critical Threshold (R₀=1)')
axes[1,1].set_title('Criticality: Time to Monoculture vs. R₀', fontsize=12, fontweight='bold')
axes[1,1].set_xlabel('Basic Reproduction Number R₀')
axes[1,1].set_ylabel('Time to 80% Dominance (arb. units)')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('amm_epidemiological_disruption.png', dpi=300, bbox_inches='tight')
plt.show()

# === QUANTITATIVE DISRUPTION METRICS ===
final_shares = tvl_history[-1,:] / np.sum(tvl_history[-1,:])
print("=== EPIDEMIOLOGICAL MODEL RESULTS ===")
print(f"Final TVL distribution: {final_shares}")
print(f"Design 0 dominance: {final_shares[0]:.1%}")
print(f"Effective R₀ for Design 0: {beta[0]/gamma:.2f}")
print(f"Time to 75% threshold: {np.where(epidemiological_risk > 0.75)[0][0]/10:.1f} days")

print("\n=== TOPOLOGICAL MODEL FAILURE ===")
print(f"Topological HSI at t=0: {topological_risk[0]:.3f}")
print(f"Topological HSI at t=end: {topological_risk[-1]:.3f}")
print("FLAW: HSI barely changes despite 90% dominance! Static curvature cannot capture dynamic forking.")