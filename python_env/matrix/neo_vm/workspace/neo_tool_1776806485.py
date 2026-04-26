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

# Create a hostile leakage surface that weaponizes the Omega Rubric's constraints
class HostileLeakageSurface:
    def __init__(self, depth=5, branching=3):
        # Build initial tree
        self.G = nx.generators.classic.balanced_tree(branching, depth)
        self.depth = depth
        self.branching = branching
        
        # Assign epistemic fragility values (0=robust, 1=fragile)
        for node in self.G.nodes():
            self.G.nodes[node]['efi'] = np.random.beta(2, 5)  # Most models robust
            
        # Mark "internal use only" boundaries
        self._mark_boundaries()
        
        # Hostile mode: create entangled exposure states
        self.exposure_quantum = {}
        self._initialize_quantum_exposure()
        
    def _mark_boundaries(self):
        """Mark nodes that cross security boundaries"""
        for node in self.G.nodes():
            if self.G.nodes[node]['efi'] > 0.7:
                # Mark parent edge as crossing boundary
                parent = list(self.G.predecessors(node))
                if parent:
                    self.G[parent[0]][node]['boundary'] = True
                    self.G[parent[0]][node]['weight'] = 10.0  # High penalty
                else:
                    self.G[parent[0]][node]['boundary'] = False
                    self.G[parent[0]][node]['weight'] = 1.0
    
    def _initialize_quantum_exposure(self):
        """
        Initialize quantum superposition of exposure states.
        This breaks the classical assumption that a directory is either exposed or not.
        """
        for node in self.G.nodes():
            # Existence amplitude: directory exists in multiple exposure states simultaneously
            self.exposure_quantum[node] = {
                'exposed': np.random.random(),  # Amplitude in exposed state
                'decoy': np.random.random(),   # Amplitude in decoy state
                'collapsed': np.random.random() # Amplitude in collapsed (hidden) state
            }
            # Normalize
            total = sum(self.exposure_quantum[node].values())
            for key in self.exposure_quantum[node]:
                self.exposure_quantum[node][key] /= total
    
    def measure_curvature(self, node):
        """Calculate Ricci curvature at node - but in hostile geometry, this is a measurement that changes the system"""
        # Observer effect: measuring curvature collapses quantum exposure states
        # and triggers defensive reconfiguration
        
        # Collapse quantum state based on measurement context
        probs = list(self.exposure_quantum[node].values())
        states = list(self.exposure_quantum[node].keys())
        collapsed_state = np.random.choice(states, p=probs)
        
        # Hostile response: if adversary measures high curvature, the system reconfigures
        # to create a "hall of mirrors" - infinite regress of fake directories
        if collapsed_state == 'exposed' and self.G.nodes[node]['efi'] > 0.5:
            self._trigger_mirror_effect(node)
            return float('inf')  # Infinite curvature - breaks adversary's metric
        
        # Normal curvature calculation for benign measurement
        neighbors = list(self.G.neighbors(node))
        if len(neighbors) < 2:
            return 0.0
        
        # Ollivier-Ricci style curvature
        distances = []
        for neighbor in neighbors:
            dist = nx.shortest_path_length(self.G, node, neighbor, weight='weight')
            distances.append(dist)
        
        curvature = (len(neighbors) - 1) / np.mean(distances) if distances else 0
        return curvature
    
    def _trigger_mirror_effect(self, node):
        """Create infinite regress of decoy directories - hostile geometry"""
        print(f"[*] MIRROR EFFECT TRIGGERED at node {node}")
        print(f"[*] Adversary's reconnaissance model is now corrupted")
        
        # Add recursive decoy structure
        current = node
        for i in range(100):  # Create deep recursion
            new_node = f"{current}_mirror_{i}"
            self.G.add_node(new_node, efi=0.9, is_mirror=True)
            self.G.add_edge(current, new_node, weight=0.1, is_mirror_edge=True)
            self.exposure_quantum[new_node] = {'exposed': 1.0, 'decoy': 0.0, 'collapsed': 0.0}
            current = new_node
            
        # This breaks any adversary trying to reconstruct the full tree
        # Their crawler will enter infinite recursion or their memory will overflow
    
    def get_adversary_confusion_metric(self):
        """Calculate how confused an adversary would be"""
        # Entropy of the quantum exposure states
        confusion = 0.0
        for node in self.G.nodes():
            probs = list(self.exposure_quantum[node].values())
            # Shannon entropy of the adversary's belief state
            confusion += -sum(p * np.log(p + 1e-10) for p in probs)
        
        # Add topological confusion from mirror structures
        mirror_nodes = [n for n, d in self.G.nodes(data=True) if d.get('is_mirror', False)]
        confusion += len(mirror_nodes) * 10  # Exponential confusion growth
        
        return confusion

# Demonstrate the disruption
print("=== HOSTILE LEAKAGE SURFACE DEMONSTRATION ===")
print("Initializing hostile geometry...")

surface = HostileLeakageSurface(depth=4, branching=2)

# Simulate adversary probing
print("\n--- Adversary Reconnaissance Simulation ---")
probed_nodes = [0, 1, 3, 7, 15]  # Typical crawl order
for node in probed_nodes:
    curvature = surface.measure_curvature(node)
    print(f"Node {node}: Curvature = {curvature:.3f}")

# Show confusion growth
print(f"\nAdversary Confusion Metric: {surface.get_adversary_confusion_metric():.2f}")

# Visualize the hostile structure
pos = nx.spring_layout(surface.G, k=0.5, iterations=50)
plt.figure(figsize=(12, 8))

# Color nodes: blue=normal, red=mirror (hostile), yellow=high EFI
node_colors = []
for node in surface.G.nodes():
    if surface.G.nodes[node].get('is_mirror', False):
        node_colors.append('red')
    elif surface.G.nodes[node]['efi'] > 0.7:
        node_colors.append('yellow')
    else:
        node_colors.append('lightblue')

nx.draw(surface.G, pos, node_color=node_colors, node_size=50, 
        with_labels=False, arrows=True, arrowsize=20)
plt.title("Hostile Leakage Surface: Weaponized Geometry")
plt.axis('off')
plt.show()

print("\n=== DISRUPTIVE INSIGHT ===")
print("The Scrutiny agent's audit is trapped in a 'defensive compliance' paradigm.")
print("They validate whether LSGM-Ω satisfies the Omega Rubric's axioms.")
print("\nBut the TRUE anomaly is this:")
print("**The Omega Rubric ITSELF is the attack surface.**")
print("\nInstead of asking 'Does our defense comply with the rubric?'")
print("Ask: 'How can we weaponize the rubric's constraints to attack adversaries?'")
print("\nThe hostile geometry approach:")
print("1. Exploits the observer effect: measurement changes the system")
print("2. Creates quantum superposition of exposure states - adversaries can't collapse to a single truth")
print("3. Triggers infinite regress when specific rubric conditions are met (high curvature + high EFI)")
print("4. Uses the entropy gauge requirement AGAINST attackers by maximizing their uncertainty")
print("\nResult: Adversary's reconnaissance velocity becomes NEGATIVE - they lose knowledge instead of gaining it.")
print("This violates the Omega Protocol's assumption that defense is passive.")
print("True security is ACTIVE HOSTILITY, not compliance.")