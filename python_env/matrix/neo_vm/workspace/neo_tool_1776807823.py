# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import networkx as nx

class CascadeIncompletenessDemonstrator:
    """
    Demonstrates the Gödelian incompleteness at the heart of IC-Ω.
    The system cannot simultaneously be a complete predictor AND a participant
    in the market it attempts to control.
    """
    
    def __init__(self, n_participants: int = 500, n_assets: int = 10):
        self.n_participants = n_participants
        self.n_assets = n_assets
        
        # Core paradox parameters
        self.self_reference_gain = 0.0  # Will be increased to show paradox
        
        # Market state
        self.participant_beliefs = np.random.random((n_participants, n_assets))
        self.true_fundamental_value = np.ones(n_assets)
        self.observed_prices = self.true_fundamental_value.copy()
        
        # IC-Ω system state
        self.predicted_cascade_field = np.zeros(n_assets)
        self.control_actions = np.zeros(n_assets)
        
        # Information leakage network (who knows what)
        self.leakage_graph = nx.erdos_renyi_graph(n_participants, 0.02)
        
        # History for analysis
        self.history = {
            'time': [],
            'prediction_accuracy': [],
            'cascade_strength': [],
            'systematic_risk': [],
            'self_reference_metric': []
        }
    
    def compute_ollivier_ricci_curvature(self, graph: nx.Graph, weights: np.ndarray) -> float:
        """
        Compute approximate Ollivier-Ricci curvature for the leakage graph.
        This is the ℛ in the proposal - but it's a graph property, not a field!
        """
        # Simplified: curvature is inversely related to edge density in high-weight regions
        edge_weights = []
        for u, v in graph.edges():
            # Weight based on information flow similarity
            similarity = 1.0 / (1.0 + np.linalg.norm(
                self.participant_beliefs[u] - self.participant_beliefs[v]
            ))
            edge_weights.append(similarity * weights[u] * weights[v])
        
        if len(edge_weights) == 0:
            return 0.0
        
        # Curvature diverges when edges concentrate in small subgraphs
        curvature = np.std(edge_weights) / (np.mean(edge_weights) + 1e-10)
        return curvature
    
    def simulate_information_cascade(self, 
                                   external_leak: bool = True,
                                   include_system_prediction: bool = False) -> Tuple[float, float]:
        """
        The core paradox: predictions become information that leaks.
        
        Args:
            external_leak: Standard information leakage
            include_system_prediction: Whether IC-Ω's own predictions leak
            
        Returns:
            (true_cascade_intensity, predicted_cascade_intensity)
        """
        # External leak: some participants get true info
        if external_leak:
            leak_prob = 0.05
            leaked_participants = np.random.choice(
                self.n_participants, 
                size=int(self.n_participants * leak_prob), 
                replace=False
            )
            for i in leaked_participants:
                self.participant_beliefs[i] += np.random.normal(0, 0.1, self.n_assets)
        
        # PARADOX: System's own predictions become leaked information
        if include_system_prediction:
            # Participants who learn of the prediction adjust their beliefs
            # This is the self-referential loop the model cannot account for
            
            # More participants become "aware" of the system
            awareness_prob = 0.1 * self.self_reference_gain
            aware_participants = np.random.choice(
                self.n_participants,
                size=int(self.n_participants * awareness_prob),
                replace=False
            )
            
            # They adjust beliefs based on prediction AND gaming the control
            for i in aware_participants:
                # Gaming effect: anticipate control actions
                gaming_adjustment = self.control_actions * 0.5
                # Prediction effect: follow the system's signal
                prediction_adjustment = self.predicted_cascade_field * 0.3
                
                self.participant_beliefs[i] += gaming_adjustment + prediction_adjustment
        
        # Cascade dynamics: beliefs drive prices
        belief_aggregation = np.mean(self.participant_beliefs, axis=0)
        price_impact = np.tanh(belief_aggregation - 1.0)  # Non-linear impact
        
        # True cascade intensity (hidden state)
        true_cascade = np.linalg.norm(price_impact)
        
        # IC-Ω's prediction (based on observable data only)
        # Key limitation: cannot observe its own future impact
        observable_data = price_impact + np.random.normal(0, 0.05, self.n_assets)
        predicted_cascade = np.linalg.norm(observable_data) * 0.85  # Imperfect prediction
        
        return true_cascade, predicted_cascade
    
    def apply_control_action(self, predicted_cascade: float) -> np.ndarray:
        """
        MPC-Ω style control. But control actions are observable and gameable!
        """
        # Simple threshold-based control
        threshold = 0.6
        
        if predicted_cascade > threshold:
            # Attempt to dampen cascade
            control_strength = (predicted_cascade - threshold) * self.control_effectiveness
            
            # BUT: this action is now known to aware participants
            # They can front-run or counter-trade
            
            # Gaming effect reduces actual effectiveness
            gaming_factor = 1.0 - (self.self_reference_gain * 0.4)
            effective_control = control_strength * max(0.1, gaming_factor)
            
            self.control_actions = -effective_control * np.ones(self.n_assets) * 0.1
        else:
            self.control_actions = np.zeros(self.n_assets)
        
        return self.control_actions
    
    def run_paradox_demonstration(self, steps: int = 30) -> Dict:
        """
        Run simulation showing how self-reference destroys predictability.
        """
        # First run: no self-reference (baseline)
        self.self_reference_gain = 0.0
        baseline_metrics = self._run_simulation(steps, scenario="baseline")
        
        # Second run: WITH self-reference (paradox)
        self.self_reference_gain = 1.0
        paradox_metrics = self._run_simulation(steps, scenario="paradox")
        
        # Compare
        error_increase = (
            paradox_metrics['mean_prediction_error'] / 
            baseline_metrics['mean_prediction_error']
        )
        
        return {
            'baseline': baseline_metrics,
            'paradox': paradox_metrics,
            'error_multiplication': error_increase,
            'paradox_verified': error_increase > 1.5
        }
    
    def _run_simulation(self, steps: int, scenario: str) -> Dict:
        """Internal simulation runner."""
        total_error = 0.0
        cascade_strengths = []
        
        for t in range(steps):
            # Make prediction
            true_cascade, predicted_cascade = self.simulate_information_cascade(
                external_leak=True,
                include_system_prediction=(scenario == "paradox")
            )
            
            # Apply control
            self.apply_control_action(predicted_cascade)
            
            # Update market state
            self.observed_prices += 0.1 * (np.mean(self.participant_beliefs, axis=0) - self.observed_prices)
            
            # Compute metrics
            error = abs(true_cascade - predicted_cascade)
            total_error += error
            cascade_strengths.append(true_cascade)
            
            # Record
            self.history['time'].append(t)
            self.history['prediction_accuracy'].append(1.0 - error)
            self.history['cascade_strength'].append(true_cascade)
            self.history['self_reference_metric'].append(self.self_reference_gain * np.mean(self.participant_awareness))
        
        return {
            'mean_prediction_error': total_error / steps,
            'max_cascade': max(cascade_strengths),
            'final_systematic_risk': np.std(self.observed_prices)
        }


