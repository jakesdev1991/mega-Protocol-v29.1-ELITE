# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import powerlaw

def simulate_collapse_paradox(n_agents=500, surveillance_granularity=0.1):
    """
    Demonstrates: As surveillance precision increases, 
    genuine security behavior collapses into adversarial superposition.
    """
    # Initial state: agents have natural friction tolerance thresholds
    true_tolerance = np.random.normal(0.5, 0.2, n_agents)
    
    # Surveillance creates "observed friction" that agents must now manage
    observed_load = np.zeros(n_agents)
    
    # Three regimes of measurement
    regimes = {
        'none': {'surveillance': 0.0, 'label': 'No CTMS'},
        'moderate': {'surveillance': 0.5, 'label': 'Moderate CTMS'},
        'extreme': {'surveillance': 1.0, 'label': 'High-Fidelity CTMS'}
    }
    
    results = {}
    
    for key, params in regimes.items():
        surveillance_intensity = params['surveillance']
        violation_timeline = []
        decoy_creation = []
        
        for t in range(100):
            # Surveillance anxiety: agents allocate cognitive budget to evasion
            evasion_cost = surveillance_intensity * 0.3 * (1 + t/50)
            
            # True cognitive load from tools (decreases naturally over time)
            actual_load = 0.7 * np.exp(-t/30)
            
            # Effective load: real + manufactured
            effective_load = actual_load + evasion_cost
            
            # Behavior bifurcation:
            # - Low surveillance: agents adapt naturally (fewer violations)
            # - High surveillance: agents create decoys while pursuing critical violations
            if surveillance_intensity < 0.3:
                # Natural adaptation regime
                violation_prob = np.clip(effective_load - true_tolerance, 0, 1) * 0.02
                decoy_rate = 0.01
            else:
                # Adversarial superposition regime
                # Decoy creation explodes (to mislead CTMS)
                decoy_rate = 0.1 * surveillance_intensity * (effective_load  true_tolerance).mean()
                # Critical violations become *more* severe but *less* frequent
                violation_prob = np.clip(effective_load - true_tolerance, 0, 1) * 0.005 * (1 + surveillance_intensity)
            
            violations = np.random.binomial(1, violation_prob, n_agents).sum()
            decoys = np.random.poisson(decoy_rate * n_agents)
            
            violation_timeline.append(violations)
            decoy_creation.append(decoys)
        
        results[key] = {
            'violations': np.array(violation_timeline),
            'decoys': np.array(decoy_creation),
            'cumulative_violations': np.cumsum(violation_timeline),
            'label': params['label']
        }
    
    # Plot the paradox
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Violation rates
    for key, data in results.items():
        axes[0,0].plot(data['violations'], label=data['label'], linewidth=2)
    axes[0,0].set_title('Weekly Critical Violations')
    axes[0,0].set_ylabel('Violations')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Decoy creation
    for key, data in results.items():
        axes[0,1].plot(data['decoys'], label=data['label'], linewidth=2)
    axes[0,1].set_title('Weekly Decoy Spreadsheets Created')
    axes[0,1].set_ylabel('Decoys')
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Cumulative violations
    for key, data in results.items():
        axes[1,0].plot(data['cumulative_violations'], label=data['label'], linewidth=2)
    axes[1,0].set_title('Cumulative Critical Violations')
    axes[1,0].set_xlabel('Weeks')
    axes[1,0].set_ylabel('Total Violations')
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Violation severity distribution (power-law tail)
    for key, data in results.items():
        if data['violations'].sum() > 0:
            # Simulate severity scores (exponential of violation count)
            severity = np.exp(np.random.gamma(2, 1, int(data['violations'].sum())))
            axes[1,1].hist(severity, bins=30, alpha=0.5, label=data['label'], density=True)
    axes[1,1].set_title('Violation Severity Distribution')
    axes[1,1].set_xlabel('Severity Score')
    axes[1,1].set_ylabel('Density')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return results

# Execute the collapse simulation
paradox_data = simulate_collapse_paradox()

# Print the counterintuitive outcome
for key, data in paradox_data.items():
    total_violations = data['cumulative_violations'][-1]
    total_decoys = data['decoys'].sum()
    print(f"{data['label']}: {total_violations:.0f} critical violations, {total_decoys:.0f} decoy spreadsheets")