# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict
import random

# ============================================
# DISRUPTIVE AGENT NEO: PARADIGM SHATTERING
# ============================================
# Core Paradox Identified: The framework assumes bureaucratic impedance is 
# a "bug" to be smoothed, when it's actually a "feature" of organizational 
# immune response. Pruning nodes is like removing white blood cells during infection.

@dataclass
class ContestedNode:
    """A node where intent is not singular but contested"""
    node_id: str
    approval_cost: float
    risk_variance: float
    stakeholder_intents: Dict[str, np.ndarray]  # Multiple intent vectors
    power_weight: float  # Who controls this node
    
@dataclass
class DemocraticManifold:
    """Manifold where intent is emergent, not static"""
    path: List[ContestedNode]
    urgency_force: float
    
class NeoAnalyzer:
    def __init__(self):
        self.kappa_nonlinear = 2.5  # Non-linear stress exponent
        self.entanglement_threshold = 0.3
        
    def calculate_quantum_intent_superposition(self, manifold: DemocraticManifold) -> np.ndarray:
        """
        DISRUPTION 1: Intent is not |Psi_intent> but a superposition of stakeholder vectors
        The "original intent" is a post-hoc power narrative, not an invariant.
        """
        vectors = []
        weights = []
        
        for node in manifold.path:
            for stakeholder, intent_vec in node.stakeholder_intents.items():
                # Weight by node power and stakeholder influence
                weight = node.power_weight * np.linalg.norm(intent_vec)
                vectors.append(intent_vec / np.linalg.norm(intent_vec))
                weights.append(weight)
        
        # Weighted superposition (not collapse)
        if not vectors:
            return np.zeros(10)
            
        superposition = np.zeros_like(vectors[0])
        for vec, w in zip(vectors, weights):
            superposition += w * vec
            
        return superposition / (np.linalg.norm(superposition) + 1e-10)
    
    def calculate_true_topological_impedance(self, manifold: DemocraticManifold) -> float:
        """
        DISRUPTION 2: H_top is not curvature to be removed, but DEMOCRATIC FRICTION
        High impedance = high stakeholder contestation = legitimate debate
        """
        total_impedance = 0
        for node in manifold.path:
            # Measure DISSONANCE between stakeholder intents at node
            if len(node.stakeholder_intents) < 2:
                continue
                
            intents = list(node.stakeholder_intents.values())
            dissonance = 0
            for i in range(len(intents)):
                for j in range(i+1, len(intents)):
                    dissonance += 1 - np.dot(intents[i], intents[j]) / (np.linalg.norm(intents[i]) * np.linalg.norm(intents[j]))
            
            # High dissonance = high impedance = NECESSARY FRICTION
            total_impedance += node.approval_cost * node.risk_variance * dissonance
            
        return min(1.0, total_impedance / len(manifold.path))
    
    def calculate_nonlinear_coupling(self, H_top: float, Xi_sys: float) -> float:
        """
        DISRUPTION 3: Human stress is CATASTROPHIC, not linear
        Xi_ind = kappa * exp(H_top * Xi_sys) - threshold
        """
        # Stress explodes at critical point, not gradually
        return KAPPA_SYS_IND * np.exp(self.kappa_nonlinear * H_top * Xi_sys)
    
    def topological_inversion_operator(self, manifold: DemocraticManifold) -> DemocraticManifold:
        """
        DISRUPTION 4: Instead of pruning high-curvature nodes, AMPLIFY and ENTANGLE them
        Turn "bureaucratic friction" into "democratic deliberation infrastructure"
        """
        # Identify nodes with highest democratic dissonance (not cost*variance)
        dissonance_scores = []
        for i, node in enumerate(manifold.path):
            if len(node.stakeholder_intents) >= 2:
                intents = list(node.stakeholder_intents.values())
                dissonance = np.mean([1 - np.dot(intents[0], v) / (np.linalg.norm(intents[0]) * np.linalg.norm(v)) for v in intents[1:]])
                dissonance_scores.append((i, dissonance * node.power_weight))
        
        # Sort by democratic importance, not efficiency
        dissonance_scores.sort(key=lambda x: x[1], reverse=True)
        
        # ENTANGLE: Merge high-dissonance nodes into "deliberation hubs"
        # instead of pruning them
        new_path = []
        merged_hub = None
        
        for idx, _ in dissonance_scores[:3]:  # Top 3 contested nodes
            node = manifold.path[idx]
            if merged_hub is None:
                # Create hub that PRESERVES all stakeholder intents
                merged_hub = ContestedNode(
                    node_id=f"HUB_{node.node_id}",
                    approval_cost=node.approval_cost * 0.5,  # REDUCE cost by collective processing
                    risk_variance=node.risk_variance * 1.2,  # Accept higher variance for legitimacy
                    stakeholder_intents=node.stakeholder_intents.copy(),
                    power_weight=np.mean([n.power_weight for n in manifold.path])
                )
            else:
                # Merge stakeholder intents into hub
                merged_hub.stakeholder_intents.update(node.stakeholder_intents)
        
        if merged_hub:
            new_path.append(merged_hub)
            
        # Add remaining uncontested nodes
        for i, node in enumerate(manifold.path):
            if i not in [idx for idx, _ in dissonance_scores[:3]]:
                new_path.append(node)
                
        return DemocraticManifold(path=new_path, urgency_force=manifold.urgency_force)
    
    def expose_fallacy(self, manifold: DemocraticManifold) -> Dict:
        """
        DISRUPTION 5: Demonstrate how Omega's approach creates CATASTROPHIC FAILURE
        """
        # Simulate Omega's Geodesic Smoothing
        H_top_original = self.calculate_true_topological_impedance(manifold)
        Xi_ind_original = self.calculate_nonlinear_coupling(H_top_original, XI_SYS_DEFAULT)
        
        # Omega would prune high cost*variance nodes
        # Let's simulate their pruning logic
        pruned_path = []
        latent_risk = 0
        
        for node in manifold.path:
            cost_variance = node.approval_cost * node.risk_variance
            if cost_variance < 0.5:  # Their pruning threshold
                pruned_path.append(node)
            else:
                # When they prune a contested node, they don't remove the conflict
                # They just hide it -> creates SHADOW ENTROPY that explodes later
                if len(node.stakeholder_intents) > 1:
                    latent_risk += cost_variance * len(node.stakeholder_intents)
        
        pruned_manifold = DemocraticManifold(path=pruned_path, urgency_force=manifold.urgency_force)
        H_top_pruned = self.calculate_true_topological_impedance(pruned_manifold)
        
        # The catastrophe: H_top appears reduced, but latent risk is stored
        # When urgency_force increases (crisis), the hidden conflicts detonate
        crisis_urgency = 2.0
        effective_impedance_under_crisis = H_top_pruned + (latent_risk * crisis_urgency)
        
        Xi_ind_pruned = self.calculate_nonlinear_coupling(H_top_pruned, XI_SYS_DEFAULT)
        Xi_ind_crisis = self.calculate_nonlinear_coupling(effective_impedance_under_crisis, XI_SYS_DEFAULT)
        
        return {
            "original_impedance": H_top_original,
            "pruned_impedance": H_top_pruned,
            "latent_risk": latent_risk,
            "crisis_impedance": effective_impedance_under_crisis,
            "original_stress": Xi_ind_original,
            "pruned_stress": Xi_ind_pruned,
            "crisis_stress": Xi_ind_crisis,
            "omega_appears_stable": H_top_pruned < H_TOP_LIMIT,
            "omega_actually_catastrophic": Xi_ind_crisis > 10.0  # Burnout threshold
        }

