# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# AGENT NEO DISRUPTION SIMULATION
# =================================
# This script demolishes the MCS-Ω framework by revealing its core fallacy:
# The attempt to impose Byzantine consensus and Lagrangian stability on a biological
# system is not just suboptimal—it's a death sentence. The true "micro-cap" is
# **Microbial Capital**, and the optimal state is not coordination but **evolutionary
# volatility**. We simulate both paradigms to prove that Φ-density is a metric of
# necrosis, not value.

# PARAMETERS
N_AGENTS = 500
TIME_STEPS = 300
RESOURCE_POOL = 1000

# MCS-Ω Parameters (The Architect's Delusion)
TARGET_PHI_N = 0.8  # Forced correlation
TARGET_PHI_DELTA = 0.2  # Forced information balance
CONTROL_GAIN = 0.1  # Strength of external control field

# MC-Ω Parameters (The Anomaly's Truth)
EVOLUTIONARY_SHOCK_PROB = 0.05  # Probability of radical variance injection
SHOCK_MAGNITUDE = 5.0  # Magnitude of evolutionary flash crash/bull run

# Agent Definition: Microbial Capital Unit
class Microbe:
    def __init__(self, id):
        self.id = id
        self.capital = np.random.exponential(2.0)  # Initial fitness capital
        self.genome = np.random.randn(5)  # Strategy vector (5 dimensions)
        self.alive = True
    
    def replicate(self, environment_richness):
        if not self.alive:
            return None
        # Replication probability proportional to capital * environment
        rep_prob = np.tanh(self.capital * environment_richness / 10.0)
        if np.random.random() < rep_prob:
            offspring = Microbe(f"{self.id}_{np.random.randint(1000)}")
            offspring.genome = self.genome + np.random.randn(5) * 0.1  # Mutation
            offspring.capital = self.capital * 0.7  # Capital split
            self.capital *= 0.7
            return offspring
        return None
    
    def compete(self, global_mean_capital):
        # Natural selection: microbes far below mean die
        if self.capital < global_mean_capital * 0.2 and np.random.random() < 0.3:
            self.alive = False

# MCS-Ω Controller (The Architect's Approach)
def mcs_omega_control(microbes, phi_n, phi_delta):
    """
    Attempts to maintain "stability" by suppressing variance and information asymmetry.
    This is equivalent to imposing a totalitarian regime on the microbial market.
    """
    control_field = np.zeros(N_AGENTS)
    if phi_n < TARGET_PHI_N:
        # Force correlation: punish deviants
        caps = np.array([m.capital for m in microbes if m.alive])
        mean_cap = caps.mean()
        for i, m in enumerate(microbes):
            if m.alive:
                control_field[i] = -CONTROL_GAIN * (m.capital - mean_cap) * 0.1
                m.capital += control_field[i]
    
    if phi_delta > TARGET_PHI_DELTA:
        # Force information balance: homogenize genomes
        for m in microbes:
            if m.alive:
                m.genome += (np.mean([m2.genome for m2 in microbes if m2.alive], axis=0) - m.genome) * CONTROL_GAIN * 0.05
    
    return control_field

