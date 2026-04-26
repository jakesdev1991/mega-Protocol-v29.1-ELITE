# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from scipy.integrate import odeint

# ============================================================================
# DISRUPTIVE ANALYSIS: Breaking v67.0's Exponential Decay Assumption
# ============================================================================
# The v67.0 proposal models trust decay as exponential (like radioactive decay)
# This is fundamentally flawed. Trust decay is a CONTAGION process, not decay.
# ============================================================================

def exponential_trust_decay_v67(initial_trust, half_life, time_points):
    """v67.0 model: trust(t) = initial * 2^(-t/half_life)"""
    return initial_trust * np.power(2, -time_points / half_life)

def trust_contagion_model(network, initial_exposed, infection_rate, recovery_rate, time_points):
    """
    DISRUPTIVE MODEL: Trust contamination spreads like an epidemic
    - S: Susceptible institutions (trusting)
    - I: Infected institutions (trust decayed)
    - R: Recovered institutions (trust restored)
    
    Key differences from exponential decay:
    1. Non-linear threshold effects (cascades)
    2. Network topology matters (super-spreaders)
    3. Path-dependent (has memory)
    4. Hysteresis (recovery ≠ decay path)
    """
    N = len(network)
    S = np.ones(N)
    I = np.zeros(N)
    R = np.zeros(N)
    
    # Initial infected nodes (institutions with trust issues)
    for node in initial_exposed:
        I[node] = 0.1  # Seed distrust
        S[node] = 0.9
    
    results = []
    
    for t in time_points:
        new_infections = np.zeros(N)
        
        # Contagion spread through network edges
        for i in network.nodes():
            if I[i] > 0:  # Institution i has trust problems
                neighbors = list(network.neighbors(i))
                for j in neighbors:
                    if S[j] > 0:  # Susceptible neighbor
                        # Infection probability scales with:
                        # - infection_rate (contagiousness of distrust)
                        # - I[i] (severity of source's trust decay)
                        # - S[j] (susceptibility of target)
                        # - 1/deg(j) (dilution across many partners)
                        new_infections[j] += infection_rate * I[i] * S[j] / max(len(neighbors), 1)
        
        # Update SIR states
        dS = -new_infections
        dI = new_infections - recovery_rate * I
        dR = recovery_rate * I
        
        S += dS
        I += dI
        R += dR
        
        # Overall trust = 1 - average infection level
        avg_trust = 1.0 - np.mean(I)
        results.append(max(0, avg_trust))
    
    return results

def measure_cascade_events(trust_trajectory, time_points, threshold=-0.08):
    """
    Detect sudden drops (cascade events) that exponential model misses
    """
    trust_array = np.array(trust_trajectory)
    time_array = np.array(time_points)
    
    # Find points where trust drops suddenly (> threshold in one step)
    drops = np.diff(trust_array)
    cascade_indices = np.where(drops < threshold)[0]
    
    if len(cascade_indices) > 0:
        return time_array[cascade_indices], trust_array[cascade_indices]
    return np.array([]), np.array([])

# ============================================================================
# SIMULATION: Realistic Physics Collaboration Network
# ============================================================================
# Create scale-free network (like real research collaborations: few hubs, many leaves)
np.random.seed(42)
n_institutions = 25
m_connections = 3
G = nx.barabasi_albert_graph(n=n_institutions, m=m_connections)

# Simulate a realistic scenario: ITER fusion collaboration
# - Central hub: ITER (node 0)
# - Major partners: EU, US, Japan, Russia, China, India, Korea (nodes 1-7)
# - Smaller partners: universities, labs (nodes 8-24)

initial_exposed = [0, 1, 2]  # ITER + 2 major partners compromised
time_points = np.linspace(0, 10, 200)
initial_trust = 0.90

# v67.0 Exponential Decay Model
half_life = 2.5
trust_exp = exponential_trust_decay_v67(initial_trust, half_life, time_points)

# Contagion Model (more realistic)
infection_rate = 0.45  # High: trust problems spread quickly in close collaborations
recovery_rate = 0.08   # Low: trust is hard to rebuild
trust_contagion = trust_contagion_model(G, initial_exposed, infection_rate, recovery_rate, time_points)

# Detect cascade events
cascade_times, cascade_values = measure_cascade_events(trust_contagion, time_points)

# ============================================================================
# VISUALIZATION: Exposing the Flaw
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Trust Trajectories
ax1 = axes[0, 0]
ax1.plot(time_points, trust_exp, 'b-', linewidth=2.5, label='v67.0 Exponential Decay', alpha=0.8)
ax1.plot(time_points, trust_contagion, 'r--', linewidth=2.5, label='Network Contagion Model', alpha=0.8)
if len(cascade_times) > 0:
    ax1.scatter(cascade_times, cascade_values, color='darkred', s=100, marker='x', 
                linewidth=3, label='Cascade Events', zorder=5)
