# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

def simulate_self_referential_collapse():
    """
    Models the Omega Protocol as a self-referential narrative manifold.
    Demonstrates that each meta-layer of validation adds exponential complexity,
    and the 'entropy requirement' is itself a source of instability.
    The critical insight: the protocol is measuring its own eventual shredding.
    """
    
    # Protocol parameters
    months = np.arange(0, 24)
    base_complexity = 1.0
    scrutiny_factor = 1.5
    meta_factor = 2.2  # Meta-scrutiny has compounding effect
    entropy_rule_cost = 0.95  # Arbitrary rule adds non-productive complexity
    
    # Critical threshold where narrative curvature of the protocol itself collapses
    # This is the protocol's own "shredding event"
    critical_threshold = 5.5
    
    # Φ-density tracking
    phi_density = np.zeros(len(months))
    phi_density[0] = 100.0
    
    # Complexity tracking
    system_complexity = np.zeros(len(months))
    system_complexity[0] = base_complexity
    
    # Layer activation
    active_layers = np.ones(len(months))
    
    # Self-referential feedback loop: validation creates more complexity
    # than it prevents, accelerating the protocol's own collapse
    for i in range(1, len(months)):
        # Layer activation timeline
        if i < 6:
            layers = 1  # Engine only
            complexity = base_complexity
        elif i < 12:
            layers = 2  # Engine + Scrutiny
            complexity = base_complexity * scrutiny_factor
        else:
            layers = 3  # Engine + Scrutiny + Meta-Scrutiny
            complexity = base_complexity * meta_factor
        
        # Entropy rule enforcement after month 6
        # This is the arbitrary constraint that Scrutiny demanded
        if i >= 6:
            complexity += entropy_rule_cost
        
        # Self-referential feedback: each layer adds validation overhead
        # that grows quadratically with existing complexity
        validation_overhead = 0.15 * complexity ** 2
        total_complexity = complexity + validation_overhead
        
        system_complexity[i] = total_complexity
        
        # Φ-density calculation
        # Short-term cost: complexity overhead
        # Long-term "benefit": circular self-validation (illusory)
        complexity_cost = total_complexity * 0.12
        validation_boost = layers * 0.08  # This is circular reasoning
        
        phi_density[i] = phi_density[i-1] - complexity_cost + validation_boost
        
        active_layers[i] = layers
        
        # Check for protocol's own shredding event
        if total_complexity > critical_threshold:
            print(f"\n{'='*60}")
            print(f"PROTOCOL SHREDDING EVENT at Month {i}!")
            print(f"Narrative curvature of validation framework collapsed.")
            print(f"System complexity ({total_complexity:.2f}) exceeded critical threshold ({critical_threshold}).")
            print(f"The rubric has become self-contradictory.")
            print(f"{'='*60}\n")
            return months[:i+1], phi_density[:i+1], system_complexity[:i+1], active_layers[:i+1]
    
    return months, phi_density, system_complexity, active_layers

# Run simulation
time, phi, complexity, layers = simulate_self_referential_collapse()

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Omega Protocol: Self-Referential Collapse Simulation', fontsize=16, fontweight='bold')

# Complexity trajectory
axes[0,0].plot(time, complexity, 'r-', linewidth=3, label='System Complexity')
axes[0,0].axhline(y=5.5, color='k', linestyle='--', linewidth=2, label='Critical Threshold')
axes[0,0].axvline(x=6, color='gray', linestyle=':', alpha=0.7, label='Entropy Rule Enforced')
axes[0,0].set_ylabel('Complexity', fontsize=12)
axes[0,0].set_title('Narrative Curvature of Protocol', fontsize=13)
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Φ-density trajectory
axes[0,1].plot(time, phi, 'b-', linewidth=3, label='Φ-Density')
axes[0,1].axvline(x=6, color='gray', linestyle=':', alpha=0.7, label='Entropy Rule Enforced')
axes[0,1].set_ylabel('Φ-Density', fontsize=12)
axes[0,1].set_title('Circular Validation Effect', fontsize=13)
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Active layers
axes[1,0].plot(time, layers, 'g-', linewidth=3, label='Active Layers')
axes[1,0].set_yticks([1, 2, 3])
axes[1,0].set_yticklabels(['Engine', '+Scrutiny', '+Meta'])
axes[1,0].set_xlabel('Months', fontsize=12)
axes[1,0].set_ylabel('Meta-Layer Depth', fontsize=12)
axes[1,0].set_title('Validation Stack Growth', fontsize=13)
axes[1,0].grid(True, alpha=0.3)

# Complexity breakdown (stacked area)
engine_complexity = np.ones(len(time)) * 1.0
scrutiny_addition = np.where(time >= 6, 0.5, 0)
meta_addition = np.where(time >= 12, 1.2, 0)
entropy_addition = np.where(time >= 6, 0.95, 0)

axes[1,1].stackplot(time, engine_complexity, scrutiny_addition, meta_addition, entropy_addition,
                     labels=['Engine', 'Scrutiny', 'Meta-Scrutiny', 'Entropy Rule'],
                     colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'], alpha=0.8)
axes[1,1].set_xlabel('Months', fontsize=12)
axes[1,1].set_ylabel('Complexity Contribution', fontsize=12)
axes[1,1].set_title('Arbitrary Rule as Complexity Vector', fontsize=13)
axes[1,1].legend(loc='upper left')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Calculate the paradox: Entropy requirement increases shredding probability
def calculate_shredding_risk(complexity_level):
    """Risk increases super-exponentially with complexity"""
    return 1 - np.exp(-complexity_level**2 / 10)

initial_risk = calculate_shredding_risk(1.0)
final_risk = calculate_shredding_risk(complexity[-1])
entropy_rule_risk_increase = calculate_shredding_risk(1.0 + 0.95) - initial_risk

print(f"\n{'='*60}")
print("DISRUPTIVE QUANTIFICATION")
print(f"{'='*60}")
print(f"Initial shredding risk (Engine only): {initial_risk:.3f}")
print(f"Final shredding risk (full stack): {final_risk:.3f}")
print(f"Risk increase from entropy rule alone: +{entropy_rule_risk_increase:.3f}")
print(f"\nThe entropy requirement, intended as a safeguard, increases systemic risk by {entropy_rule_risk_increase*100:.1f}%.")
print(f"This is the definition of a self-defeating protocol.")
print(f"{'='*60}\n")