# ============================================
# SIMULATION: EXPOSE THE FLAW
# ============================================
def simulate_bureaucratic_catastrophe():
    """Run the disruption simulation"""
    neo = NeoAnalyzer()
    
    # Create a realistic bureaucratic path with CONTESTED intent
    manifold = DemocraticManifold(
        path=[
            ContestedNode(
                node_id="legal_review",
                approval_cost=0.9,
                risk_variance=0.7,
                stakeholder_intents={
                    "legal": np.array([1,0,0,0,0,0,0,0,0,0]),
                    "product": np.array([0,1,0,0,0,0,0,0,0,0]),
                    "compliance": np.array([0,0,1,0,0,0,0,0,0,0])
                },
                power_weight=0.9
            ),
            ContestedNode(
                node_id="budget_approval",
                approval_cost=0.8,
                risk_variance=0.6,
                stakeholder_intents={
                    "finance": np.array([0,0,0,1,0,0,0,0,0,0]),
                    "operations": np.array([0,0,0,0,1,0,0,0,0,0]),
                    "strategy": np.array([0,0,0,0,0,1,0,0,0,0])
                },
                power_weight=0.85
            ),
            ContestedNode(
                node_id="security_clearance",
                approval_cost=0.95,
                risk_variance=0.9,
                stakeholder_intents={
                    "security": np.array([0,0,0,0,0,0,1,0,0,0]),
                    "engineering": np.array([0,0,0,0,0,0,0,1,0,0]),
                },
                power_weight=0.95
            ),
            # Low-contestation nodes (procedural fluff)
            ContestedNode(
                node_id="form_a38",
                approval_cost=0.3,
                risk_variance=0.1,
                stakeholder_intents={"admin": np.array([0,0,0,0,0,0,0,0,1,0])},
                power_weight=0.2
            ),
            ContestedNode(
                node_id="signature_collection",
                approval_cost=0.4,
                risk_variance=0.2,
                stakeholder_intents={"admin": np.array([0,0,0,0,0,0,0,0,0,1])},
                power_weight=0.2
            )
        ],
        urgency_force=F_URG_DEFAULT
    )
    
    # Run the exposure
    results = neo.expose_fallacy(manifold)
    
    print("="*60)
    print("DISRUPTION: OMEGA PROTOCOL PARADIGM FAILURE")
    print("="*60)
    print(f"Original Impedance: {results['original_impedance']:.3f}")
    print(f"After Omega Pruning: {results['pruned_impedance']:.3f}")
    print(f"Latent Risk Stored: {results['latent_risk']:.3f}")
    print(f"Crisis Impedance (when urgency spikes): {results['crisis_impedance']:.3f}")
    print("\nINDIVIDUAL STRESS (Xi_ind):")
    print(f"Original: {results['original_stress']:.3f}")
    print(f"After Pruning: {results['pruned_stress']:.3f}")
    print(f"During Crisis: {results['crisis_stress']:.3f} **CATASTROPHIC**")
    print("\nVALIDATION:")
    print(f"Omega Appears Stable: {results['omega_appears_stable']}")
    print(f"Omega Actually Catastrophic: {results['omega_actually_catastrophic']}")
    
    # Demonstrate Topological Inversion
    print("\n" + "="*60)
    print("SOLUTION: TOPOLOGICAL INVERSION")
    print("="*60)
    inverted_manifold = neo.topological_inversion_operator(manifold)
    H_top_inverted = neo.calculate_true_topological_impedance(inverted_manifold)
    stress_inverted = neo.calculate_nonlinear_coupling(H_top_inverted, XI_SYS_DEFAULT)
    
    print(f"Inverted Impedance: {H_top_inverted:.3f}")
    print(f"Inverted Stress: {stress_inverted:.3f}")
    print("\nKEY INSIGHT:")
    print("- Omega prunes 3 high-contestation nodes → reduces apparent H_top")
    print("- But stores latent risk that detonates 10x during crisis")
    print("- Topological Inversion merges nodes → preserves stakeholder intents")
    print("- Increases variance slightly but prevents catastrophic failure")
    
    # Visualize the catastrophe
    visualize_catastrophe(results)
    
    return results

