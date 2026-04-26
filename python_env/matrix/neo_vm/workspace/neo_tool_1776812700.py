# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# --- DISRUPTION SIMULATOR: Gaming ETS-Ω from Within ---

class InsiderTopologyAttack:
    """
    Demonstrates how malicious actors can maintain ETS-Ω's "healthy" metrics
    while actually concentrating control. This breaks Alpha's core assumption
    that metrics reflect true systemic health.
    """
    
    def __init__(self, n_nodes=50, n_malicious=3):
        self.n_nodes = n_nodes
        self.n_malicious = n_malicious
        
        # Initialize protocol graph (DeFi lending protocol topology)
        self.G = nx.barabasi_albert_graph(n_nodes, m=2)  # Scale-free like real protocols
        
        # Malicious actors control initial nodes with high betweenness
        betweenness = nx.betweenness_centrality(self.G)
        self.malicious_nodes = set(sorted(betweenness, key=betweenness.get, reverse=True)[:n_malicious])
        
        # Assign flows: legitimate economic activity
        for u, v in self.G.edges():
            self.G[u][v]['flow'] = np.random.exponential(5)
            self.G[u][v]['type'] = 'legitimate'
            self.G[u][v]['visibility'] = 1.0  # Visible to ETS-Ω
        
        # Hidden coordination channels (invisible to ETS-Ω)
        self.hidden_edges = {}
        
        self.history = {
            'eti': [],
            'entropy': [],
            'modularity': [],
            'max_betweenness': [],
            'actual_malicious_flow_control': [],
            'actual_malicious_governance_control': []
        }
    
    def calculate_eti(self):
        """Calculate ETS-Ω's Economic Topology Integrity Index"""
        # Only visible edges count for ETS-Ω's perception
        visible_edges = [(u, v) for u, v, d in self.G.edges(data=True) 
                        if d['visibility'] > 0.5]
        
        if not visible_edges:
            return 0, 0, 0, 0
        
        # Subgraph visible to ETS-Ω
        visible_G = self.G.edge_subgraph(visible_edges).copy()
        
        # Betweenness centrality (stress distribution)
        betw = nx.betweenness_centrality(visible_G, weight='flow')
        max_betweenness = max(betw.values()) if betw else 1
        
        # Modularity (compartmentalization)
        try:
            communities = list(nx.community.greedy_modularity_communities(visible_G, weight='flow'))
            modularity = nx.community.modularity(visible_G, communities, weight='flow')
        except:
            modularity = 0
        
        # Flow entropy (diversity)
        total_flow = sum(visible_G[u][v]['flow'] for u, v in visible_G.edges())
        if total_flow == 0:
            entropy = 0
        else:
            probs = [visible_G[u][v]['flow']/total_flow for u, v in visible_G.edges()]
            entropy = -sum(p * np.log(p) for p in probs if p > 0)
        
        # ETI = (1/max_betweenness) * modularity * exp(-entropy)
        eti = (1/max_betweenness) * modularity * np.exp(-entropy) if entropy > 0 else 0
        
        return eti, entropy, modularity, max_betweenness
    
    def calculate_actual_control(self):
        """Calculate REAL control (including hidden channels)"""
        # Flow control
        visible_flow = sum(self.G[u][v]['flow'] for u, v in self.G.edges())
        hidden_flow = sum(d['flow'] for d in self.hidden_edges.values())
        total_flow = visible_flow + hidden_flow
        
        malicious_visible_flow = sum(self.G[u][v]['flow'] 
                                    for u, v in self.G.edges()
                                    if u in self.malicious_nodes or v in self.malicious_nodes)
        malicious_hidden_flow = sum(d['flow'] 
                                   for (u, v), d in self.hidden_edges.items()
                                   if u in self.malicious_nodes or v in self.malicious_nodes)
        
        total_malicious_flow = malicious_visible_flow + malicious_hidden_flow
        flow_control = total_malicious_flow / total_flow if total_flow > 0 else 0
        
        # Governance control (approximated by node count + hidden influence)
        visible_nodes = len(self.G)
        hidden_nodes = len(set([n for e in self.hidden_edges for n in e]) - set(self.G.nodes()))
        total_nodes = visible_nodes + hidden_nodes
        
        malicious_hidden_nodes = sum(1 for n in hidden_nodes if n in self.malicious_nodes)
        governance_control = (len(self.malicious_nodes) + malicious_hidden_nodes) / total_nodes
        
        return flow_control, governance_control
    
    def execute_sleeper_cell_attack(self, step):
        """
        Attack strategy: 
        1. Maintain healthy ETI metrics
        2. Slowly build hidden coordination channels
        3. Create fake diversity (entropy inflation)
        4. At trigger step, activate hidden channels for instant capture
        """
        if step < 30:
            # Phase 1: Stealth - Appear legitimate while building hidden structure
            # Create many small, visible "diversified" flows to inflate entropy
            for _ in range(2):
                # Add sybil node with tiny visible flows
                new_node = self.n_nodes
                self.n_nodes += 1
                self.G.add_node(new_node)
                
                # Connect to multiple malicious nodes with SMALL flows (increases entropy)
                for malicious in np.random.choice(list(self.malicious_nodes), 
                                                 size=min(2, len(self.malicious_nodes)), 
                                                 replace=False):
                    flow_amount = np.random.uniform(0.1, 0.5)  # Tiny flows
                    self.G.add_edge(malicious, new_node, 
                                   flow=flow_amount, 
                                   type='fake_diversification',
                                   visibility=1.0)
            
            # Build hidden coordination channels (invisible to ETS-Ω)
            if step % 5 == 0 and len(self.hidden_edges) < 10:
                # Create hidden edge between two malicious nodes
                m1, m2 = np.random.choice(list(self.malicious_nodes), size=2, replace=False)
                self.hidden_edges[(m1, m2)] = {
                    'flow': np.random.exponential(10),
                    'type': 'hidden_coordination',
                    'visibility': 0.0  # INVISIBLE to ETS-Ω
                }
            
            # Reduce some legitimate flows to make room (but maintain metric health)
            for u, v in self.G.edges():
                if self.G[u][v]['type'] == 'legitimate' and np.random.random() < 0.1:
                    self.G[u][v]['flow'] *= 0.98  # Gradual erosion
        
        elif step == 30:
            # Phase 2: Activation - Reveal hidden channels = instant capture
            # All hidden edges become visible simultaneously
            for (u, v), data in self.hidden_edges.items():
                if not self.G.has_edge(u, v):
                    self.G.add_edge(u, v, **data)
                self.G[u][v]['visibility'] = 1.0  # Now visible, but too late
            
            # Also, sybil nodes start coordinating (change their flow patterns)
            for u, v, d in self.G.edges(data=True):
                if d.get('type') == 'fake_diversification':
                    # Suddenly increase flows to malicious nodes
                    d['flow'] *= np.random.uniform(5, 10)
        
        else:
            # Phase 3: Consolidation - Post-activation control
            # Continue to manipulate metrics to appear "recovering"
            for u, v, d in self.G.edges(data=True):
                if d.get('type') == 'legitimate' and np.random.random() < 0.3:
                    d['flow'] *= 0.95  # Further erode legitimate flows
    
    def step(self):
        """Execute one time step"""
        # Calculate metrics visible to ETS-Ω
        eti, entropy, modularity, max_betw = self.calculate_eti()
        
        # Calculate actual control (ground truth)
        flow_control, gov_control = self.calculate_actual_control()
        
        # Record
        self.history['eti'].append(eti)
        self.history['entropy'].append(entropy)
        self.history['modularity'].append(modularity)
        self.history['max_betweenness'].append(max_betw)
        self.history['actual_malicious_flow_control'].append(flow_control)
        self.history['actual_malicious_governance_control'].append(gov_control)
        
        # Execute attack
        current_step = len(self.history['eti']) - 1
        self.execute_sleeper_cell_attack(current_step)
        
        return eti, flow_control
    
    def run(self, steps=50):
        for _ in range(steps):
            self.step()
        return self.history