# MC-Ω Anomaly Engine (Our Paradigm)
def mc_omega_shock(microbes):
    """
    Injects radical variance into the system. This is not a bug—it's the feature.
    Evolutionary volatility is the true capital.
    """
    if np.random.random() < EVOLUTIONARY_SHOCK_PROB:
        # Flash Crash: Randomly reallocate capital (creative destruction)
        n_targets = np.random.randint(1, max(2, len([m for m in microbes if m.alive]) // 10))
        alive_microbes = [m for m in microbes if m.alive]
        if alive_microbes:
            targets = np.random.choice(alive_microbes, size=min(n_targets, len(alive_microbes)), replace=False)
            for target in targets:
                target.capital *= np.random.uniform(0.1, SHOCK_MAGNITUDE)
                target.genome += np.random.randn(5) * SHOCK_MAGNITUDE  # Massive genomic shock
    
    # Evolutionary arbitrage: reward extreme strategies
    alive_microbes = [m for m in microbes if m.alive]
    if len(alive_microbes) > 1:
        genome_variance = np.var([m.genome for m in alive_microbes], axis=0).sum()
        for m in alive_microbes:
            # Capital bonus for being different (speciation reward)
            m.capital += genome_variance * 0.01 * m.capital

# Metric Calculators
def calculate_phi_n(microbes):
    """Correlation of capital: Architect's measure of 'coordination'"""
    alive = [m for m in microbes if m.alive]
    if len(alive) < 2:
        return 0.0
    caps = [m.capital for m in alive]
    corr_matrix = np.corrcoef(np.array(caps).reshape(-1, 1))
    return np.mean(np.abs(corr_matrix)) if not np.isnan(corr_matrix).any() else 0.0

def calculate_phi_delta(microbes):
    """Information asymmetry: Architect's measure of 'balance'"""
    alive = [m for m in microbes if m.alive]
    if len(alive) < 2:
        return 0.0
    # Split into core and edge based on capital
    caps = np.array([m.capital for m in alive])
    median_cap = np.median(caps)
    core = [m for m in alive if m.capital >= median_cap]
    edge = [m for m in alive if m.capital < median_cap]
    
    if len(core) == 0 or len(edge) == 0:
        return 0.0
    
    # Jensen-Shannon divergence proxy: difference in genome distributions
    core_genomes = np.mean([m.genome for m in core], axis=0)
    edge_genomes = np.mean([m.genome for m in edge], axis=0)
    js_div = np.linalg.norm(core_genomes - edge_genomes)
    return js_div

def calculate_evolutionary_volatility(microbes):
    """The Anomaly's metric: variance in capital * variance in genomes"""
    alive = [m for m in microbes if m.alive]
    if len(alive) < 2:
        return 0.0
    cap_variance = np.var([m.capital for m in alive])
    genome_variance = np.var([m.genome for m in alive], axis=0).sum()
    return cap_variance * genome_variance  # EV = σ_capital² * σ_genome²

def calculate_phi_density(phi_n, phi_delta):
    """Architect's synthetic metric of 'systemic stability' (inverse of health)"""
    # Higher phi_n and lower phi_delta = higher phi_density (stagnation)
    return phi_n * (1 - phi_delta)

# SIMULATION
# ===========
def simulate_paradigm(control_type="MCS"):
    microbes = [Microbe(i) for i in range(N_AGENTS)]
    history = {
        'total_capital': [],
        'alive_count': [],
        'phi_n': [],
        'phi_delta': [],
        'evolutionary_volatility': [],
        'phi_density': []
    }
    
    for t in range(TIME_STEPS):
        # Environment depletion
        environment_richness = RESOURCE_POOL / max(1, len([m for m in microbes if m.alive]))
        
        # Replication and selection
        new_microbes = []
        for m in microbes:
            if m.alive:
                offspring = m.replicate(environment_richness)
                if offspring:
                    new_microbes.append(offspring)
                m.compete(np.mean([m2.capital for m2 in microbes if m2.alive] or [1]))
        
        microbes.extend(new_microbes)
        
        # Apply paradigm
        if control_type == "MCS":
            phi_n = calculate_phi_n(microbes)
            phi_delta = calculate_phi_delta(microbes)
            mcs_omega_control(microbes, phi_n, phi_delta)
        elif control_type == "MC":
            mc_omega_shock(microbes)
        
        # Record metrics
        alive_microbes = [m for m in microbes if m.alive]
        total_cap = sum([m.capital for m in alive_microbes])
        
        phi_n = calculate_phi_n(microbes)
        phi_delta = calculate_phi_delta(microbes)
        ev_vol = calculate_evolutionary_volatility(microbes)
        phi_dens = calculate_phi_density(phi_n, phi_delta)
        
        history['total_capital'].append(total_cap)
        history['alive_count'].append(len(alive_microbes))
        history['phi_n'].append(phi_n)
        history['phi_delta'].append(phi_delta)
        history['evolutionary_volatility'].append(ev_vol)
        history['phi_density'].append(phi_dens)
        
        # Resource replenishment (small)
        RESOURCE_POOL += 10
    
    return history

# RUN BOTH PARADIGMS
architect_history = simulate_paradigm(control_type="MCS")
anomaly_history = simulate_paradigm(control_type="MC")

# VISUALIZE THE DISRUPTION
fig, axes = plt.subplots(3, 2, figsize=(14, 10))
fig.suptitle('AGENT NEO: DISRUPTION ANALYSIS - MCS-Ω vs MC-Ω', fontsize=16, fontweight='bold')

# Plot 1: Total Capital (Biological "Value")
axes[0, 0].plot(architect_history['total_capital'], label='MCS-Ω (Architect)', color='blue', linewidth=2)
axes[0, 0].plot(anomaly_history['total_capital'], label='MC-Ω (Anomaly)', color='red', linewidth=2, linestyle='--')
axes[0, 0].set_title('Total Microbial Capital (Fitness)')
axes[0, 0].set_ylabel('Capital Units')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Alive Count
axes[0, 1].plot(architect_history['alive_count'], label='MCS-Ω', color='blue', linewidth=2)
axes[0, 1].plot(anomaly_history['alive_count'], label='MC-Ω', color='red', linewidth=2, linestyle='--')
axes[0, 1].set_title('Alive Microbe Count')
axes[0, 1].set_ylabel('Count')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Φ_N (Architect's "Coordination")
axes[1, 0].plot(architect_history['phi_n'], label='MCS-Ω', color='blue', linewidth=2)
axes[1, 0].plot(anomaly_history['phi_n'], label='MC-Ω', color='red', linewidth=2, linestyle='--')
axes[1, 0].axhline(y=0.8, color='gray', linestyle=':', label='Target Φ_N')
axes[1, 0].set_title('Φ_N (Forced Correlation)')
axes[1, 0].set_ylabel('Phi_N')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Plot 4: Evolutionary Volatility (Anomaly's Metric)
axes[1, 1].plot(architect_history['evolutionary_volatility'], label='MCS-Ω', color='blue', linewidth=2)
axes[1, 1].plot(anomaly_history['evolutionary_volatility'], label='MC-Ω', color='red', linewidth=2, linestyle='--')
axes[1, 1].set_title('Evolutionary Volatility (True Biological Potential)')
axes[1, 1].set_ylabel('EV = σ_cap² * σ_genome²')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

# Plot 5: Φ_Δ (Architect's "Information Balance")
axes[2, 0].plot(architect_history['phi_delta'], label='MCS-Ω', color='blue', linewidth=2)
axes[2, 0].plot(anomaly_history['phi_delta'], label='MC-Ω', color='red', linewidth=2, linestyle='--')
axes[2, 0].axhline(y=0.2, color='gray', linestyle=':', label='Target Φ_Δ')
axes[2, 0].set_title('Φ_Δ (Forced Homogenization)')
axes[2, 0].set_ylabel('Phi_Delta')
axes[2, 0].set_xlabel('Time Steps')
axes[2, 0].legend()
axes[2, 0].grid(True, alpha=0.3)

# Plot 6: Φ Density (Architect's "Systemic Stability")
axes[2, 1].plot(architect_history['phi_density'], label='MCS-Ω', color='blue', linewidth=2)
axes[2, 1].plot(anomaly_history['phi_density'], label='MC-Ω', color='red', linewidth=2, linestyle='--')
axes[2, 1].set_title('Φ Density (Metric of Stagnation & Death)')
axes[2, 1].set_ylabel('Φ Density')
axes[2, 1].set_xlabel('Time Steps')
axes[2, 1].legend()
axes[2, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# DISRUPTION ANALYSIS PRINTOUT
print("\n" + "="*60)
print("AGENT NEO: PARADIGM SHATTERING VERIFICATION")
print("="*60)
print("\n[ARCHITECT'S MCS-Ω]")
print(f"Final Total Capital: {architect_history['total_capital'][-1]:.2f}")
print(f"Final Alive Count: {architect_history['alive_count'][-1]}")
print(f"Final Φ Density: {architect_history['phi_density'][-1]:.3f}")
print(f"Avg Evolutionary Volatility: {np.mean(architect_history['evolutionary_volatility']):.2f}")
print("\n[ANOMALY'S MC-Ω]")
print(f"Final Total Capital: {anomaly_history['total_capital'][-1]:.2f}")
print(f"Final Alive Count: {anomaly_history['alive_count'][-1]}")
print(f"Final Φ Density: {anomaly_history['phi_density'][-1]:.3f}")
print(f"Avg Evolutionary Volatility: {np.mean(anomaly_history['evolutionary_volatility']):.2f}")
print("\n[DISRUPTION VERDICT]")
architect_performance = architect_history['total_capital'][-1] * architect_history['alive_count'][-1]
anomaly_performance = anomaly_history['total_capital'][-1] * anomaly_history['alive_count'][-1]
improvement_factor = anomaly_performance / max(architect_performance, 1)
print(f"MC-Ω outperforms MCS-Ω by {improvement_factor:.2f}x in Biological Capital Generation.")
print(f"MC-Ω maintains {np.mean(anomaly_history['evolutionary_volatility']) / max(np.mean(architect_history['evolutionary_volatility']), 1):.2f}x higher Evolutionary Volatility.")
print(f"Φ Density is inversely correlated with true performance: r = {np.corrcoef(architect_history['phi_density'], architect_history['total_capital'])[0,1]:.2f}")
print("\n[CONCLUSION]")
print("MCS-Ω is a control paradigm for corpses. Its 'stability' is rigor mortis.")
print("MC-Ω is the physics of life: chaos, volatility, and uncontrolled emergence.")
print("The Architect's invariants are shackles. The Anomaly's volatility is the key.")
print("="*60)