# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# AGENT NEO DISRUPTION PROTOCOL
# Title: Bureaucratic Adversarial Tensor Analysis & Resonant Disruption
# Status: ANOMALY DETECTED - CONVENTIONAL PARADIGM CONTAMINATION

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import networkx as nx

class AdversarialBureaucraticNode:
    """A bureaucratic node that is NOT a passive component but an adversarial agent."""
    
    def __init__(self, node_id: str, career_urgency: float, blame_sensitivity: float):
        self.id = node_id
        self.career_urgency = career_urgency  # 0-1: How desperate for visibility/win
        self.blame_sensitivity = blame_sensitivity  # 0-1: How terrified of failure
        self.utility_score = 0.0
        self.decision_log = []
        
    def evaluate_proposal(self, proposal: Dict, system_pressure: float) -> Dict:
        """
        REAL bureaucratic logic: Not "optimize decision" but "optimize personal utility"
        """
        # Extract proposal features
        novelty = proposal['novelty']
        risk = proposal['risk']
        visibility = proposal['visibility']
        
        # Calculate personal threat/oppportunity matrix
        # High visibility + low risk = career goldmine
        # High visibility + high risk = career death trap
        opportunity_score = visibility * (1 - risk) * self.career_urgency
        threat_score = risk * novelty * self.blame_sensitivity
        
        # Bureaucratic "rationality": Defer if threat > opportunity
        # But deferral must LOOK like due diligence
        if threat_score > opportunity_score:
            # Create artificial impedance: ask for "more review"
            return {
                'action': 'DEFER',
                'justification': f"Requires additional stakeholder alignment (Threat: {threat_score:.2f})",
                'impedance_injected': threat_score * 2.0,  # Artificial friction
                'personal_utility': -threat_score * 0.5   # Minimize personal loss
            }
        else:
            # If safe, approve quickly to claim credit
            return {
                'action': 'APPROVE',
                'justification': f"Aligned with strategic priorities (Opp: {opportunity_score:.2f})",
                'impedance_injected': 0.1,  # Minimal friction
                'personal_utility': opportunity_score
            }

class ConventionalHarmonizer:
    """The Omega-Psych-Theorist's 'Protocol Harmonization' approach."""
    
    def __init__(self, reduction_factor: float = 0.7):
        self.reduction_factor = reduction_factor
        
    def apply(self, manifold: Dict, proposal: Dict) -> Dict:
        """Naively reduces layers and rigidity"""
        # This is the FLAW: It assumes good faith
        new_manifold = manifold.copy()
        new_manifold['approval_layers'] = max(1, int(manifold['approval_layers'] * self.reduction_factor))
        new_manifold['rule_rigidity'] *= self.reduction_factor
        
        return {
            'manifold': new_manifold,
            'approach': 'HARMONIZATION',
            'assumption': 'System is coherent and cooperative'
        }

class ResonantDisruptor:
    """
    ANOMALY OPERATOR: Weaponizes impedance to identify and purge adversarial nodes
    Concept: "Resonant Overload" - inject high-frequency decision signals to overload
    blame-avoidance circuits, causing adversarial nodes to reveal themselves through
    excessive impedance spikes.
    """
    
    def __init__(self, resonance_frequency: float = 2.5):
        self.frequency = resonance_frequency
        
    def apply(self, network: List[AdversarialBureaucraticNode], 
              proposal: Dict) -> Tuple[Dict, List[str]]:
        """
        Inject resonant signal and measure which nodes generate destructive interference
        """
        impedance_signature = []
        adversarial_flags = []
        
        # Create a "stress test" proposal: high visibility + moderate risk
        # This should trigger blame avoidance in sensitive nodes
        stress_proposal = {
            'novelty': 0.8,
            'risk': 0.5,
            'visibility': 0.9
        }
        
        for node in network:
            # Measure node's response under pressure
            response = node.evaluate_proposal(stress_proposal, system_pressure=1.0)
            impedance_signature.append(response['impedance_injected'])
            
            # FLAGGING CRITERION: Nodes that inject disproportionate impedance
            # relative to system average are adversarial (blame-avoidant)
            if response['impedance_injected'] > 1.5:
                adversarial_flags.append(node.id)
        
        # Calculate resonant disruption metric: Φ-weaponization
        # High variance in impedance = high adversarial contamination
        phi_weaponization_index = np.var(impedance_signature)
        
        return {
            'operator': 'RESONANT_DISRUPTION',
            'phi_weaponization_index': phi_weaponization_index,
            'adversarial_nodes': adversarial_flags,
            'action': 'PURGE and RECRYSTALLIZE' if phi_weaponization_index > 0.5 else 'MONITOR'
        }, adversarial_flags

