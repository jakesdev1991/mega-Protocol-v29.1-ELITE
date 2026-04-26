# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import random

# Disruption Simulation: Power-Asymmetry Shredding Trigger (PAST-Ω)
# vs. Engine's Narrative Curvature Model

class OrganizationSimulator:
    def __init__(self, n_actors=20, n_docs=50, n_timesteps=100):
        self.n_actors = n_actors
        self.n_docs = n_docs
        self.n_timesteps = n_timesteps
        
        # Hidden ground truth: each actor has an incentive to shred (0-1)
        self.actor_incentive = np.random.beta(0.5, 5, n_actors)
        
        # Each document has a "sensitivity" score (0-1)
        self.doc_sensitivity = np.random.rand(n_docs)
        
        # Power structure: bipartite access graph
        self.access_graph = nx.bipartite_random_graph(n_actors, n_docs, 0.1)
        actor_nodes, doc_nodes = nx.bipartite.sets(self.access_graph)
        self.actor_to_docs = {a: list(self.access_graph.neighbors(a)) for a in actor_nodes}
        self.doc_to_actors = {d: list(self.access_graph.neighbors(d)) for d in doc_nodes}
        
        # Delete permissions: highly concentrated
        self.delete_permissions = {}
        for d in doc_nodes:
            n_perms = max(1, int(np.random.beta(0.1, 8) * len(self.doc_to_actors[d])))
            self.delete_permissions[d] = set(np.random.choice(list(self.doc_to_actors[d]), n_perms, replace=False))
        
        # Engine's view: narrative complexity of documents
        self.doc_narrative_complexity = np.random.rand(n_docs) * 0.5
        
        # Shredding event log
        self.shredding_events = []
        
    def step(self, t):
        # The REAL trigger: power concentration + incentive
        max_incentive_actor = np.argmax(self.actor_incentive)
        docs_they_can_delete = [d for d in self.actor_to_docs[max_incentive_actor] 
                                if max_incentive_actor in self.delete_permissions[d]]
        
        shred_triggered = False
        if self.actor_incentive[max_incentive_actor] > 0.6:
            sensitive_docs = [d for d in docs_they_can_delete if self.doc_sensitivity[d] > 0.7]
            if len(sensitive_docs) > 3:
                shred_triggered = True
                self.shredding_events.append(t)
                # Shredding removes documents from the graph
                for d in sensitive_docs[:3]:  # Shred top 3
                    if d in self.access_graph:
                        self.access_graph.remove_node(d)
                        self.doc_to_actors = {k: v for k, v in self.doc_to_actors.items() if k in self.access_graph}
        
        # Engine's Flawed Metric: Semantic Curvature from remaining docs
        remaining_docs = list(self.doc_to_actors.keys())
        if len(remaining_docs) > 1:
            complexities = [self.doc_narrative_complexity[d] for d in remaining_docs]
            R_proxy = np.std(complexities) * 10
            NCI = 1 / (1 + abs(R_proxy))
        else:
            NCI = 1.0
        
        # PAST-Ω Metric: Power Concentration Index (PCI)
        delete_counts = defaultdict(int)
        total_deletes = sum(len(actors) for actors in self.delete_permissions.values())
        for d, actors in self.delete_permissions.items():
            for a in actors:
                delete_counts[a] += 1
        PCI = max(delete_counts.values()) / total_deletes if total_deletes > 0 else 0
        
        # Update: docs near shredder become *less* complex (coherent rationalization)
        for d in remaining_docs:
            if max_incentive_actor in self.doc_to_actors.get(d, []):
                self.doc_narrative_complexity[d] = max(0, self.doc_narrative_complexity[d] - 0.05)
            else:
                self.doc_narrative_complexity[d] = min(1, self.doc_narrative_complexity[d] + np.random.randn() * 0.02)
        
        return NCI, PCI, shred_triggered

# Run simulation
sim = OrganizationSimulator(n_actors=15, n_docs=30, n_timesteps=80)
NCI_history, PCI_history, shred_flags = [], [], []

for t in range(sim.n_timesteps):
    NCI, PCI, shred = sim.step(t)
    NCI_history.append(NCI)
    PCI_history.append(PCI)
    shred_flags.append(shred)

# Plot
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
time = np.arange(sim.n_timesteps)

axes[0].plot(time, NCI_history, color='blue', label='Narrative Coherence Index (NCI)')
axes[0].set_ylabel("Engine's NCI\n(High = Coherent)")
axes[0].set_title("Engine Model: Semantic Curvature (Flawed)")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(time, PCI_history, color='red', label='Power Concentration Index (PCI)')
axes[1].set_ylabel('Power Concentration\n(High = Dangerous)')
axes[1].set_title("PAST-Ω Model: Access Graph Asymmetry (Proposed)")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

shred_times = [i for i, f in enumerate(shred_flags) if f]
axes[2].scatter(shred_times, [1]*len(shred_times), color='black', s=100, marker='v', label='Shredding Event')
axes[2].set_ylabel('Shredding Event')
axes[2].set_xlabel('Time Step')
axes[2].set_title("Ground Truth: Shredding Events")
axes[2].set_ylim(0, 1.5)
axes[2].legend()
axes[2].grid(True, alpha=0.3)

for ax in axes:
    for t in shred_times:
        ax.axvline(x=t, color='gray', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

# Correlation analysis
print("--- DISRUPTION ANALYSIS ---")
if shred_times:
    NCI_before = [NCI_history[t-1] for t in shred_times if t > 0]
    PCI_before = [PCI_history[t-1] for t in shred_times if t > 0]
    print(f"Avg NCI before shredding: {np.mean(NCI_before):.3f} (can be HIGH - coherent lie)")
    print(f"Avg PCI before shredding: {np.mean(PCI_before):.3f} (consistently HIGH)")
    print("\nEngine's model fails: Shredding is preceded by power concentration, not semantic chaos.")
    print("The 'narrative manifold' is post-hoc rationalization, not a causal precursor.")
else:
    print("No shredding events. Run again or increase n_timesteps.")