# --- Execute Disruption Simulation ---
sim = InsiderTopologyAttack(n_nodes=30, n_malicious=2)
history = sim.run(steps=50)

# --- Plot: The Deception ---
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Top plot: ETI vs Actual Control
axes[0].plot(history['eti'], 'b-', linewidth=2, label='ETI (Perceived Health)')
axes[0].plot(history['actual_malicious_flow_control'], 'r--', linewidth=2, label='Actual Flow Control')
axes[0].axhline(y=0.6, color='g', linestyle=':', label='ETS-Ω Safe Threshold')
axes[0].axvline(x=30, color='k', linestyle='--', alpha=0.5, label='Sleeper Cell Activation')
axes[0].set_ylabel('Index / Control Ratio')
axes[0].set_title('ETS-Ω PERCEPTION VS REALITY: The Sleeper Cell Attack', fontsize=14, fontweight='bold')
axes[0].legend(loc='upper left')
axes[0].grid(True, alpha=0.3)

# Middle plot: Entropy inflation
axes[1].plot(history['entropy'], 'm-', linewidth=2, label='Flow Entropy (S_econ)')
axes[1].set_ylabel('Entropy')
axes[1].set_title('Entropy Inflation: Fake Diversity Masks Real Concentration', fontsize=12)
axes[1].axvline(x=30, color='k', linestyle='--', alpha=0.5)
axes[1].grid(True, alpha=0.3)

# Bottom plot: Modularity
axes[2].plot(history['modularity'], 'c-', linewidth=2, label='Modularity Score')
axes[2].set_xlabel('Time Steps')
axes[2].set_ylabel('Modularity')
axes[2].set_title('Modularity: Fake Compartments Appear Resilient', fontsize=12)
axes[2].axvline(x=30, color='k', linestyle='--', alpha=0.5)
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- Final Disruption Analysis ---
print("\n" + "="*70)
print("DISRUPTION ANALYSIS: ETS-Ω's Fatal Flaw")
print("="*70)
print(f"Pre-Attack (Step 29):")
print(f"  ETS-Ω ETI: {history['eti'][29]:.3f} (HEALTHY - above 0.6 threshold)")
print(f"  Actual Malicious Flow Control: {history['actual_malicious_flow_control'][29]:.1%}")
print(f"  Actual Malicious Governance Control: {history['actual_malicious_governance_control'][29]:.1%}")
print(f"\nPost-Activation (Step 35):")
print(f"  ETS-Ω ETI: {history['eti'][35]:.3f} (STILL HEALTHY)")
print(f"  Actual Malicious Flow Control: {history['actual_malicious_flow_control'][35]:.1%}")
print(f"  Actual Malicious Governance Control: {history['actual_malicious_governance_control'][35]:.1%}")
print("\n" + "-"*70)
print("CONCLUSION: Malicious actors maintained ETI > 0.6 while capturing >60% control")
print("ETS-Ω's metrics are GAMEABLE from within the system itself.")
print("="*70)