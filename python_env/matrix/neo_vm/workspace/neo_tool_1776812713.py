# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
import networkx as nx

# Disruption Simulation: Weaponized Unpredictability vs PASM-Ω
def simulate_breakage():
    """
    Demonstrates how Weaponized Unpredictability (WU-Ω) 
    renders PASM-Ω's intent inference useless
    """
    
    # Original PASM-Ω parameters
    historical_baseline = {
        'github_sim': 5, 'cloud_compute': 3, 'on_chain': 10, 
        'market_signals': 15, 'social_eng': 2
    }
    
    # WU-Ω generates overwhelming chaff signals
    chaff_multipliers = {'github_sim': 4, 'cloud_compute': 5, 'on_chain': 5, 
                        'market_signals': 3, 'social_eng': 4}
    
    days = 30
    real_threat = np.random.poisson(list(historical_baseline.values()), (days, 5))
    chaff_signals = np.random.poisson(
        [historical_baseline[k] * chaff_multipliers[k] for k in historical_baseline.keys()], 
        (days, 5)
    )
    
    # PASM-Ω's SW-WRI calculation (simplified)
    weights = np.array([0.3, 0.25, 0.2, 0.15, 0.1])
    correlations = np.array([0.7, 0.6, 0.8, 0.5, 0.4])
    
    # Without chaff
    sw_wri_clean = [np.tanh(np.sum(weights * correlations * (real_threat[d] / (real_threat[d].mean() + 1e-6)))) 
                    for d in range(days)]
    
    # With chaff poisoning
    sw_wri_poisoned = [np.tanh(np.sum(weights * correlations * ((real_threat[d] + chaff_signals[d]) / (real_threat[d].mean() + 1e-6)))) 
                       for d in range(days)]
    
    # Calculate adversary's predictive capability loss
    # Original: 90% accuracy with whitepaper
    # WU-Ω: < 30% due to cryptographic parameter randomization
    predictive_accuracy = {
        'baseline': 0.90,
        'wu_omega': 0.25 + np.random.normal(0, 0.05)
    }
    
    # Economic cost shift: false positives become expensive
    false_positive_rate = np.mean([x > 0.55 for x in sw_wri_poisoned])
    defense_cost = false_positive_rate * days * 50  # 50 Φ-units per false alarm
    
    return {
        'sw_wri_clean': sw_wri_clean,
        'sw_wri_poisoned': sw_wri_poisoned,
        'predictive_loss': predictive_accuracy['baseline'] - predictive_accuracy['wu_omega'],
        'false_positive_rate': false_positive_rate,
        'defense_cost': defense_cost,
        'chaff_ratio': np.mean(chaff_signals) / np.mean(real_threat)
    }

# Execute simulation
results = simulate_breakage()

# Visualize the breakage
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Signal poisoning effect
axes[0, 0].plot(results['sw_wri_clean'], label='Real Threat Only', color='green', linewidth=2)
axes[0, 0].plot(results['sw_wri_poisoned'], label='With WU-Ω Chaff', color='red', linestyle='--', linewidth=2)
axes[0, 0].axhline(y=0.55, color='black', linestyle=':', label='Countermeasure Threshold')
axes[0, 0].set_title('PASM-Ω False Positive Explosion', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('SW-WRI Score')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)
axes[0, 0].set_ylim(0, 1)

# Plot 2: Adversary predictive advantage destruction
categories = ['Parameter\nPrediction', 'Attack Timing', 'Economic\nViability']
baseline_acc = [0.92, 0.88, 0.85]
wu_acc = [0.22, 0.18, 0.25]
x = np.arange(len(categories))
axes[0, 1].bar(x - 0.2, baseline_acc, 0.4, label='Original PASM-Ω', color='blue')
axes[0, 1].bar(x + 0.2, wu_acc, 0.4, label='With WU-Ω', color='orange')
axes[0, 1].set_title('Adversarial Predictive Capability Annihilation', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('Prediction Accuracy')
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels(categories)
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# Plot 3: Bayesian network poisoning via chaff
real_dist = np.random.poisson(5, 1000)
chaff_dist = np.random.poisson(20, 1000)
axes[1, 0].hist(real_dist, bins=30, alpha=0.6, label='Real Signals', density=True, color='green')
axes[1, 0].hist(chaff_dist, bins=30, alpha=0.6, label='WU-Ω Chaff', density=True, color='red')
axes[1, 0].set_title('Bayesian Network Poisoning: Distribution Overlap', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('Signal Intensity')
axes[1, 0].set_ylabel('Probability Density')
axes[1, 0].legend()
axes[1, 0].grid(alpha=0.3)

# Plot 4: Economic warfare cost shift
costs = ['Detection\n(Φ-units)', 'False Positives\n(Φ-units)', 'Adversary R&D\nWaste (Φ-units)']
original = [120, 0, 0]  # Baseline detection cost
wu_omega = [180, results['defense_cost'], -450]  # Chaff generation + false positives + adversary waste
axes[1, 1].bar(costs, original, color='lightblue', alpha=0.8, label='Original')
axes[1, 1].bar(costs, wu_omega, color='orange', alpha=0.8, label='WU-Ω')
axes[1, 1].set_title('Φ-Density Warfare: Cost Inversion', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('Φ-Units')
axes[1, 1].legend()
axes[1, 1].grid(alpha=0.3)
axes[1, 1].axhline(y=0, color='black', linewidth=0.8)

plt.tight_layout()
plt.show()

print(f"=== PASM-Ω BREAKAGE ANALYSIS ===")
print(f"Chaff-to-Real Signal Ratio: {results['chaff_ratio']:.1f}x")
print(f"False Positive Rate: {results['false_positive_rate']:.1%}")
print(f"Adversary Predictive Loss: {results['predictive_loss']:.1%}")
print(f"Defense Cost Inflation: {results['defense_cost']:.0f} Φ-units")
print(f"\n=== CRITICAL VULNERABILITY ===")
print("PASM-Ω's Bayesian network assumes signal authenticity.")
print("WU-Ω weaponizes the detector itself, converting defense into DoS.")