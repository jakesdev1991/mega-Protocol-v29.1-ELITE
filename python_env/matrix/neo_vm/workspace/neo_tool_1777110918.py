# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
NEO'S DISRUPTION ENGINE: Adversarial API Propagation Analysis
===========================================================

This script exposes the fundamental flaw in the epidemic modeling approach
and demonstrates why adversarial game theory is the correct paradigm.
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple
import random

@dataclass
class FacilityNode:
    """Represents a tokamak research facility in the collaboration network"""
    name: str
    api_exposure: float  # 0-1 scale
    safety_criticality: float  # 0-1, inverse of safety
    provenance_integrity: float  # 0-1
    node_centrality: float = 0.0  # Will be computed
    adversarial_value: float = 0.0  # Will be computed
    
    def __post_init__(self):
        # Adversarial value: high exposure + high criticality = high target value
        self.adversarial_value = self.api_exposure * (1 - self.safety_criticality)

class EpidemicModel:
    """The flawed v77.0-Ω model - passive diffusion"""
    
    def __init__(self, network: nx.Graph):
        self.network = network
        self.r0_cache = {}
        
    def calculate_r0(self, source: str) -> float:
        """Calculate R0 as average secondary infections (flawed: assumes random diffusion)"""
        # Get source node data
        source_data = self.network.nodes[source]['data']
        
        # Susceptibility fraction (simplified)
        susceptible = np.mean([
            1 - self.network.nodes[n]['data'].provenance_integrity 
            for n in self.network.neighbors(source)
        ])
        
        # Connectivity factor
        connectivity = len(list(self.network.neighbors(source))) / 20.0
        
        # Quarantine efficacy (random, no adversarial adaptation)
        quarantine = 0.3
        
        r0 = source_data.api_exposure * connectivity * susceptible * (1 - quarantine)
        return min(max(r0, 0.0), 1.0)
    
    def simulate_propagation(self, source: str, steps: int = 5) -> Dict[str, float]:
        """Simulate passive epidemic spread"""
        infected = {source: 1.0}
        propagation_history = []
        
        for step in range(steps):
            new_infected = {}
            for node, intensity in infected.items():
                neighbors = list(self.network.neighbors(node))
                for neighbor in neighbors:
                    if neighbor not in infected:
                        # Random transmission probability (naive)
                        transmission_prob = 0.3 * intensity
                        if random.random() < transmission_prob:
                            new_infected[neighbor] = transmission_prob
            
            infected.update(new_infected)
            propagation_history.append(len(infected))
        
        return infected, propagation_history

class AdversarialModel:
    """NEO'S DISRUPTION: Active adversarial optimization model"""
    
    def __init__(self, network: nx.Graph):
        self.network = network
        self.adversary_position = None
        
    def calculate_optimal_target_sequence(self, budget: int = 3) -> List[str]:
        """
        Adversary optimizes for maximum blast radius given detection constraints.
        This is a simplified version of a real adversarial optimization.
        """
        # Compute network centrality (PageRank - who is most "influential")
        centrality = nx.pagerank(self.network)
        
        # Update nodes with centrality
        for node, cent in centrality.items():
            self.network.nodes[node]['data'].node_centrality = cent
        
        # Sort by adversarial value: centrality × exposure × (1-safety)
        targets = sorted(
            self.network.nodes(),
            key=lambda n: (
                self.network.nodes[n]['data'].node_centrality * 
                self.network.nodes[n]['data'].adversarial_value
            ),
            reverse=True
        )
        
        # Adversary picks top-k targets, but avoids immediate detection
        # They'll start with moderately valuable nodes to avoid triggering superspreader alerts
        optimal_sequence = []
        for target in targets:
            if len(optimal_sequence) >= budget:
                break
            
            # Skip if it would trigger immediate superspreader detection (>0.7 centrality)
            if self.network.nodes[target]['data'].node_centrality > 0.7:
                continue
                
            optimal_sequence.append(target)
        
        return optimal_sequence
    
    def simulate_strategic_propagation(self, target_sequence: List[str]) -> Dict[str, float]:
        """
        Simulate adversarial strategy: targeted exploitation with stealth optimization
        """
        compromised = {}
        
        for target in target_sequence:
            # Adversary exploits target
            compromised[target] = 1.0
            
            # Calculate blast radius based on centrality
            neighbors = list(self.network.neighbors(target))
            for neighbor in neighbors:
                if neighbor not in compromised:
                    # Higher centrality = higher chance neighbor also compromised
                    target_centrality = self.network.nodes[target]['data'].node_centrality
                    neighbor_centrality = self.network.nodes[neighbor]['data'].node_centrality
                    
                    # Adversarial propagation: correlated with centrality
                    propagation_prob = target_centrality * neighbor_centrality
                    compromised[neighbor] = propagation_prob
        
        return compromised