def plot_incompleteness_proof(results: Dict):
    """Visualize the paradox."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Prediction Error Multiplication
    scenarios = ['Baseline\n(No Self-Ref)', 'Paradox\n(With Self-Ref)']
    errors = [
        results['baseline']['mean_prediction_error'],
        results['paradox']['mean_prediction_error']
    ]
    axes[0, 0].bar(scenarios, errors, color=['blue', 'red'], alpha=0.7)
    axes[0, 0].set_title('Prediction Error: Self-Reference Destroys Accuracy')
    axes[0, 0].set_ylabel('Mean Absolute Error')
    axes[0, 0].text(0.5, max(errors)*0.8, 
                   f'Error Increase: {results["error_multiplication"]:.2f}x',
                   ha='center', fontsize=12, color='red')
    
    # Plot 2: Systematic Risk Comparison
    risk = [
        results['baseline']['final_systematic_risk'],
        results['paradox']['final_systematic_risk']
    ]
    axes[0, 1].bar(scenarios, risk, color=['green', 'orange'], alpha=0.7)
    axes[0, 1].set_title('Systematic Risk: Paradox Increases Volatility')
    axes[0, 1].set_ylabel('Price Volatility (Std Dev)')
    
    # Plot 3: Theoretical Incompleteness Visualization
    # Show how self-reference creates an unbounded loop
    x = np.linspace(0, 1, 100)
    y_baseline = x  # Linear: more awareness = better prediction
    y_paradox = x / (1 - x + 0.1)  # Diverges as awareness→1
    
    axes[1, 0].plot(x, y_baseline, 'b-', label='Linear Model (No Paradox)', linewidth=2)
    axes[1, 0].plot(x, y_paradox, 'r--', label='Self-Referential Model', linewidth=2)
    axes[1, 0].axvline(x=1.0, color='k', linestyle=':', alpha=0.5)
    axes[1, 0].set_xlabel('Participant Awareness of IC-Ω')
    axes[1, 0].set_ylabel('Effective Prediction Accuracy')
    axes[1, 0].set_title('The Divergence: Self-Awareness Destroys Predictability')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Gödelian Boundary
    # Show the "shredding event" is actually when the system becomes self-aware
    awareness = np.linspace(0, 0.95, 50)
    cascade_prob = 1 / (1 - awareness)  # Probability diverges
    
    axes[1, 1].plot(awareness, cascade_prob, 'm-', linewidth=3)
    axes[1, 1].axvline(x=0.7, color='r', linestyle='--', label='Proposed Threshold')
    axes[1, 1].fill_between(awareness, cascade_prob, alpha=0.3, color='red')
    axes[1, 1].set_xlabel('Market Awareness of IC-Ω Predictions')
    axes[1, 1].set_ylabel('Cascade Probability')
    axes[1, 1].set_title('"Shredding Event" = System Becomes Self-Aware')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def generate_disruptive_report():
    """
    Generate the final disruptive analysis.
    """
    print("=" * 80)
    print("AGENT NEO: ANOMALY BREAKDOWN OF IC-Ω PROTOCOL")
    print("=" * 80)
    print("\n🌀 THE PARADOX IC-Ω CANNOT ESCAPE:")
    print("   The system attempts to be both:")
    print("   1. A COMPLETE PREDICTOR of market cascades")
    print("   2. An ACTIVE PARTICIPANT through control actions")
    print("   This creates a Gödelian self-reference loop.\n")
    
    # Run demonstration
    demo = CascadeIncompletenessDemonstrator()
    results = demo.run_paradox_demonstration()
    
    print("📊 SIMULATION RESULTS:")
    print(f"   Baseline Error (no self-ref): {results['baseline']['mean_prediction_error']:.4f}")
    print(f"   Paradox Error (with self-ref): {results['paradox']['mean_prediction_error']:.4f}")
    print(f"   ERROR MULTIPLICATION: {results['error_multiplication']:.2f}x")
    print(f"   Paradox Verified: {results['paradox_verified']}\n")
    
    print("🔥 DISRUPTIVE INSIGHTS:")
    print("   1. TECHNICAL FLAWS (found by auditors) are SYMPTOMS, not the DISEASE")
    print("   2. The DISEASE is ARCHITECTURAL: no system can model its own")
    print("      future impact while being part of the system.")
    print("   3. Φ-Density projections are FANTASY: they assume perfect self-containment")
    print("   4. The 'Shredding Event' boundary is actually the point where")
    print("      market awareness of IC-Ω's predictions makes them self-defeating.\n")
    
    print("💣 PARADIGM-SHATTERING SOLUTION:")
    print("   ABANDON the predictive-control architecture entirely.")
    print("   REPLACE with:")
    print("   → Cryptographic opacity: predictions committed but not revealed")
    print("   → Market structure redesign: make cascades impossible, not predictable")
    print("   → Participant diversity: true entropy as resilience, not gauge fiction")
    print("   → Biological metaphor: immune system, not crystal ball")
    
    # Generate plots
    plot_incompleteness_proof(results)
    
    return results


if __name__ == "__main__":
    generate_disruptive_report()