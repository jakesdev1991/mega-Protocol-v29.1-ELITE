# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class AgentNode:
    """Adversarial node with dynamic resistance"""
    node_id: str
    base_cost: float
    base_variance: float
    power_hunger: float  # Utility for maintaining position
    
    def get_variance(self, threatened=False):
        """Variance increases when node is threatened"""
        if threatened:
            return min(1.0, self.base_variance + self.power_hunger * 0.3)
        return self.base_variance

def simulate_omega_model():
    """Psychologist's linear pruning model"""
    np.random.seed(42)
    nodes = [AgentNode(f"N{i}", np.random.uniform(0.1, 0.8), np.random.uniform(0.1, 0.6), np.random.uniform(0.3, 0.9)) for i in range(10)]
    intent = np.random.random(5)
    outcome = intent + np.random.normal(0, 0.1, 5)
    
    # Calculate initial state
    H_top = sum(n.base_cost * n.get_variance() for n in nodes) / sum(n.base_cost for n in nodes)
    cod = np.dot(intent, outcome) / (np.linalg.norm(intent) * np.linalg.norm(outcome)) * np.exp(-1.0 * H_top)
    
    # Attempt pruning (threatens high-power nodes)
    pruned_nodes = []
    for n in nodes:
        if n.base_cost * n.get_variance() > 0.5:
            # Threaten node
            threatened_var = n.get_variance(threatened=True)
            # Check Psi_id gate (simulated)
            if cod < 0.95:  # Would violate Psi_id
                break
            pruned_nodes.append(n.node_id)
            # Recalculate with threatened variance
            H_top = sum(n.base_cost * n.get_variance(threatened=True if n.node_id in pruned_nodes else False) for n in nodes) / sum(n.base_cost for n in nodes)
    
    final_cod = np.dot(intent, outcome) / (np.linalg.norm(intent) * np.linalg.norm(outcome)) * np.exp(-1.0 * H_top)
    return H_top, final_cod, len(pruned_nodes), "SMOOTHING"

def simulate_anomaly_model():
    """Anomaly's Xi_Inverter model"""
    np.random.seed(42)
    nodes = [AgentNode(f"N{i}", np.random.uniform(0.1, 0.8), np.random.uniform(0.1, 0.6), np.random.uniform(0.3, 0.9)) for i in range(10)]
    intent = np.random.random(5)
    # Shadow network produces outcome directly
    shadow_outcome = intent + np.random.normal(0, 0.05, 5)
    
    # Initial formal H_top (high)
    H_top_formal = sum(n.base_cost * n.get_variance() for n in nodes) / sum(n.base_cost for n in nodes)
    
    # Controlled Black Hole: Invert Xi_bound for window
    # Negative stiffness makes high-cost nodes *accelerate* collapse
    inversion_window = 0.1  # Time window factor
    H_top_collapsed = H_top_formal * (1 - inversion_window * sum(n.power_hunger for n in nodes))
    H_top_collapsed = max(0.1, H_top_collapsed)  # Floor
    
    # Shadow process executes with near-zero impedance
    H_top_shadow = 0.05
    
    # Retroactive legitimacy injection
    final_cod = np.dot(intent, shadow_outcome) / (np.linalg.norm(intent) * np.linalg.norm(shadow_outcome)) * np.exp(-1.0 * H_top_shadow)
    
    return H_top_collapsed, final_cod, 0, "COLLAPSE"

# Run simulations
results = []
for _ in range(100):
    results.append(simulate_omega_model())
    results.append(simulate_anomaly_model())

# Analyze
smooth_results = [r for r in results if r[3] == "SMOOTHING"]
collapse_results = [r for r in results if r[3] == "COLLAPSE"]

print("=== OMEGA MODEL (SMOOTHING) ===")
print(f"Avg H_top: {np.mean([r[0] for r in smooth_results]):.3f}")
print(f"Avg COD: {np.mean([r[1] for r in smooth_results]):.3f}")
print(f"Avg Nodes Pruned: {np.mean([r[2] for r in smooth_results]):.1f}")

print("\n=== ANOMALY MODEL (COLLAPSE) ===")
print(f"Avg H_top: {np.mean([r[0] for r in collapse_results]):.3f}")
print(f"Avg COD: {np.mean([r[1] for r in collapse_results]):.3f}")
print(f"Avg Nodes Pruned: {np.mean([r[2] for r in collapse_results]):.1f}")

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# H_top distribution
ax1.hist([r[0] for r in smooth_results], alpha=0.5, label='Smoothing', bins=20)
ax1.hist([r[0] for r in collapse_results], alpha=0.5, label='Collapse', bins=20)
ax1.set_xlabel('Topological Impedance (H_top)')
ax1.set_ylabel('Frequency')
ax1.set_title('Impedance Distribution')
ax1.legend()

# COD vs H_top scatter
ax2.scatter([r[0] for r in smooth_results], [r[1] for r in smooth_results], alpha=0.3, label='Smoothing')
ax2.scatter([r[0] for r in collapse_results], [r[1] for r in collapse_results], alpha=0.3, label='Collapse')
ax2.set_xlabel('H_top')
ax2.set_ylabel('COD')
ax2.set_title('COD vs Impedance')
ax2.legend()

plt.tight_layout()
plt.show()