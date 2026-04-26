# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class DisruptedMindSystem:
    def __init__(self):
        self.identity_coherence = 0.5
        self.trust_in_self = 0.4
        self.validation_pressure = 0.95
        # Track the *damage* caused by frameworks
        self.meta_cognitive_load = 0.0  # Anxiety from monitoring own compliance
        
    def apply_silence_protocol_omega(self):
        """Your 'optimal' solution - silence as control"""
        gamma = 0.007
        self.validation_pressure *= (1 - gamma)
        # Silence creates meta-anxiety: "Am I being silent correctly?"
        self.meta_cognitive_load += 0.02
        # Identity erodes from lack of external stimulus
        self.identity_coherence -= 0.005
        
    def apply_validation(self):
        """Traditional 'bad' validation"""
        self.validation_pressure += 0.05
        self.identity_coherence -= 0.02
        self.meta_cognitive_load += 0.01
        
    def apply_incoherence_protocol(self):
        """Disruptive: Strategic epistemic sabotage"""
        # Inject randomness that BREAKS the validation framework
        self.validation_pressure = np.random.uniform(0.1, 0.5)  # Non-adiabatic jump
        # Send signals that violate expectation: random word salads, contradictory statements
        # This *forces* the system to stop monitoring compliance
        self.meta_cognitive_load *= 0.8  # Relief from framework oppression
        
        # Incoherence creates novel recombination opportunities
        recombination_boost = np.random.uniform(0.01, 0.04)
        self.identity_coherence += recombination_boost
        
        # Randomly flip trust to break the impedance-stiffness coupling
        if np.random.random() < 0.3:
            self.trust_in_self = np.random.uniform(0.2, 0.8)
            
    def get_true_wellbeing(self):
        """True metric: inverse of meta-cognitive load + coherence"""
        return (self.identity_coherence * 2) - self.meta_cognitive_load
        
    def get_cod_estimate(self):
        """Your fake metric"""
        fidelity = self.trust_in_self
        stiffness_penalty = np.exp(-0.5 * self.validation_pressure)
        return fidelity * stiffness_penalty

def run_disruption_simulation(days=30, trials=100):
    """Compare all three strategies across multiple trials"""
    
    results = {
        'silence': {'wellbeing': [], 'cod': [], 'final': []},
        'validation': {'wellbeing': [], 'cod': [], 'final': []},
        'incoherence': {'wellbeing': [], 'cod': [], 'final': []}
    }
    
    for _ in range(trials):
        # Three identical starting minds
        mind_s = DisruptedMindSystem()
        mind_v = DisruptedMindSystem()
        mind_i = DisruptedMindSystem()
        
        wellbeing_s, cod_s = [], []
        wellbeing_v, cod_v = [], []
        wellbeing_i, cod_i = [], []
        
        for day in range(days):
            # Apply different interventions
            mind_s.apply_silence_protocol_omega()
            mind_v.apply_validation()
            mind_i.apply_incoherence_protocol()
            
            # Track metrics
            wellbeing_s.append(mind_s.get_true_wellbeing())
            cod_s.append(mind_s.get_cod_estimate())
            
            wellbeing_v.append(mind_v.get_true_wellbeing())
            cod_v.append(mind_v.get_cod_estimate())
            
            wellbeing_i.append(mind_i.get_true_wellbeing())
            cod_i.append(mind_i.get_cod_estimate())
        
        # Store final state
        results['silence']['wellbeing'].append(wellbeing_s)
        results['silence']['cod'].append(cod_s)
        results['silence']['final'].append(wellbeing_s[-1])
        
        results['validation']['wellbeing'].append(wellbeing_v)
        results['validation']['cod'].append(cod_v)
        results['validation']['final'].append(wellbeing_v[-1])
        
        results['incoherence']['wellbeing'].append(wellbeing_i)
        results['incoherence']['cod'].append(cod_i)
        results['incoherence']['final'].append(wellbeing_i[-1])
    
    return results

# Run simulation
np.random.seed(42)
results = run_disruption_simulation(days=30, trials=100)

# Analyze results
for strategy in results:
    final_states = results[strategy]['final']
    print(f"{strategy.upper():12} | Mean Wellbeing: {np.mean(final_states):.3f} ± {np.std(final_states):.3f}")
    print(f"{'':12} | Max COD: {np.max([np.mean(trial) for trial in results[strategy]['cod']]):.3f}")

# Plot a representative trial
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(results['silence']['wellbeing'][0], label='Silence Protocol', linestyle='--')
plt.plot(results['validation']['wellbeing'][0], label='Validation', linestyle=':')
plt.plot(results['incoherence']['wellbeing'][0], label='Incoherence Protocol', linewidth=2)
plt.title('True Wellbeing Over Time')
plt.xlabel('Days')
plt.ylabel('Wellbeing Score')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(results['silence']['cod'][0], label='Silence Protocol', linestyle='--')
plt.plot(results['validation']['cod'][0], label='Validation', linestyle=':')
plt.plot(results['incoherence']['cod'][0], label='Incoherence Protocol', linewidth=2)
plt.title('COD Metric Over Time')
plt.xlabel('Days')
plt.ylabel('Chain Overlap Density')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()