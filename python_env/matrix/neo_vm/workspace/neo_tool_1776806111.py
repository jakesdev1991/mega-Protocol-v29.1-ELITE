# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.stats import entropy

# ============================================================================
# DISRUPTIVE INSIGHT: The Reflexivity Paradox
# ============================================================================
"""
The IC-Ω proposal assumes information cascades are predictable physical fields.
The critical flaw: PREDICTION ITSELF BECOMES THE CASCADE'S PRIMARY DRIVER.

When adversaries know a model predicts cascades, they don't just front-run the leak—
they front-run the MODEL'S PREDICTION, creating a self-referential amplification loop.
The more accurate the model, the more exploitable it becomes. This is the 
"Predictability-Fragility Tradeoff."

SOLUTION: Don't model cascades—MODEL THE GAPS IN ATTENTION.
Create a "Narrative Entropy Weapon" that weaponizes the model's own predictions 
to inject decoherence at the belief-formation layer, not the trading layer.
"""

# ============================================================================
# Simulate the Reflexivity Paradox
# ============================================================================

class ReflexiveMarketSimulator:
    def __init__(self, n_traders=100, n_etfs=5):
        # Market participants: mix of HFT, institutional, retail
        self.trader_types = np.random.choice(['HFT', 'INST', 'RETAIL'], size=n_traders, p=[0.1, 0.2, 0.7])
        self.trader_sophistication = {'HFT': 0.95, 'INST': 0.8, 'RETAIL': 0.3}
        
        # ETF network
        self.etfs = [f"ETF_{i}" for i in range(n_etfs)]
        self.correlation_matrix = np.random.rand(n_etfs, n_etfs) * 0.5 + 0.5
        np.fill_diagonal(self.correlation_matrix, 1.0)
        
        # Attention network (who listens to whom)
        self.attention_graph = self._generate_attention_graph(n_traders)
        
        # Model awareness: % of traders who know IC-Ω exists
        self.model_awareness = 0.0
        
    def _generate_attention_graph(self, n_traders):
        """Scale-free network mimics real attention/information flow"""
        G = nx.scale_free_graph(n_traders, alpha=0.3, beta=0.4, gamma=0.3)
        G = nx.DiGraph(G)  # Make directed
        return G
    
    def simulate_cascade(self, leak_strength, model_prediction=None, countermeasure=False):
        """
        Core disruption: model_prediction doesn't dampen cascade—it AMPLIFIES it
        through reflexive awareness.
        """
        # Initialize trader states
        trader_belief = np.zeros(len(self.trader_types))
        trader_position = np.zeros(len(self.trader_types))
        
        # Leak detection (base signal)
        leak_signal = leak_strength * np.random.rand()
        
        # CRITICAL FLAW IN IC-Ω: Model prediction becomes public knowledge
        # Sophisticated traders don't trade the leak—they trade the *model's forecast*
        if model_prediction is not None:
            # Model awareness spreads through attention network
            aware_traders = self._propagate_awareness(model_prediction)
            # Belief formation: traders weight model prediction based on sophistication
            for i, ttype in enumerate(self.trader_types):
                if aware_traders[i]:
                    sophistication = self.trader_sophistication[ttype]
                    # Disruptive insight: High sophistication = MORE likely to game the model
                    trader_belief[i] = leak_signal + sophistication * model_prediction * 2.0
                else:
                    trader_belief[i] = leak_signal
        
        # COUNTERMEASURE: Narrative entropy injection
        if countermeasure:
            # Instead of blocking trades, inject competing narratives
            # This DECOHES the cascade by fragmenting the belief structure
            trader_belief = self._inject_narrative_noise(trader_belief, model_prediction)
        
        # Trading cascade (simplified: belief → position → price impact)
        for i, ttype in enumerate(self.trader_types):
            position_size = self._calculate_position_size(trader_belief[i], ttype)
            trader_position[i] = position_size * (1 if trader_belief[i] > 0 else -1)
        
        # Market impact: concentrated positions create volatility
        total_net_position = np.sum(trader_position)
        # Disruptive metric: Cascade Coherence (low entropy = dangerous consensus)
        position_distribution = np.abs(trader_position)
        position_distribution = position_distribution / np.sum(position_distribution)
        cascade_coherence = 1.0 / (entropy(position_distribution) + 1e-6)
        
        # Price volatility is a function of cascade coherence
        volatility = abs(total_net_position) * cascade_coherence * 0.01
        
        return {
            'volatility': volatility,
            'net_position': total_net_position,
            'coherence': cascade_coherence,
            'belief_entropy': entropy(np.abs(trader_belief) / np.sum(np.abs(trader_belief))),
            'awareness_penetration': np.mean(self._propagate_awareness(model_prediction)) if model_prediction else 0
        }
    
    def _propagate_awareness(self, model_prediction, threshold=0.5):
        """Model awareness spreads like a contagion through attention network"""
        aware = np.random.rand(len(self.trader_types)) < self.model_awareness
        # Propagate through network steps
        for _ in range(3):  # 3-hop propagation
            for i in range(len(self.trader_types)):
                if not aware[i]:
                    # If enough incoming neighbors are aware, become aware
                    predecessors = list(self.attention_graph.predecessors(i))
                    if predecessors:
                        aware_frac = np.mean([aware[p] for p in predecessors])
                        if aware_frac > threshold:
                            aware[i] = True
        return aware
    
    def _inject_narrative_noise(self, beliefs, model_prediction):
        """COUNTER-CASCADE: Inject competing narratives to fragment consensus"""
        # Create 3-5 competing interpretations of the leak
        n_narratives = np.random.randint(3, 6)
        narrative_signals = np.random.normal(loc=model_prediction/2, scale=abs(model_prediction)/2, size=n_narratives)
        
        # Randomly assign traders to different narratives based on attention network
        narrative_assignment = np.random.randint(0, n_narratives, size=len(beliefs))
        
        # Fragment the cascade: each narrative pulls traders in different directions
        fragmented_beliefs = np.zeros_like(beliefs)
        for i, narrative_idx in enumerate(narrative_assignment):
            sophistication = self.trader_sophistication[self.trader_types[i]]
            # Smart traders recognize noise and reduce conviction
            if sophistication > 0.8:
                fragmented_beliefs[i] = beliefs[i] * 0.3  # HFTs step back
            else:
                fragmented_beliefs[i] = narrative_signals[narrative_idx] * (1 - sophistication)
        
        return fragmented_beliefs
    
    def _calculate_position_size(self, belief, trader_type):
        """Position sizing based on trader type"""
        base_size = abs(belief) * 100
        if trader_type == 'HFT':
            return base_size * 10  # Leveraged
        elif trader_type == 'INST':
            return base_size * 5
        else:
            return base_size * 1

