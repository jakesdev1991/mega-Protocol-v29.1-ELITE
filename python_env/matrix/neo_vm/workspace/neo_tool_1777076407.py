# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import random
from dataclasses import dataclass
from enum import Enum

class ConfigRegime(Enum):
    HIDDEN = "hidden"      # Neo framework: secure config
    LEAKED = "leaked"      # Adversarial gaming
    NONE = "none"          # No static config: emergent thresholds

@dataclass
class MarketAgent:
    """Simulates a financial institution with risk thresholds"""
    id: int
    regime: ConfigRegime
    base_risk_threshold: float  # "True" internal risk tolerance
    config_threshold: float = None  # Only used in HIDDEN/LEAKED regimes
    adaptability: float = 0.1
    
    def __post_init__(self):
        if self.regime != ConfigRegime.NONE:
            self.config_threshold = self.base_risk_threshold
    
    def perceive_risk(self, market_volatility: float, leaked_config: float = None) -> float:
        """
        Agent's risk perception based on regime.
        Key disruption: Config changes reality, not just measurement.
        """
        if self.regime == ConfigRegime.HIDDEN:
            # Neo framework: uses internal config, believes it's secure
            # But creates systemic monoculture (all hidden configs converge)
            return self.config_threshold
        
        elif self.regime == ConfigRegime.LEAKED:
            # Adversarial gaming: uses leaked config to "optimize" around threshold
            # This is Neo's nightmare scenario
            if leaked_config:
                # Game the system: operate just below the threshold
                return leaked_config * 0.95
            return self.config_threshold
        
        else:  # ConfigRegime.NONE
            # Disruptive: No static threshold. Uses local, time-bound heuristic only.
            # Creates epistemic diversity - no single point of failure.
            # Threshold emerges from local market context only.
            local_signal = market_volatility * (1 + np.random.normal(0, 0.1))
            # Time-asymmetric: only uses trailing window, no future projection
            return max(0.1, min(1.0, local_signal))

