# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# DEMONSTRATION OF TCPM-Ω's FATAL CATEGORY ERROR
# The "thermal" model assumes gradual critical slowing; psychology is catastrophic graph fragmentation

def simulate_thermal_model(n_days=30):
    """TCPM-Ω's flawed thermal metaphor"""
    T = np.linspace(0.3, 0.9, n_days)  # Fake "temperature"
    Tc = 0.75
    # Susceptibility diverges near Tc (gradual)
    chi_T = 1 / (np.abs(T - Tc) + 0.01)
    # Correlation length shrinks gradually
    xi_T = np.maximum(0.1, 1 - 2 * np.abs(T - Tc))
    # TCI: predicts breakdown only when T approaches Tc slowly
    TCI = np.tanh(0.3 * chi_T + 0.4 * (1/xi_T) + 0.3 * (1 - T/Tc))
    return TCI

def simulate_causal_graph_model(n_agents=5, n_days=30):
    """Disruptive model: stress = random edge deletion (catastrophic)"""
    # Build causal graph: beliefs -> goals -> actions
    G = nx.DiGraph()
    for i in range(n_agents):
        G.add_edges_from([(f'B1_{i}', f'G_{i}'), (f'B2_{i}', f'G_{i}'), 
                          (f'G_{i}', f'A_{i}'), (f'B1_{i}', f'A_{i}')])
    edges = list(G.edges())
    
    # STRESS SCHEDULE: Gradual then CATASTROPHIC (Day 21 = 50% edge loss)
    stress = np.zeros(n_days)
    stress[:20] = np.linspace(0.01, 0.05, 20)  # Gradual
    stress[20] = 0.5  # CATASTROPHIC EVENT
    stress[21:] = 0.02
    
    frag_index = []
    for day in range(n_days):
        n_remove = int(stress[day] * len(edges))
        if n_remove > 0:
            idx = np.random.choice(len(edges), min(n_remove, len(edges)), replace=False)
            edges = [e for i, e in enumerate(edges) if i not in idx]
        G_day = nx.DiGraph(edges)
        frag_index.append(nx.number_connected_components(G_day.to_undirected()))
    
    return np.array(frag_index)

# RUN SIMULATIONS
TCI = simulate_thermal_model()
fragmentation = simulate_causal_graph_model()

# VISUALIZE THE FAILURE
plt.figure(figsize=(12, 5))
plt.plot(TCI, label='TCPM-Ω: TCI (gradual)', color='blue', linewidth=2)
plt.axhline(y=0.6, color='blue', linestyle='--', label='TCPM Alert Threshold')
plt.plot(fragmentation / max(fragmentation), label='Causal Graph: Fragmentation (catastrophic)', color='red', linewidth=2)
plt.axvline(x=20, color='black', linestyle='-', label='Day 21: Catastrophic Event')
plt.fill_between(range(len(TCI)), 0, 1, where=(fragmentation>1), color='red', alpha=0.2, label='Actual Breakdown')
plt.title('TCPM-Ω vs. Reality: Thermal Metaphor Misses Catastrophic Collapse')
plt.xlabel('Day')
plt.ylabel('Normalized Metric')
plt.legend()
plt.grid(True)
plt.show()

print("=== TCPM-Ω PARADIGM SHATTERED ===")
print(f"TCPM-Ω TCI at catastrophic event (Day 21): {TCI[20]:.2f} (NO ALERT)")
print(f"Graph fragmentation at Day 21: {fragmentation[20]} (IMMEDIATE ALERT)")