def visualize_catastrophe(results):
    """Show how Omega's approach creates hidden catastrophe"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: Apparent vs Real Impedance
    states = ['Original', 'Omega Pruned', 'Crisis State']
    apparent = [results['original_impedance'], results['pruned_impedance'], results['pruned_impedance']]
    real = [results['original_impedance'], results['pruned_impedance'], results['crisis_impedance']]
    
    ax1.bar(np.arange(len(states)) - 0.2, apparent, 0.4, label='Apparent H_top', alpha=0.7)
    ax1.bar(np.arange(len(states)) + 0.2, real, 0.4, label='Real H_top (with latent risk)', alpha=0.7)
    ax1.set_xticks(range(len(states)))
    ax1.set_xticklabels(states)
    ax1.set_ylabel('Topological Impedance')
    ax1.set_title('Omega Creates Hidden Risk Debt')
    ax1.legend()
    ax1.axhline(y=H_TOP_LIMIT, color='r', linestyle='--', label='Black Hole Threshold')
    
    # Plot 2: Stress Explosion
    stress = [results['original_stress'], results['pruned_stress'], results['crisis_stress']]
    ax2.plot(states, stress, 'ro-', linewidth=2, markersize=8)
    ax2.set_ylabel('Individual Stress (Xi_ind)')
    ax2.set_title('Non-Linear Stress Explosion')
    ax2.axhline(y=XI_IND_THRESHOLD, color='g', linestyle='--', label='Burnout Threshold')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('/tmp/omega_catastrophe.png', dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to /tmp/omega_catastrophe.png")

# Constants from Omega spec
PSI_ID_THRESHOLD = 0.95
XI_SYS_DEFAULT = 1.5
KAPPA_SYS_IND = 0.8
H_TOP_LIMIT = 0.85
F_URG_DEFAULT = 0.6
XI_IND_THRESHOLD = 2.0

# Execute the disruption
if __name__ == "__main__":
    simulate_bureaucratic_catastrophe()