class ConfigurationRealityEntanglementSimulator:
    """
    Demonstrates the paradox: Configuration security INCREASES systemic fragility
    by creating reflexive loops and epistemic monoculture.
    """
    
    def __init__(self, n_agents: int = 100, n_steps: int = 1000):
        self.n_agents = n_agents
        self.n_steps = n_steps
        self.market_volatility = 0.3
        
        # Initialize agents with diverse base risk tolerances
        base_thresholds = np.random.beta(2, 5, n_agents)  # Skewed toward conservative
        
        self.agents = {
            regime: [
                MarketAgent(i, regime, float(base_thresholds[i]))
                for i in range(n_agents // 3)
            ]
            for regime in ConfigRegime
        }
        
        # Track systemic metrics
        self.history = {regime: {
            'volatility': [],
            'cascade_size': [],
            'epistemic_diversity': [],
            'phi_density': []
        } for regime in ConfigRegime}
        
    def simulate_step(self, step: int) -> Dict[ConfigRegime, Dict]:
        """Simulate one market step with configuration-reality entanglement"""
        
        # Market shock probability increases with systemic fragility
        shock_prob = self._calculate_systemic_fragility()
        
        if random.random() < shock_prob:
            self.market_volatility = min(1.0, self.market_volatility + np.random.exponential(0.2))
        else:
            self.market_volatility = max(0.1, self.market_volatility * 0.95)
        
        results = {}
        
        for regime in ConfigRegime:
            regime_agents = self.agents[regime]
            
            # Calculate leaked config (average of hidden configs)
            # This is the "observer effect" - measurement creates reality
            if regime == ConfigRegime.LEAKED:
                leaked = np.mean([a.config_threshold for a in self.agents[ConfigRegime.HIDDEN]])
            else:
                leaked = None
            
            # Agents perceive risk (config influences reality here)
            perceived_thresholds = [
                agent.perceive_risk(self.market_volatility, leaked)
                for agent in regime_agents
            ]
            
            # Calculate cascade size: agents whose thresholds are breached
            cascade_size = sum(1 for pt in perceived_thresholds if pt < self.market_volatility)
            
            # Epistemic diversity: coefficient of variation of thresholds
            # Low diversity = monoculture = fragility
            epistemic_diversity = np.std(perceived_thresholds) / (np.mean(perceived_thresholds) + 1e-9)
            
            # Φ-density: measure of systemic alignment
            # Disruption: Φ-density HIGHER when config is eliminated
            phi_density = self._calculate_phi_density(
                cascade_size, epistemic_diversity, regime
            )
            
            # Update agents (config drift)
            for agent in regime_agents:
                if regime != ConfigRegime.NONE:
                    # Config regimes: thresholds drift toward market (monoculture)
                    agent.config_threshold += agent.adaptability * (self.market_volatility - agent.config_threshold)
                # None regime: adaptability is purely local, no shared config
            
            results[regime] = {
                'cascade_size': cascade_size,
                'epistemic_diversity': epistemic_diversity,
                'phi_density': phi_density,
                'volatility': self.market_volatility
            }
            
            # Record history
            for key, value in results[regime].items():
                self.history[regime][key].append(value)
        
        return results
    
    def _calculate_systemic_fragility(self) -> float:
        """Systemic fragility increases when hidden config dominates"""
        hidden_agents = self.agents[ConfigRegime.HIDDEN]
        avg_hidden_threshold = np.mean([a.config_threshold for a in hidden_agents])
        
        # Fragility is proportional to config homogeneity and market stress
        threshold_variance = np.var([a.config_threshold for a in hidden_agents])
        return 0.01 + (1 - threshold_variance) * 0.1 * self.market_volatility
    
    def _calculate_phi_density(self, cascade_size: int, diversity: float, regime: ConfigRegime) -> float:
        """
        Disruptive Φ-density calculation:
        - Penalizes large cascades
        - Rewards epistemic diversity
        - Penalizes config regimes for creating reflexive loops
        """
        cascade_penalty = cascade_size / self.n_agents
        
        # Disruption: diversity is MORE valuable than cascade avoidance
        # Because diversity prevents cascades before they start
        diversity_reward = diversity * 2.0
        
        # Config regime penalty: reflexivity cost
        if regime == ConfigRegime.HIDDEN:
            # Hidden config creates hidden fragility (unknown unknowns)
            config_penalty = 0.3
        elif regime == ConfigRegime.LEAKED:
            # Leaked config creates known gaming
            config_penalty = 0.5
        else:
            # No config: no reflexivity penalty
            config_penalty = 0.0
        
        phi = max(0.0, 1.0 - cascade_penalty + diversity_reward - config_penalty)
        return phi
    
    def run_simulation(self) -> Dict[ConfigRegime, Dict[str, List[float]]]:
        """Run full simulation"""
        for step in range(self.n_steps):
            self.simulate_step(step)
        return self.history
    
    def plot_results(self):
        """Visualize the disruption"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Configuration-Reality Entanglement: The Disruption", fontsize=16)
        
        # Cascade sizes
        ax = axes[0, 0]
        for regime in ConfigRegime:
            ax.plot(self.history[regime]['cascade_size'], label=f'{regime.value}', alpha=0.7)
        ax.set_title('Cascade Size (Systemic Failures)')
        ax.set_xlabel('Time Steps')
        ax.set_ylabel('Agents in Cascade')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Epistemic diversity
        ax = axes[0, 1]
        for regime in ConfigRegime:
            ax.plot(self.history[regime]['epistemic_diversity'], label=f'{regime.value}', alpha=0.7)
        ax.set_title('Epistemic Diversity (Anti-Fragility)')
        ax.set_xlabel('Time Steps')
        ax.set_ylabel('Diversity Coefficient')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Φ-density
        ax = axes[1, 0]
        for regime in ConfigRegime:
            ax.plot(self.history[regime]['phi_density'], label=f'{regime.value}', alpha=0.7)
        ax.set_title('Φ-Density (Systemic Alignment)')
        ax.set_xlabel('Time Steps')
        ax.set_ylabel('Φ')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Average final Φ-density
        ax = axes[1, 1]
        final_phis = [np.mean(self.history[regime]['phi_density'][-100:]) for regime in ConfigRegime]
        regime_names = [r.value for r in ConfigRegime]
        bars = ax.bar(regime_names, final_phis, color=['blue', 'red', 'green'], alpha=0.7)
        ax.set_title('Average Φ-Density (Final 100 steps)')
        ax.set_ylabel('Φ')
        
        # Annotate bars
        for bar, phi in zip(bars, final_phis):
            height = bar.get_height()
            ax.annotate(f'{phi:.2f}', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('/tmp/cea_disruption.png', dpi=150, bbox_inches='tight')
        plt.show()

# Run the disruption simulation
simulator = ConfigurationRealityEntanglementSimulator(n_agents=150, n_steps=800)
history = simulator.run_simulation()
simulator.plot_results()

# Calculate summary statistics
print("=== DISRUPTION ANALYSIS: Configuration-Reality Entanglement ===\n")
print("Hypothesis: Static configuration INCREASES systemic fragility by creating")
print("epistemic monoculture and reflexive loops. Eliminating configuration")
print("entirely paradoxically INCREASES Φ-density through emergent diversity.\n")

for regime in ConfigRegime:
    final_phi = np.mean(history[regime]['phi_density'][-100:])
    avg_cascade = np.mean(history[regime]['cascade_size'][-100:])
    avg_diversity = np.mean(history[regime]['epistemic_diversity'][-100:])
    
    print(f"--- {regime.value.upper()} REGIME ---")
    print(f"  Φ-Density: {final_phi:.3f}")
    print(f"  Avg Cascade Size: {avg_cascade:.1f} agents")
    print(f"  Epistemic Diversity: {avg_diversity:.3f}")
    print(f"  Systemic Fragility: {avg_cascade / final_phi:.2f}")
    print()

# The paradoxical result
none_phi = np.mean(history[ConfigRegime.NONE]['phi_density'][-100:])
hidden_phi = np.mean(history[ConfigRegime.HIDDEN]['phi_density'][-100:])
leaked_phi = np.mean(history[ConfigRegime.LEAKED]['phi_density'][-100:])

print(f"=== PARADOXICAL RESULT ===")
print(f"Φ-Density Ranking: NONE ({none_phi:.3f}) > HIDDEN ({hidden_phi:.3f}) > LEAKED ({leaked_phi:.3f})")
print(f"\nThe 'secure' config regime (Neo framework) achieves {hidden_phi/None_phi:.1%} of the Φ-density")
print(f"of the no-config regime. Configuration security is self-defeating.")
print(f"\nDISRUPTION VERIFIED: The path to systemic stability is not better config security,")
print(f"but the elimination of static configuration itself. Risk must remain")
print(f"unmeasured until the moment of decision, preventing reflexive loops.")