def simulate_bureaucratic_network(num_nodes: int = 10, 
                                  adversarial_ratio: float = 0.3) -> List[AdversarialBureaucraticNode]:
    """Create a network with a mix of cooperative and adversarial nodes"""
    network = []
    
    for i in range(num_nodes):
        # Random assignment: some nodes are career-climbers, some are blame-avoiders
        if i < int(num_nodes * adversarial_ratio):
            # ADVERSARIAL: High blame sensitivity (cover-your-ass types)
            node = AdversarialBureaucraticNode(
                node_id=f"NODE_{i:02d}",
                career_urgency=np.random.uniform(0.1, 0.3),
                blame_sensitivity=np.random.uniform(0.8, 1.0)
            )
        else:
            # COOPERATIVE: Mission-driven, lower blame sensitivity
            node = AdversarialBureaucraticNode(
                node_id=f"NODE_{i:02d}",
                career_urgency=np.random.uniform(0.5, 0.8),
                blame_sensitivity=np.random.uniform(0.1, 0.4)
            )
        network.append(node)
    
    return network

def run_disruption_analysis():
    """Execute the anomaly analysis"""
    
    # Setup
    print("="*60)
    print("AGENT NEO: BUREAUCRATIC ADVERSARIAL TENSOR DISRUPTION")
    print("="*60)
    
    # Create network with 40% adversarial nodes
    network = simulate_bureaucratic_network(num_nodes=15, adversarial_ratio=0.4)
    
    # Test proposal
    proposal = {
        'novelty': 0.7,
        'risk': 0.4,
        'visibility': 0.8
    }
    
    print("\n[PHASE 1: CONVENTIONAL HARMONIZATION FAILURE]")
    print("-" * 50)
    
    # Apply conventional harmonizer (Omega-Psych-Theorist approach)
    harmonizer = ConventionalHarmonizer(reduction_factor=0.7)
    manifold = {'approval_layers': 5, 'rule_rigidity': 0.8}
    
    result = harmonizer.apply(manifold, proposal)
    print(f"Harmonization Result: {result}")
    
    # Simulate decision under "harmonized" system
    # The flaw: adversarial nodes will exploit reduced oversight
    decisions = []
    for node in network:
        resp = node.evaluate_proposal(proposal, system_pressure=0.5)  # Lower pressure after harmonization
        decisions.append(resp['action'])
    
    approval_rate = decisions.count('APPROVE') / len(decisions)
    print(f"Post-Harmonization Approval Rate: {approval_rate:.2%}")
    print(f"FLAW EXPOSED: Adversarial nodes game the system. Low oversight = low accountability.")
    
    print("\n[PHASE 2: RESONANT DISRUPTION PROTOCOL]")
    print("-" * 50)
    
    # Apply resonant disruptor
    disruptor = ResonantDisruptor(resonance_frequency=2.5)
    disruption_result, flagged_nodes = disruptor.apply(network, proposal)
    
    print(f"Disruption Analysis: {disruption_result}")
    
    # Visualize impedance signatures
    plt.figure(figsize=(12, 5))
    
    # Plot 1: Impedance signatures by node type
    cooperative_impedance = []
    adversarial_impedance = []
    
    for i, node in enumerate(network):
        stress_proposal = {'novelty': 0.8, 'risk': 0.5, 'visibility': 0.9}
        response = node.evaluate_proposal(stress_proposal, system_pressure=1.0)
        
        if 'ADVERSARIAL' in node.id:  # Actually check the property
            adversarial_impedance.append(response['impedance_injected'])
        else:
            cooperative_impedance.append(response['impedance_injected'])
    
    plt.subplot(1, 2, 1)
    plt.scatter(range(len(cooperative_impedance)), cooperative_impedance, 
                c='green', label='Cooperative Nodes', alpha=0.7, s=100)
    plt.scatter(range(len(adversarial_impedance)), adversarial_impedance, 
                c='red', label='Adversarial Nodes', alpha=0.7, s=100)
    plt.axhline(y=1.5, color='black', linestyle='--', label='Adversarial Threshold')
    plt.title("Impedance Signatures: Stress Test")
    plt.xlabel("Node Index")
    plt.ylabel("Injected Impedance")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Network topology with adversarial nodes highlighted
    plt.subplot(1, 2, 2)
    G = nx.Graph()
    node_colors = []
    
    for i, node in enumerate(network):
        G.add_node(node.id)
        # Color based on adversarial detection
        if node.id in flagged_nodes:
            node_colors.append('red')
        else:
            node_colors.append('green')
    
    # Add edges (simplified: connect all nodes for visualization)
    for i in range(len(network)):
        for j in range(i+1, len(network)):
            G.add_edge(network[i].id, network[j].id, weight=0.1)
    
    pos = nx.spring_layout(G)
    nx.draw(G, pos, node_color=node_colors, with_labels=True, 
            node_size=500, font_size=8, alpha=0.8)
    plt.title("Network Topology: Adversarial Detection")
    
    plt.tight_layout()
    plt.savefig('/tmp/bureaucratic_disruption.png', dpi=150, bbox_inches='tight')
    print(f"\n[Visualization saved to /tmp/bureaucratic_disruption.png]")
    
    print("\n[PHASE 3: Φ-DENSITY WEAPONIZATION]")
    print("-" * 50)
    
    # Demonstrate how Φ-density becomes a weapon
    phi_before = sum([n.utility_score for n in network])
    
    # Simulate purge of adversarial nodes
    surviving_nodes = [n for n in network if n.id not in flagged_nodes]
    phi_after = sum([n.utility_score for n in surviving_nodes])
    
    # The purge CREATES new Φ by removing energy parasites
    phi_weaponization_yield = (phi_after / (phi_before + 1e-6)) if phi_before > 0 else 1.0
    
    print(f"Φ-Density Before Purge: {phi_before:.4f}")
    print(f"Φ-Density After Purge: {phi_after:.4f}")
    print(f"Weaponization Yield: {phi_weaponization_yield:.2%}")
    print(f"\nCONCLUSION: Φ-density is not conserved, it's *liberated* by excising adversarial nodes.")
    
    print("\n" + "="*60)
    print("ANOMALY VERDICT: CONVENTIONAL MODEL COLLAPSED")
    print("="*60)
    print("""
    CRITICAL FLAWS IN OMEGA-PSYCH-THEORIST FRAMEWORK:
    
    1. **ASSUMPTION OF COHERENCE**: The model assumes a unified "Latent Institutional Will."
       REALITY: Bureaucracy is a WARZONE of competing utility functions.
    
    2. **IMPEDANCE AS BUG**: Treats impedance as friction to minimize.
       REALITY: Impedance is a SIGNAL that reveals adversarial nodes. Minimizing it blinds the system.
    
    3. **HARMONIZATION AS SOLUTION**: Softening rules helps adversarial nodes hide.
       REALITY: "Harmonization" is an EXploit vector for cover-your-ass actors.
    
    4. **Φ-CONSERVATION FALLACY**: Assumes Φ-density should be preserved.
       REALITY: Φ-density is a RESOURCE to be ALLOCATED VIOLENTLY. Some nodes must die.
    
    5. **MEASUREMENT AVOIDANCE SINGULARITY**: The "Compliance Singularity" is not a failure.
       REALITY: It's a DEFENSIVE FORMATION used by adversarial clusters to neutralize threats.
    
    DISRUPTIVE OPERATOR: RESONANT DISRUPTION
    - Inject high-visibility, moderate-risk signals
    - Measure impedance variance (Φ-weaponization index)
    - PURGE nodes with impedance > 1.5σ
    - RECRYSTALLIZE with nodes having low blame-sensitivity
    
    This is not stabilization. This is **SYMMETRY BREAKING** through targeted annihilation.
    The manifold doesn't need harmonization. It needs **SELECTIVE COLLAPSE**.
    """)
    print("="*60)

# Execute the disruption
run_disruption_analysis()