def generate_realistic_network(n_facilities: int = 15) -> nx.Graph:
    """
    Generate a realistic tokamak collaboration network with hub-spoke topology
    """
    # Create a scale-free network (realistic for research collaborations)
    G = nx.barabasi_albert_graph(n_facilities, 2)
    
    # Assign realistic facility data
    facilities = [
        ("ITER", 0.9, 0.1, 0.95),  # High exposure, high safety, high provenance
        ("NIF", 0.85, 0.2, 0.90),
        ("JET", 0.8, 0.3, 0.85),
        ("KSTAR", 0.7, 0.4, 0.80),
        ("DIII-D", 0.65, 0.5, 0.75),
        ("ASDEX-U", 0.6, 0.6, 0.70),
        ("WEST", 0.55, 0.7, 0.65),
        ("EAST", 0.5, 0.8, 0.60),
        ("CFETR", 0.7, 0.3, 0.85),
        ("SPARC", 0.8, 0.2, 0.90),
        ("ARC", 0.75, 0.3, 0.88),
        ("Commonwealth", 0.6, 0.5, 0.70),
        ("Helion", 0.5, 0.6, 0.65),
        ("ZAP", 0.4, 0.7, 0.60),
        ("TAE", 0.3, 0.8, 0.55),
    ]
    
    for i, node in enumerate(G.nodes()):
        if i < len(facilities):
            name, exposure, safety, provenance = facilities[i]
        else:
            name = f"Facility_{i}"
            exposure = random.uniform(0.2, 0.8)
            safety = random.uniform(0.2, 0.8)
            provenance = random.uniform(0.5, 0.9)
        
        G.nodes[node]['data'] = FacilityNode(
            name=name,
            api_exposure=exposure,
            safety_criticality=safety,
            provenance_integrity=provenance
        )
    
    return G

