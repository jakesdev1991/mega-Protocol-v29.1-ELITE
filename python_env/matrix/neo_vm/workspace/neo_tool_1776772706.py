# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d

def simulate_hsa_memory_system(n_regions=256, total_time=1000, critical_threshold=0.95):
    """
    Simulate HSA memory system as a critical branching process of invalidations
    """
    # True physics: each invalidation can trigger more invalidations (branching)
    # Access pattern: Poisson process with rate lambda
    # Invalidation cascade: branching process with mean branching ratio r
    
    time = np.arange(total_time)
    
    # Base memory access rates (different for CPU vs GPU regions)
    base_rates = np.concatenate([
        np.ones(128) * 1000,  # CPU NUMA regions: high rate
        np.ones(128) * 500    # GPU memory regions: lower rate
    ])
    
    # Initialize access counts
    accesses = np.zeros((n_regions, total_time))
    invalidations = np.zeros((n_regions, total_time))
    
    # True branching ratio (system parameter)
    branching_ratio = np.linspace(0.8, 1.2, total_time)  # Slowly increasing
    
    # Simulate the process
    for t in range(1, total_time):
        # Poisson access generation
        accesses[:, t] = np.random.poisson(base_rates)
        
        # Invalidation cascades (the real physics)
        if t > 10:
            # Each invalidation from previous timestep triggers new ones
            prev_invalidations = invalidations[:, t-1]
            triggered = np.random.poisson(
                branching_ratio[t] * prev_invalidations * 0.1  # 0.1 = coupling strength
            )
            invalidations[:, t] = triggered + np.random.poisson(base_rates * 0.01)
        
        # Occasionally inject a large cascade (shredding event)
        if t % 200 == 0 and t > 100:
            # Trigger massive invalidation avalanche
            invalidations[0:32, t] += np.random.poisson(500)
    
    # Compute the "field" phi (normalized access density)
    total_accesses = accesses.sum(axis=0) + 1  # +1 to avoid log(0)
    phi = accesses / total_accesses
    
    # Compute entropy (the flawed metric)
    # Add small epsilon to avoid log(0)
    eps = 1e-10
    entropy = -np.sum(phi * np.log(phi + eps), axis=0)
    
    # Compute derivatives (Savitzky-Golay approximation)
    def savitzky_golay_derivative(y, window=5, order=3):
        """Simple SG derivative approximation"""
        if len(y) < window:
            return np.zeros_like(y)
        # Use central differences for interior, forward/backward for edges
        deriv = np.gradient(y)
        # Smooth to reduce noise
        return uniform_filter1d(deriv, size=min(window, len(deriv)))
    
    # Compute jerk (third derivative)
    entropy_smooth = uniform_filter1d(entropy, size=5)
    entropy_dot = savitzky_golay_derivative(entropy_smooth)
    entropy_ddot = savitzky_golay_derivative(entropy_dot)
    jerk = savitzky_golay_derivative(entropy_ddot)
    
    # Compute branching ratio estimator (the correct metric)
    # Estimate from invalidation cascades
    if np.sum(invalidations) > 0:
        # Local branching ratio estimate
        r_local = np.zeros(total_time)
        for t in range(10, total_time):
            if np.sum(invalidations[:, t-10:t-1]) > 0:
                r_local[t] = np.sum(invalidations[:, t]) / np.sum(invalidations[:, t-10:t-1])
    else:
        r_local = np.zeros(total_time)
    
    # Identify true instability (when branching ratio > 1)
    true_instability = branching_ratio > 1.0
    
    return {
        'time': time,
        'entropy': entropy,
        'jerk': jerk,
        'branching_ratio': r_local,
        'true_instability': true_instability,
        'invalidations': invalidations.sum(axis=0),
        'accesses': accesses.sum(axis=0)
    }