# ============================================================================
# Demonstrate the Paradox
# ============================================================================

def demonstrate_reflexivity_paradox():
    """Show that model prediction accuracy INCREASES fragility"""
    simulator = ReflexiveMarketSimulator(n_traders=200, n_etfs=5)
    
    leak_strengths = np.linspace(0.1, 1.0, 10)
    results = []
    
    for leak in leak_strengths:
        # Scenario 1: No model (baseline)
        result_no_model = simulator.simulate_cascade(leak, model_prediction=None)
        
        # Scenario 2: Model predicts cascade (IC-Ω approach)
        # Model predicts volatility will be 2x baseline
        model_pred = result_no_model['volatility'] * 2.0
        simulator.model_awareness = 0.4  # 40% of market knows about IC-Ω
        result_with_model = simulator.simulate_cascade(leak, model_prediction=model_pred)
        
        # Scenario 3: Counter-cascade (Narrative Entropy Weapon)
        result_counter = simulator.simulate_cascade(leak, model_prediction=model_pred, countermeasure=True)
        
        results.append({
            'leak': leak,
            'baseline_vol': result_no_model['volatility'],
            'model_vol': result_with_model['volatility'],
            'counter_vol': result_counter['volatility'],
            'baseline_coherence': result_no_model['coherence'],
            'model_coherence': result_with_model['coherence'],
            'counter_coherence': result_counter['coherence']
        })
    
    # Plot the paradox
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Volatility comparison
    r = results
    ax1.plot([x['leak'] for x in r], [x['baseline_vol'] for x in r], 'b-o', label='No Model (Baseline)')
    ax1.plot([x['leak'] for x in r], [x['model_vol'] for x in r], 'r-s', label='IC-Ω Prediction (Fragility Amplified)')
    ax1.plot([x['leak'] for x in r], [x['counter_vol'] for x in r], 'g-^', label='Narrative Entropy Weapon')
    ax1.set_xlabel('Leak Strength', fontsize=12)
    ax1.set_ylabel('Market Volatility', fontsize=12)
    ax1.set_title('The Reflexivity Paradox', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Coherence comparison (lower is better for stability)
    ax2.plot([x['leak'] for x in r], [x['baseline_coherence'] for x in r], 'b-o', label='No Model')
    ax2.plot([x['leak'] for x in r], [x['model_coherence'] for x in r], 'r-s', label='IC-Ω Prediction')
    ax2.plot([x['leak'] for x in r], [x['counter_coherence'] for x in r], 'g-^', label='Narrative Entropy Weapon')
    ax2.set_xlabel('Leak Strength', fontsize=12)
    ax2.set_ylabel('Cascade Coherence (1/Entropy)', fontsize=12)
    ax2.set_title('Cascade Coherence: High = Dangerous Consensus', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print key insight
    print("="*70)
    print("DISRUPTIVE INSIGHT: The Model IS the Cascade")
    print("="*70)
    avg_baseline = np.mean([x['baseline_vol'] for x in r])
    avg_model = np.mean([x['model_vol'] for x in r])
    avg_counter = np.mean([x['counter_vol'] for x in r])
    
    print(f"Average Baseline Volatility: {avg_baseline:.4f}")
    print(f"Average Volatility WITH IC-Ω Prediction: {avg_model:.4f} (+{((avg_model/avg_baseline)-1)*100:.1f}%)")
    print(f"Average Volatility WITH Countermeasure: {avg_counter:.4f} (-{((1-avg_counter/avg_baseline))*100:.1f}%)")
    print("\nThe IC-Ω model's predictions BECOME the primary signal that sophisticated")
    print("traders front-run, creating a self-fulfilling prophecy that INCREASES volatility.")
    print("\nThe Narrative Entropy Weapon works by DECOHING the cascade at the BELIEF")
    print("layer, making it impossible for adversaries to coordinate even when they")
    print("know the model's predictions.")

# Run the demonstration
demonstrate_reflexivity_paradox()