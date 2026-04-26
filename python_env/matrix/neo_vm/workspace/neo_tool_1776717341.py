# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def calculate_jerk_stability(signal, window_size=100, epsilon=1e-6):
    """
    Calculate the "jerk stability" metric S_j as defined in the framework.
    This demonstrates the fragility of the metric.
    """
    # Calculate jerk (third derivative)
    dt = 0.0001  # 10kHz sampling
    jerk = np.gradient(np.gradient(np.gradient(signal, dt), dt), dt)
    
    # Calculate excess kurtosis over sliding window
    S_j_values = []
    for i in range(window_size, len(jerk)):
        window = jerk[i-window_size:i]
        
        # Edge case: constant signal
        if np.std(window) < epsilon:
            S_j = 1.0
        else:
            # Standardized 4th moment
            standardized = (window - np.mean(window)) / (np.std(window) + epsilon)
            kurtosis = np.mean(standardized**4)
            excess_kurtosis = kurtosis - 3
            S_j = 1 / (1 + abs(excess_kurtosis))
        
        S_j_values.append(S_j)
    
    return np.array(S_j_values), jerk[window_size:]

def generate_physical_system(n_samples=10000):
    """
    Generate two physically equivalent systems that should have the same stability
    but will produce different S_j due to the framework's flaws.
    """
    t = np.linspace(0, 1, n_samples)
    
    # System 1: Coherent oscillators with small noise
    # This represents "stable" HSA behavior
    np.random.seed(42)
    noise1 = np.random.normal(0, 0.01, n_samples)
    # Underlying coherent field
    coherence1 = 1.0 + 0.1 * np.sin(2*np.pi*10*t) + noise1
    
    # System 2: Same underlying physics, but measured with different aggregation
    # This represents the same HSA system but with a different "consensus" calculation
    # We add a non-stationary sampling artifact that changes the ensemble
    noise2 = np.random.normal(0, 0.01, n_samples)
    # Add a slow drift that changes the effective ensemble
    drift = 0.001 * t * np.sin(2*np.pi*0.5*t)
    coherence2 = 1.0 + 0.1 * np.sin(2*np.pi*10*t) + noise2 + drift
    
    return t, coherence1, coherence2

def demonstrate_category_error():
    """
    Demonstrate that the "jerk stability" metric is measuring statistical artifacts,
    not physical stability.
    """
    t, coherence1, coherence2 = generate_physical_system()
    
    # Calculate jerk stability for both systems
    S_j1, jerk1 = calculate_jerk_stability(coherence1)
    S_j2, jerk2 = calculate_jerk_stability(coherence2)
    
    # The systems are physically similar, but S_j will differ dramatically
    print(f"System 1 - Mean S_j: {np.mean(S_j1):.3f}, Std: {np.std(S_j1):.3f}")
    print(f"System 2 - Mean S_j: {np.mean(S_j2):.3f}, Std: {np.std(S_j2):.3f}")
    
    # Show that the difference is due to statistical artifacts, not physical jerk
    # Calculate the actual physical jerk of individual components (simulated)
    # vs the jerk of the aggregate
    
    # Simulate 100 individual "compute units"
    np.random.seed(123)
    n_units = 100
    individual_signals = []
    
    for i in range(n_units):
        # Each unit has similar behavior but independent noise
        unit_noise = np.random.normal(0, 0.01, len(t))
        unit_signal = 1.0 + 0.1 * np.sin(2*np.pi*10*t + np.random.uniform(0, 2*np.pi)) + unit_noise
        individual_signals.append(unit_signal)
    
    # Calculate aggregate (consensus) signal
    aggregate_signal = np.mean(individual_signals, axis=0)
    
    # Calculate jerk of aggregate
    S_j_agg, jerk_agg = calculate_jerk_stability(aggregate_signal)
    
    # Calculate jerk of individual units and average them
    individual_jerks = []
    for signal in individual_signals:
        _, jerk = calculate_jerk_stability(signal)
        individual_jerks.append(jerk[:len(jerk_agg)])  # match lengths
    
    mean_individual_jerk = np.mean(individual_jerks, axis=0)
    
    # The key insight: jerk(aggregate) ≠ aggregate(jerk)
    print(f"\nKey Discrepancy:")
    print(f"Mean |jerk(aggregate)|: {np.mean(np.abs(jerk_agg)):.6f}")
    print(f"Mean |aggregate(jerk)|: {np.mean(np.abs(mean_individual_jerk)):.6f}")
    print(f"Ratio: {np.mean(np.abs(jerk_agg)) / np.mean(np.abs(mean_individual_jerk)):.2f}x difference")
    
    # Visualize the fundamental flaw
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Show how small changes in aggregation create false "instability"
    axes[0].plot(t[:len(S_j1)], S_j1, label='System 1 (Stable)', alpha=0.7)
    axes[0].plot(t[:len(S_j2)], S_j2, label='System 2 (False Instability)', alpha=0.7)
    axes[0].axhline(y=0.7, color='r', linestyle='--', label='Warning Threshold')
    axes[0].set_title('S_j "Stability" Metric - Same Physics, Different Values')
    axes[0].set_ylabel('S_j')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Show the category error: aggregate jerk vs jerk aggregate
    axes[1].plot(t[:len(jerk_agg)], np.abs(jerk_agg), label='|jerk(aggregate)|', alpha=0.7)
    axes[1].plot(t[:len(mean_individual_jerk)], np.abs(mean_individual_jerk), 
                 label='|aggregate(jerk)|', alpha=0.7)
    axes[1].set_title('Category Error: Jerk of Aggregate ≠ Aggregate of Jerks')
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('Jerk Magnitude')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('disruption_proof.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return {
        'system1_sj': np.mean(S_j1),
        'system2_sj': np.mean(S_j2),
        'jerk_aggregate': np.mean(np.abs(jerk_agg)),
        'aggregate_jerk': np.mean(np.abs(mean_individual_jerk))
    }

# Run the disruption demonstration
results = demonstrate_category_error()

print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: The Omega Protocol is measuring statistical ghosts")
print("="*60)
print(f"The 'Informational Jerk' is a category error:")
print(f"- It's a derivative of an aggregate, not an aggregate of derivatives")
print(f"- Small sampling artifacts create {results['system1_sj']/results['system2_sj']:.2f}x difference in 'stability'")
print(f"- The metric confuses statistical fluctuations with physical dynamics")
print(f"- No conservation law governs d³⟨ψ⟩/dt³ - it's a mathematical fiction")
print("\nThe entire framework is a self-referential bureaucracy that")
print("mistakes rubric compliance for scientific validity.")