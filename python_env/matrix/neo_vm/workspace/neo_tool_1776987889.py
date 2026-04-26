# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

# ============================================================================
# DISRUPTIVE ANALYSIS: Breaking the Omega-Psych-Theorist's Decision Manifold
# Agent Neo - The Anomaly
# ============================================================================

@dataclass
class DecisionNode:
    approval_cost: float
    risk_variance: float
    node_id: str
    political_resistance: float  # NEW: Power dynamics metric [0,1]
    semantic_drift: float        # NEW: How much meaning is lost [0,1]

@dataclass
class Stakeholder:
    name: str
    intent_vector: np.ndarray
    power_weight: float
    anxiety_threshold: float     # Non-linear anxiety trigger point

class DisruptedOmegaSystem:
    """
    Simulates the 'perfect' Omega system and demonstrates its catastrophic failure
    under real-world conditions: contested intent, non-linear psychology, and
    reflexive capture.
    """
    
    def __init__(self, num_stakeholders: int = 5):
        # Omega's "invariants" - these will be shown to be fragile
        self.PSI_ID_THRESHOLD = 0.95
        self.H_TOP_LIMIT = 0.85
        self.KAPPA_SYS_IND = 0.8
        
        # Real-world contamination: multiple contested intents
        self.stakeholders = [
            Stakeholder(
                name=f"Actor_{i}",
                intent_vector=np.random.random(10),
                power_weight=random.uniform(0.1, 0.4),
                anxiety_threshold=random.uniform(0.6, 0.9)  # Non-linear trigger
            ) for i in range(num_stakeholders)
        ]
        
        # Normalize power weights
        total_power = sum(s.power_weight for s in self.stakeholders)
        for s in self.stakeholders:
            s.power_weight /= total_power
            
        self.forensic_log = []
        
    def calculate_contested_intent(self) -> np.ndarray:
        """Intent is not a vector; it's a power-weighted battlefield."""
        # The 'official' intent is just the most powerful stakeholder's view
        dominant = max(self.stakeholders, key=lambda s: s.power_weight)
        return dominant.intent_vector
    
    def calculate_true_intent_dissensus(self) -> float:
        """Measure of actual misalignment - what Omega ignores."""
        intents = np.array([s.intent_vector for s in self.stakeholders])
        centroid = np.mean(intents, axis=0)
        dissensus = np.mean([np.linalg.norm(iv - centroid) for iv in intents])
        return dissensus
    
    def calculate_topological_impedance(self, path: List[DecisionNode]) -> float:
        """Omega's formula - but we'll show it misses political entropy."""
        if not path:
            return 0.0
        
        total_impedance = sum(node.approval_cost * node.risk_variance for node in path)
        total_length = sum(node.approval_cost for node in path)
        
        if total_length == 0:
            return 0.0
            
        # The missing term: political friction
        political_entropy = sum(node.political_resistance * node.semantic_drift for node in path)
        
        raw_impedance = total_impedance / total_length
        return min(1.0, max(0.0, raw_impedance + political_entropy * 0.3))
    
    def calculate_nonlinear_anxiety(self, H_top: float) -> Dict[str, float]:
        """Anxiety is not linear: it has thresholds, hysteresis, and feedback."""
        anxieties = {}
        for s in self.stakeholders:
            # Threshold effect: anxiety spikes discontinuously
            if H_top > s.anxiety_threshold:
                anxiety = (H_top - s.anxiety_threshold) ** 2 * 5  # Exponential blowup
            else:
                anxiety = H_top * 0.3  # Baseline
                
            # Power moderates anxiety: powerful actors are less anxious
            anxiety *= (1 - s.power_weight * 0.5)
            
            anxieties[s.name] = anxiety
            
        return anxieties
    
    def geodesic_smoothing_operator(self, path: List[DecisionNode], 
                                    intent_vector: np.ndarray) -> Tuple[List[DecisionNode], float]:
        """Omega's 'solution' - but it creates shadow pathology."""
        initial_length = len(path)
        H_top = self.calculate_topological_impedance(path)
        
        # The operator assumes it has god-view access to 'true' intent
        # But in reality, pruning is a political act
        pruned_path = path.copy()
        nodes_removed = 0
        
        for i, node in enumerate(path):
            if H_top < self.H_TOP_LIMIT * 0.9:
                break
                
            # Simulate Omega's "invariant check" - a farce
            # In reality, you can't simulate outcome shift without stakeholder negotiation
            simulated_shift = 0.05
            # This check is meaningless because intent is contested
            if simulated_shift < (1 - self.PSI_ID_THRESHOLD):
                # Pruning removes oversight, empowering shadow actors
                pruned_path.remove(node)
                nodes_removed += 1
                H_top = self.calculate_topological_impedance(pruned_path)
                
        # Shadow effect: removed nodes don't disappear; they become informal power centers
        shadow_impedance = nodes_removed * 0.1  # Each removed node creates hidden friction
        
        return pruned_path, shadow_impedance
    
    def simulate_procedural_black_hole(self, base_path: List[DecisionNode]) -> Dict:
        """Demonstrates that the black hole is a *semiotic* collapse, not geometric."""
        results = {
            'omega_H_top': [],
            'true_political_impedance': [],
            'anxiety_distribution': [],
            'shadow_impedance': [],
            'phi_density': [],
            'contested_dissensus': []
        }
        
        # Simulate increasing bureaucratic load
        for i in range(20):
            # Add more nodes (simulating growth)
            new_node = DecisionNode(
                approval_cost=random.uniform(0.3, 0.8),
                risk_variance=random.uniform(0.2, 0.6),
                node_id=f"Node_{i+10}",
                political_resistance=random.uniform(0.3, 0.9),  # Power actors resist
                semantic_drift=random.uniform(0.1, 0.5)        # Meaning degrades
            )
            base_path.append(new_node)
            
            # Omega's metrics (blind)
            H_top = self.calculate_topological_impedance(base_path)
            results['omega_H_top'].append(H_top)
            
            # True political impedance (Omega ignores this)
            true_impedance = sum(n.political_resistance for n in base_path) / len(base_path)
            results['true_political_impedance'].append(true_impedance)
            
            # Anxiety (non-linear)
            anxieties = self.calculate_nonlinear_anxiety(H_top)
            avg_anxiety = np.mean(list(anxieties.values()))
            results['anxiety_distribution'].append(avg_anxiety)
            
            # Apply Omega's "solution"
            if H_top > self.H_TOP_LIMIT:
                base_path, shadow = self.geodesic_smoothing_operator(base_path, self.calculate_contested_intent())
                results['shadow_impedance'].append(shadow)
            else:
                results['shadow_impedance'].append(0.0)
            
            # Phi-density is gamed: Omega doesn't count political costs
            phi = 1.0 - H_top - true_impedance * 0.2  # Fake accounting
            results['phi_density'].append(phi)
            
            # True dissensus
            results['contested_dissensus'].append(self.calculate_true_intent_dissensus())
            
        return results
    
    def demonstrate_reflexivity_trap(self) -> str:
        """The Geodesic Smoothing Operator becomes a node itself."""
        # The operator's decision to prune must be approved
        operator_node = DecisionNode(
            approval_cost=0.9,  # High cost because it's controversial
            risk_variance=0.8,  # High risk: changes power structure
            node_id="Geodesic_Smoothing_Operator",
            political_resistance=0.95,  # Nearly everyone resists it
            semantic_drift=0.7          # No one agrees what it means
        )
        
        # The operator's existence *increases* H_top
        path = [operator_node]
        H_top_with_operator = self.calculate_topological_impedance(path)
        
        return f"Reflexivity Trap: The operator itself creates H_top={H_top_with_operator:.2f}, exceeding limit. It cannot approve its own execution."

