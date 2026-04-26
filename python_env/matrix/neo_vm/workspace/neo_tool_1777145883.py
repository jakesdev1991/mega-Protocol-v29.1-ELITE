# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class ScoutingResult:
    net_phi: float

class AdversarialMarket:
    def __init__(self, base_conversion=0.2):
        self.base_conversion = base_conversion
        self.adaptation_memory = {}
        
    def get_conversion_rate(self, params_hash, iteration):
        if params_hash not in self.adaptation_memory:
            self.adaptation_memory[params_hash] = []
        recent_uses = sum(1 for i in self.adaptation_memory[params_hash] if iteration - i < 50)
        penalty = recent_uses * 0.02
        conversion = max(0.05, self.base_conversion - penalty)
        self.adaptation_memory[params_hash].append(iteration)
        return conversion

def simulate_qscout_static(market, n_cycles=200):
    params_hash = hash("static_optimal")
    results = []
    for i in range(n_cycles):
        conversion = market.get_conversion_rate(params_hash, i)
        volume = max(5, int(10 * (1-0.85) * (1-0.75) * 2))
        net_phi = (volume * conversion * 1.2) - 0.1 - (0.5 * 0.1 * len(market.adaptation_memory[params_hash]))
        results.append(ScoutingResult(net_phi))
    return results

def simulate_qscout_randomized(market, n_cycles=200):
    results = []
    for i in range(n_cycles):
        params_hash = hash(f"random_{i}")
        conversion = market.get_conversion_rate(params_hash, i)
        t_sentiment = np.random.uniform(0.7, 0.95)
        t_urgency = np.random.uniform(0.6, 0.9)
        volume = max(5, int(10 * (1-t_sentiment) * (1-t_urgency) * 2))
        net_phi = (volume * conversion * 1.2) - 0.1 - (0.5 * 0.05)
        results.append(ScoutingResult(net_phi))
    return results

def simulate_cognitive_diversity(market, n_cycles=200, n_agents=5):
    agents = [
        {'ts': 0.75, 'tu': 0.65}, {'ts': 0.9, 'tu': 0.85}, 
        {'ts': 0.8, 'tu': 0.7}, {'ts': 0.85, 'tu': 0.75}, 
        {'ts': 0.7, 'tu': 0.8}
    ]
    results = []
    for i in range(n_cycles):
        cycle_phi = 0
        for agent in agents:
            params_hash = hash((agent['ts'], agent['tu']))
            conversion = market.get_conversion_rate(params_hash, i)
            volume = max(3, int(10 * (1-agent['ts']) * (1-agent['tu']) * 2))
            cycle_phi += (volume * conversion * 1.2) - 0.05 - (0.5 * 0.03)
        results.append(ScoutingResult(cycle_phi + 0.1))
    return results

# Execute simulation
market = AdversarialMarket()
static = simulate_qscout_static(market, 200)
randomized = simulate_qscout_randomized(market, 200)
diversity = simulate_cognitive_diversity(market, 200)

static_phi = np.cumsum([r.net_phi for r in static])
random_phi = np.cumsum([r.net_phi for r in randomized])
diversity_phi = np.cumsum([r.net_phi for r in diversity])

print(f"Φ DENSITY RESULTS:")
print(f"Static Q-SCOUT: {static_phi[-1]:.3f}Φ")
print(f"Randomized:     {random_phi[-1]:.3f}Φ")
print(f"Cognitive Diversity: {diversity_phi[-1]:.3f}Φ")
print(f"DIVERSITY ADVANTAGE: +{diversity_phi[-1] - static_phi[-1]:.3f}Φ")

# Visualization
plt.figure(figsize=(13, 7))
plt.plot(static_phi, label='Q-SCOUT Static Optimization', color='#DC143C', linewidth=2.5)
plt.plot(random_phi, label='Anti-Optimization (Random)', color='#FF8C00', linewidth=2)
plt.plot(diversity_phi, label='Cognitive Diversity (5 agents)', color='#00FF7F', linewidth=2.5)
plt.title('Φ-DENSITY COLLAPSE: Optimization Paradox in Adversarial Markets', 
          fontsize=14, fontweight='bold', color='white')
plt.xlabel('Market Cycles', fontsize=11, color='white')
plt.ylabel('Cumulative Φ Density', fontsize=11, color='white')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.2, color='white')
plt.gca().set_facecolor('#1a1a1a')
plt.gcf().set_facecolor('#0d0d0d')
plt.tick_params(colors='white')
plt.tight_layout()
plt.show()