def demonstrate_disruption():
    """
    Demonstrate the fundamental flaw in epidemic modeling vs adversarial optimization
    """
    print("=" * 80)
    print("NEO'S DISRUPTION: EXPOSING THE EPIDEMIC MODEL FALLACY")
    print("=" * 80)
    
    # Generate realistic network
    network = generate_realistic_network()
    
    # Select a source facility (moderate risk)
    source_node = 8  # CFETR - moderate centrality, high exposure
    
    print(f"\nSource Facility: {network.nodes[source_node]['data'].name}")
    print(f"API Exposure: {network.nodes[source_node]['data'].api_exposure:.2f}")
    print(f"Safety Criticality: {network.nodes[source_node]['data'].safety_criticality:.2f}")
    print(f"Provenance Integrity: {network.nodes[source_node]['data'].provenance_integrity:.2f}")
    
    # Run epidemic model
    print("\n" + "-"*40)
    print("EPIDEMIC MODEL (v77.0-Ω) - FLAWED")
    print("-"*40)
    
    epidemic = EpidemicModel(network)
    r0 = epidemic.calculate_r0(source_node)
    print(f"Calculated R0: {r0:.3f}")
    
    infected, history = epidemic.simulate_propagation(source_node, steps=5)
    print(f"Facilities 'infected' after 5 steps: {len(infected)}")
    print(f"Propagation history: {history}")
    
    # Run adversarial model
    print("\n" + "-"*40)
    print("ADVERSARIAL MODEL (NEO'S DISRUPTION) - CORRECT")
    print("-"*40)
    
    adversarial = AdversarialModel(network)
    targets = adversarial.calculate_optimal_target_sequence(budget=3)
    
    print("Optimal target sequence (adversary's strategy):")
    for i, target in enumerate(targets):
        node_data = network.nodes[target]['data']
        print(f"  {i+1}. {node_data.name} (Centrality: {node_data.node_centrality:.3f}, Value: {node_data.adversarial_value:.3f})")
    
    compromised = adversarial.simulate_strategic_propagation(targets)
    print(f"\nFacilities compromised by adversarial strategy: {len(compromised)}")
    
    # Calculate adversarial risk metric
    avg_centrality = np.mean([network.nodes[n]['data'].node_centrality for n in compromised])
    avg_adversarial_value = np.mean([network.nodes[n]['data'].adversarial_value for n in compromised])
    
    print(f"Average centrality of compromised nodes: {avg_centrality:.3f}")
    print(f"Average adversarial value: {avg_adversarial_value:.3f}")
    
    # The disruption: Show that epidemic model underestimates high-value targets
    print("\n" + "="*80)
    print("DISRUPTIVE INSIGHT")
    print("="*80)
    
    # Identify high-value nodes that epidemic model would miss
    high_value_nodes = [
        n for n in network.nodes() 
        if network.nodes[n]['data'].node_centrality > 0.15 
        and network.nodes[n]['data'].adversarial_value > 0.5
    ]
    
    epidemic_hit_high_value = len([n for n in high_value_nodes if n in infected])
    adversarial_hit_high_value = len([n for n in high_value_nodes if n in compromised])
    
    print(f"High-value target nodes (centrality > 0.15, adversarial value > 0.5): {len(high_value_nodes)}")
    print(f"Epidemic model hit: {epidemic_hit_high_value} ({epidemic_hit_high_value/len(high_value_nodes)*100:.1f}%)")
    print(f"Adversarial model hit: {adversarial_hit_high_value} ({adversarial_hit_high_value/len(high_value_nodes)*100:.1f}%)")
    
    if epidemic_hit_high_value < adversarial_hit_high_value:
        print("\n⚠️  EPIDEMIC MODEL BLINDNESS: The passive diffusion model underestimates")
        print("   adversarial targeting of high-value nodes by {:.1f}%".format(
            (adversarial_hit_high_value - epidemic_hit_high_value) / len(high_value_nodes) * 100
        ))
    
    # Visualization
    print("\nGenerating visualization...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Network layout
    pos = nx.spring_layout(network, seed=42)
    
    # Plot epidemic spread
    node_colors = ['red' if n in infected else 'lightblue' for n in network.nodes()]
    node_sizes = [network.nodes[n]['data'].api_exposure * 500 + 100 for n in network.nodes()]
    
    nx.draw_networkx_nodes(network, pos, node_color=node_colors, node_size=node_sizes, ax=ax1)
    nx.draw_networkx_edges(network, pos, alpha=0.3, ax=ax1)
    nx.draw_networkx_labels(network, pos, 
                           labels={n: network.nodes[n]['data'].name for n in network.nodes()},
                           font_size=8, ax=ax1)
    ax1.set_title("Epidemic Model: Random Diffusion\n(Red = 'Infected', Size = Exposure)")
    
    # Plot adversarial compromise
    node_colors2 = ['darkred' if n in compromised else 'lightgreen' for n in network.nodes()]
    nx.draw_networkx_nodes(network, pos, node_color=node_colors2, node_size=node_sizes, ax=ax2)
    nx.draw_networkx_edges(network, pos, alpha=0.3, ax=ax2)
    nx.draw_networkx_labels(network, pos,
                           labels={n: network.nodes[n]['data'].name for n in network.nodes()},
                           font_size=8, ax=ax2)
    ax2.set_title("Adversarial Model: Strategic Targeting\n(Dark Red = Compromised)")
    
    plt.tight_layout()
    plt.savefig('/tmp/api_propagation_disruption.png', dpi=150, bbox_inches='tight')
    print("Visualization saved to /tmp/api_propagation_disruption.png")
    
    return {
        'epidemic_coverage': len(infected),
        'adversarial_coverage': len(compromised),
        'high_value_nodes': len(high_value_nodes),
        'epidemic_high_value_hits': epidemic_hit_high_value,
        'adversarial_high_value_hits': adversarial_hit_high_value,
        'r0': r0,
        'avg_centrality': avg_centrality
    }

if __name__ == "__main__":
    results = demonstrate_disruption()
    
    print("\n" + "="*80)
    print("QUANTITATIVE BREAKDOWN")
    print("="*80)
    for key, value in results.items():
        print(f"{key.replace('_', ' ').title()}: {value:.3f}")
    
    print("\n" + "="*80)
    print("NEO'S DISRUPTIVE MANIFESTO")
    print("="*80)
    
    manifesto = """
    The v77.0-Ω epidemic model commits a cardinal sin: it treats intelligent
    adversaries as mindless viruses. This is not a minor implementation flaw—
    it's a category error that fundamentally misrepresents the threat landscape.
    
    KEY BREAKTHROUGHS:
    
    1. **Adversarial Utility Maximization > Passive Diffusion**
       - Viruses mutate randomly; adversaries optimize strategically
       - The epidemic model's R0 assumes random transmission probability
       - Reality: Adversaries actively target high-centrality nodes first
    
    2. **Strategic Stealth > Blind Propagation**
       - Viruses can't "lay low"; adversaries can maintain persistence
       - The model assumes immediate detection when R0 > threshold
       - Reality: Advanced adversaries exploit low-and-slow strategies
    
    3. **Network Topology is Dynamic, Not Static**
       - The model assumes fixed partner_facilities
       - Reality: Tokamak collaborations are project-based and fluid
       - Adversaries exploit temporary trust relationships
    
    4. **Entropy as Obfuscation, Not State**
       - Shannon entropy assumes independent probabilities
       - Reality: Facility compromise events are highly correlated
       - The entropy calculation is mathematically elegant but semantically void
    
    5. **Φ-Density is a Protocol-Specific Artifact, Not Truth**
       - The entire Φ-scoring system may be optimizing for the wrong objective
       - It rewards complexity and self-referential compliance over actual security
    
    THE DISRUPTIVE REPLACEMENT:
    
    Replace the entire epidemic framework with **Adversarial Game Theory + Network Deception**.
    
    New Risk Model:
    ```
    Risk = Adversarial_Utility × Network_Centrality × Deception_Gap
    ```
    
    Where Deception_Gap measures the difference between what the protocol *thinks*
    is happening vs. what the adversary is *actually* doing.
    
    Omega Protocol v78.0-Ω: **Counter-Deception Manifold**
    - Instead of tracking R0, track **Adversarial Belief Space**
    - Instead of herd immunity, implement **Dynamic Network Cloaking**
    - Instead of superspreader detection, deploy **Honeypot Centrality Sinks**
    
    The protocol shouldn't ask "How fast is this spreading?"
    It should ask: "What does the adversary *believe* about our network topology,
    and how can we make them optimize for a fake target?"
    
    This is the difference between **epidemic containment** and **adversary manipulation**.
    
    The former is reactive. The latter is Neo.
    """
    
    print(manifesto)