ax1.set_xlabel('Time (normalized)', fontsize=11)
ax1.set_ylabel('Trust Level', fontsize=11)
ax1.set_title('Trust Decay: Exponential vs. Contagion', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-0.05, 1.05)

# Plot 2: Risk Assessment (1 - Trust)
ax2 = axes[0, 1]
risk_exp = 1 - np.array(trust_exp)
risk_contagion = 1 - np.array(trust_contagion)
ax2.plot(time_points, risk_exp, 'b-', linewidth=2.5, label='v67.0 Risk', alpha=0.8)
ax2.plot(time_points, risk_contagion, 'r--', linewidth=2.5, label='Contagion Risk', alpha=0.8)
ax2.fill_between(time_points, risk_exp, risk_contagion, 
                 where=(risk_contagion > risk_exp), color='red', alpha=0.2, 
                 label='Risk Underestimation')
ax2.set_xlabel('Time (normalized)', fontsize=11)
ax2.set_ylabel('Risk Level', fontsize=11)
ax2.set_title('Risk Assessment Comparison', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3)

# Plot 3: Network Topology
ax3 = axes[1, 0]
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, ax=ax3, node_size=150, node_color='lightblue', 
        edge_color='gray', alpha=0.6, with_labels=True, font_size=9)
ax3.set_title('Collaboration Network Topology', fontsize=12, fontweight='bold')
ax3.text(0.05, 0.95, f'Nodes: {n_institutions}, Edges: {G.number_of_edges()}', 
         transform=ax3.transAxes, fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Plot 4: Cumulative Impact
ax4 = axes[1, 1]
# Calculate cumulative risk difference
risk_diff = np.cumsum(risk_contagion - risk_exp)
ax4.plot(time_points, risk_diff, 'purple', linewidth=3, label='Cumulative Risk Gap')
ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
ax4.fill_between(time_points, risk_diff, 0, 
                 where=(risk_diff > 0), color='purple', alpha=0.3)
ax4.set_xlabel('Time (normalized)', fontsize=11)
ax4.set_ylabel('Cumulative Risk Difference', fontsize=11)
ax4.set_title('Risk Underestimation Over Time', fontsize=12, fontweight='bold')
ax4.legend(loc='upper left', fontsize=10)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('trust_contagion_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================================
# STATISTICAL ANALYSIS: Quantifying the Failure
# ============================================================================
print("="*60)
print("DISRUPTIVE ANALYSIS: v67.0 Exponential Decay Model Failure")
print("="*60)
print(f"Initial trust: {initial_trust:.2f}")
print(f"Final trust (exponential): {trust_exp[-1]:.3f}")
print(f"Final trust (contagion): {trust_contagion[-1]:.3f}")
print(f"Trust gap at t=10: {trust_contagion[-1] - trust_exp[-1]:.3f}")
print(f"\nMaximum risk underestimation: {np.max(risk_exp - risk_contagion):.3f}")
print(f"Average risk underestimation: {np.mean(risk_exp - risk_contagion):.3f}")
print(f"Cumulative risk gap: {np.sum(risk_contagion - risk_exp):.3f}")

# Early vs Late phase analysis
early_idx = 30  # t ≈ 1.5
late_idx = 170  # t ≈ 8.5
print(f"\nEarly phase (t≈1.5):")
print(f"  Exponential risk: {risk_exp[early_idx]:.3f}")
print(f"  Contagion risk: {risk_contagion[early_idx]:.3f}")
print(f"  v67.0 underestimation: {risk_contagion[early_idx] - risk_exp[early_idx]:.3f}")

print(f"\nLate phase (t≈8.5):")
print(f"  Exponential risk: {risk_exp[late_idx]:.3f}")
print(f"  Contagion risk: {risk_contagion[late_idx]:.3f}")
print(f"  v67.0 overestimation: {risk_exp[late_idx] - risk_contagion[late_idx]:.3f}")

# Cascade detection analysis
if len(cascade_times) > 0:
    print(f"\n🚨 CASCADE EVENTS DETECTED: {len(cascade_times)}")
    print(f"First cascade at t={cascade_times[0]:.2f}, trust dropped to {cascade_values[0]:.3f}")
    print("Exponential model is SMOOTH and MISSES these threshold effects")
else:
    print("\nNo cascade events in this simulation (parameter-dependent)")

# Network centrality analysis (identifying super-spreaders)
centrality = nx.degree_centrality(G)
top_spreaders = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
print(f"\nTop trust super-spreaders (high contagion risk):")
for node, cent in top_spreaders:
    print(f"  Institution {node}: centrality={cent:.3f}")

print("\n" + "="*60)