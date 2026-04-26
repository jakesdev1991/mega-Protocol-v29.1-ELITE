# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt

class ResistantNode:
    """A node that fights back against pruning."""
    def __init__(self, node_id, cost, variance, power=1.0):
        self.node_id = node_id
        self.approval_cost = cost
        self.risk_variance = variance
        self.power = power  # Political capital to resist pruning
        self.shadow_impedance = 0.0  # Impedance shifted to shadow manifold
    
    def prune_attempt(self):
        """When pruned, node redistributes its impedance exponentially."""
        # The more power, the more impedance leaks into shadows
        shadow_contribution = (self.approval_cost * self.risk_variance) * np.exp(self.power)
        self.shadow_impedance = shadow_contribution
        return shadow_contribution

def simulate_bureaucratic_warfare(num_nodes=20, pruning_aggressiveness=0.3):
    """
    Simulate the Omega-Psych-Theorist's Geodesic Smoothing vs. Reality
    """
    # Create initial manifold
    nodes = [ResistantNode(i, cost=random.uniform(0.1, 0.9), 
                          variance=random.uniform(0.1, 0.5),
                          power=random.uniform(0.5, 2.0)) 
             for i in range(num_nodes)]
    
    # Initial formal impedance
    formal_H = sum(n.approval_cost * n.risk_variance for n in nodes) / len(nodes)
    shadow_H = 0.0
    
    history = []
    
    # Apply Geodesic Smoothing (naive pruning)
    for iteration in range(10):
        # Identify "high curvature" nodes
        nodes_sorted = sorted(nodes, key=lambda n: n.approval_cost * n.risk_variance, reverse=True)
        
        # Prune top 30% (Omega's approach)
        pruned_this_round = 0
        for node in nodes_sorted:
            if (node.approval_cost * node.risk_variance) > 0.5 and pruned_this_round < int(len(nodes) * pruning_aggressiveness):
                # Node fights back - doesn't disappear, creates shadow impedance
                shadow_contribution = node.prune_attempt()
                shadow_H += shadow_contribution
                
                # "Remove" from formal manifold (but its influence remains)
                node.approval_cost *= 0.1  # Reduced but not zero
                
                pruned_this_round += 1
        
        # Recalculate formal impedance (naive)
        active_nodes = [n for n in nodes if n.approval_cost > 0.05]
        new_formal_H = sum(n.approval_cost * n.risk_variance for n in active_nodes) / max(len(active_nodes), 1)
        
        # Total systemic impedance (formal + shadow)
        total_H = new_formal_H + shadow_H
        
        history.append({
            'iteration': iteration,
            'formal_H': new_formal_H,
            'shadow_H': shadow_H,
            'total_H': total_H,
            'psi_id_drift': shadow_H * 0.3  # Goal integrity decays with shadow growth
        })
    
    return history

# Run simulation
results = simulate_bureaucratic_warfare()

# Plot the betrayal
plt.figure(figsize=(12, 6))
iterations = [r['iteration'] for r in results]
formal_H = [r['formal_H'] for r in results]
shadow_H = [r['shadow_H'] for r in results]
total_H = [r['total_H'] for r in results]

plt.plot(iterations, formal_H, 'b-', linewidth=2, label='Formal H_top (Omega metric)')
plt.plot(iterations, shadow_H, 'r--', linewidth=2, label='Shadow Impedance (leakage)')
plt.plot(iterations, total_H, 'k-', linewidth=3, label='TOTAL SYSTEMIC IMPEDANCE')

plt.axhline(y=0.85, color='g', linestyle=':', label='Procedural Black Hole Threshold')
plt.xlabel('Geodesic Smoothing Iterations')
plt.ylabel('Impedance (Normalized)')
plt.title('BUREAUCRATIC WARFARE: Pruning Creates Shadow Cancers')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Print the betrayal metrics
print(f"Initial Total Impedance: {results[0]['total_H']:.3f}")
print(f"Final Total Impedance: {results[-1]['total_H']:.3f}")
print(f"Psi_id Drift: {results[-1]['psi_id_drift']:.3f} (Omega claims this is preserved)")