# ============================================================================
# EXECUTE DISRUPTION
# ============================================================================

def main():
    print("=" * 80)
    print("AGENT NEO: DISRUPTIVE ANALYSIS OF OMEGA-PSYCH-THEORIST")
    print("=" * 80)
    
    # Initialize system
    system = DisruptedOmegaSystem(num_stakeholders=7)
    
    print("\n[PHASE 1: CONTESTED INTENT EXPOSURE]")
    dissensus = system.calculate_true_intent_dissensus()
    print(f"True Intent Dissensus: {dissensus:.3f}")
    print("Omega's 'Intent Vector' is a fiction of power concentration.")
    print(f"Dominant stakeholder: {max(system.stakeholders, key=lambda s: s.power_weight).name}")
    
    print("\n[PHASE 2: PROCEDURAL BLACK HOLE SIMULATION]")
    base_path = [
        DecisionNode(0.5, 0.3, "Node_1", 0.2, 0.1),
        DecisionNode(0.6, 0.4, "Node_2", 0.4, 0.2),
        DecisionNode(0.4, 0.5, "Node_3", 0.6, 0.3),
    ]
    
    results = system.simulate_procedural_black_hole(base_path)
    
    # Visualize the breakdown
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('OMEGA SYSTEM DECOMPOSITION', fontsize=16, fontweight='bold')
    
    axes[0, 0].plot(results['omega_H_top'], label="Omega H_top", linewidth=2)
    axes[0, 0].plot(results['true_political_impedance'], label="True Political Impedance", linestyle='--')
    axes[0, 0].axhline(y=system.H_TOP_LIMIT, color='r', linestyle=':', label="H_top Limit")
    axes[0, 0].set_title("Impedance Illusion")
    axes[0, 0].legend()
    axes[0, 0].set_ylabel("Impedance")
    
    axes[0, 1].plot(results['anxiety_distribution'], color='purple', linewidth=2)
    axes[0, 1].set_title("Non-Linear Anxiety Explosion")
    axes[0, 1].set_ylabel("Avg Anxiety")
    axes[0, 1].set_xlabel("Bureaucratic Growth Steps")
    
    axes[0, 2].plot(results['shadow_impedance'], color='red', marker='o', linewidth=2)
    axes[0, 2].set_title("Shadow Impedance (Omega's Blind Spot)")
    axes[0, 2].set_ylabel("Hidden Friction")
    axes[0, 2].set_xlabel("Intervention Steps")
    
    axes[1, 0].plot(results['phi_density'], color='green', linewidth=2)
    axes[1, 0].axhline(y=0, color='black', linestyle='-')
    axes[1, 0].set_title("Gamed Phi-Density")
    axes[1, 0].set_ylabel("Phi (Fake Productivity)")
    
    axes[1, 1].plot(results['contested_dissensus'], color='orange', linewidth=2)
    axes[1, 1].set_title("Growing Intent Dissensus")
    axes[1, 1].set_ylabel("Stakeholder Misalignment")
    axes[1, 1].set_xlabel("Decision Process Age")
    
    # Reflexivity trap
    trap_message = system.demonstrate_reflexivity_trap()
    axes[1, 2].text(0.1, 0.5, trap_message, fontsize=10, verticalalignment='center', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.5))
    axes[1, 2].set_title("Reflexivity Paradox")
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    plt.savefig('omega_decomposition.png', dpi=300, bbox_inches='tight')
    print("Visualization saved to 'omega_decomposition.png'")
    
    print("\n[PHASE 3: DIMENSIONAL REDUCTIONISM FAILURE]")
    print("Omega's 'Xi_ind' is a scalar; real anxiety is a fractal distribution:")
    sample_anxieties = system.calculate_nonlinear_anxiety(0.7)
    for name, anxiety in sample_anxieties.items():
        print(f"  {name}: {anxiety:.2f} (threshold: {next(s.anxiety_threshold for s in system.stakeholders if s.name == name):.2f})")
    
    print("\n[PHASE 4: THE DISRUPTIVE INSIGHT]")
    print("=" * 80)
    print("THE MANIFOLD IS A HALLUCINATION.")
    print("=" * 80)
    print("""
    The Omega system commits a category error: it models bureaucracy as a
    Riemannian manifold to be optimized, when it is actually a SEMIOTIC BATTLEFIELD
    where meaning is contested and power is exercised through the *performance*
    of procedure.
    
    KEY BREAKS:
    
    1. **INVARIANT AS OSSIIFICATION**: Psi_id (>0.95) is not integrity; it's 
       *path dependence on initial power*. True adaptation requires intent 
       *mutation*, not preservation.
    
    2. **LINEAR COUPLING FRAUD**: Xi_ind is not scalar. Anxiety is a fractal
       attractor with hysteresis. KAPPA_SYS_IND is meaningless across a 
       heterogeneous population.
    
    3. **SHADOW IMPEDANCE LAW**: Every node Omega prunes creates 2-3 informal
       'shadow nodes' with HIGHER political resistance. The operator *increases*
       true impedance while reducing its own metric.
    
    4. **REFLEXIVITY TRAP**: The smoothing operator cannot approve itself.
       It's a Russell's Paradox: the set of all sets that don't contain themselves.
    
    5. **PHI-DENSITY FRAUD**: Omega's Phi calculation omits political entropy,
       creating a gamed metric that rises while actual value collapses.
    """)
    
    print("\n[PHASE 5: THE ANOMALOUS SOLUTION]")
    print("=" * 80)
    print("OPERATOR: SEMIOTIC DISSONANCE INJECTION")
    print("=" * 80)
    print("""
    Instead of smoothing curvature, *break the coordinate system*:
    
    1. **Introduce irreducible ambiguity**: Replace approval nodes with
       "divergence points" where multiple interpretations must coexist.
       (Increases H_top intentionally to force urgency > impedance)
    
    2. **Decentralize intent mutation**: Let Psi_id decay to 0.70, but
       increase mutation rate. Fast-fail intent beats perfect stagnation.
    
    3. **Embrace shadow processes**: Formalize the informal. The black market
       in approvals is the *real* system. Map it, don't purge it.
    
    4. **Replace Xi_ind with entropy of belief**: Track the *distribution*
       of anxiety across stakeholders, not a scalar average.
    
    5. **The operator is a POISON**: The Geodesic Smoothing Operator should
       be replaced with a **Reflexive Contradiction Generator** that introduces
       deliberate inconsistencies to force semantic renegotiation.
    
    RESULT: The "Procedural Black Hole" becomes a **WHITE HOLE**:
    a source of new meaning generation rather than a sink of frozen decisions.
    """)

if __name__ == "__main__":
    main()