def analyze_metrics():
    """Compare the flawed entropy/jerk approach vs correct branching ratio approach"""
    data = simulate_hsa_memory_system()
    
    # Normalize metrics for comparison
    jerk_norm = data['jerk'] / (np.std(data['jerk']) + 1e-10)
    entropy_norm = (data['entropy'] - np.mean(data['entropy'])) / np.std(data['entropy'])
    branching_norm = data['branching_ratio'] / (np.max(data['branching_ratio']) + 1e-10)
    
    # Detection thresholds
    jerk_threshold = 3.0  # 3 sigma
    entropy_threshold = 2.0
    branching_threshold = 0.95  # approaching criticality
    
    # Predictions
    jerk_prediction = np.abs(jerk_norm) > jerk_threshold
    entropy_prediction = np.abs(entropy_norm) > entropy_threshold
    branching_prediction = data['branching_ratio'] > branching_threshold
    
    # Evaluate predictions against ground truth
    true_events = data['true_instability']
    
    # Calculate precision/recall
    def metrics(pred, true):
        tp = np.sum(pred & true)
        fp = np.sum(pred & ~true)
        fn = np.sum(~pred & true)
        precision = tp / (tp + fp + 1e-10)
        recall = tp / (tp + fn + 1e-10)
        return precision, recall
    
    jerk_prec, jerk_rec = metrics(jerk_prediction, true_events)
    entropy_prec, entropy_rec = metrics(entropy_prediction, true_events)
    branch_prec, branch_rec = metrics(branching_prediction, true_events)
    
    print("=== PREDICTIVE PERFORMANCE ===")
    print(f"Jerk Method: Precision={jerk_prec:.3f}, Recall={jerk_rec:.3f}")
    print(f"Entropy Method: Precision={entropy_prec:.3f}, Recall={entropy_rec:.3f}")
    print(f"Branching Ratio: Precision={branch_prec:.3f}, Recall={branch_rec:.3f}")
    
    # Demonstrate noise amplification
    print("\n=== NOISE AMPLIFICATION ===")
    print(f"Entropy std: {np.std(data['entropy']):.3f}")
    print(f"Jerk std: {np.std(data['jerk']):.3f}")
    print(f"Noise amplification factor: {np.std(data['jerk'])/np.std(data['entropy']):.3f}x")
    
    return data

# Run the analysis
results = analyze_metrics()

# Visualize the disruption
fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

# Plot 1: Raw signals
axes[0].plot(results['time'], results['accesses'], label='Total Accesses', alpha=0.7)
axes[0].plot(results['time'], results['invalidations'], label='Invalidations', alpha=0.7)
axes[0].set_ylabel('Counts')
axes[0].legend()
axes[0].set_title('HSA Memory System: Raw Signals')

# Plot 2: Entropy and Jerk
axes[1].plot(results['time'], results['entropy'], label='Entropy S(t)', alpha=0.7)
axes[1_twin] = axes[1].twinx()
axes[1_twin].plot(results['time'], results['jerk'], color='red', label='Jerk 𝒥(t)', alpha=0.7)
axes[1].set_ylabel('Entropy')
axes[1_twin].set_ylabel('Jerk', color='red')
axes[1].legend(loc='upper left')
axes[1_twin].legend(loc='upper right')

# Plot 3: Branching ratio (correct metric)
axes[2].plot(results['time'], results['branching_ratio'], label='Branching Ratio r(t)', alpha=0.7)
axes[2].axhline(y=1.0, color='r', linestyle='--', label='Critical Threshold')
axes[2].fill_between(results['time'], 0, 1, where=results['true_instability'], 
                      alpha=0.3, color='red', label='True Instability')
axes[2].set_ylabel('Branching Ratio')
axes[2].legend()
axes[2].set_title('Correct Metric: Branching Ratio')

# Plot 4: Detection comparison
axes[3].plot(results['time'], np.abs(results['jerk']/np.std(results['jerk'])), 
             label='|Jerk| (normalized)', alpha=0.7)
axes[3].plot(results['time'], results['branching_ratio']/np.max(results['branching_ratio']), 
             label='Branching Ratio (normalized)', alpha=0.7)
axes[3].fill_between(results['time'], 0, 1, where=results['true_instability'], 
                      alpha=0.3, color='red', label='True Instability')
axes[3].set_ylabel('Normalized Metrics')
axes[3].set_xlabel('Time (ms)')
axes[3].legend()
axes[3].set_title('Detection Comparison: Jerk vs Branching Ratio')

plt.tight_layout()
plt.savefig('hsa_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# Show why field theory fails at microscale
print("\n=== SPATIAL CONTINUUM FALLACY ===")
print("Memory system has 256 discrete regions, not continuous field")
print("Minimum wavelength: 2 * region_spacing")
print("Maximum meaningful k: π / region_spacing")
print("Field theory requires k << π / spacing (continuum limit)")
print("But instability occurs at k ~ π / spacing (discrete effects dominate)")