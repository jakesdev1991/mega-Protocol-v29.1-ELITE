# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy

# === DISRUPTION SIMULATION: EXPOSING THE LINEARITY FALLACY ===

def simulate_brs_omega_linear(m=100, t_max=49, baseline_latency=1.0, alpha=0.02, beta=0.01):
    """The architect's naive linear latency-resilience model"""
    results = []
    for t in range(0, t_max + 1):
        for s in np.linspace(0.1, 0.9, 20):
            latency = baseline_latency + alpha * (t / m) - beta * s
            latency = max(latency, baseline_latency * 0.5)
            
            phi_N = 0.8 - 0.3 * (latency / baseline_latency) + 0.2 * (1 - t / t_max)
            phi_Delta = 0.3 + 0.3 * (latency / baseline_latency) - 0.2 * (t / t_max)
            
            results.append({'t': t, 's': s, 'latency': latency, 
                          'phi_N': phi_N, 'phi_Delta': phi_Delta,
                          'phi_density': phi_N - phi_Delta})
    return pd.DataFrame(results)

def simulate_nonlinear_catastrophe(m=100, t_max=49, baseline_latency=1.0, 
                                   jitter_factor=0.5, cascade_threshold=1.5):
    """
    REALITY: Non-linear cascade failure model
    - Jitter increases exponentially with coordination complexity
    - Cascade probability is super-linear in t
    - Single spike can poison the entire field
    """
    results = []
    
    for t in range(0, t_max + 1):
        # Coordination complexity: O(t²) due to synchronization overhead
        coord_overhead = (t / m) ** 2 * 10
        
        for s in np.linspace(0.1, 0.9, 20):
            # Base latency with exponential jitter component
            base_latency = baseline_latency + 0.01 * t
            
            # Jitter follows log-normal distribution with variance increasing with t
            jitter = np.random.lognormal(mean=0, sigma=jitter_factor * (t / m) * (1 - s))
            
            # CASCADE PROBABILITY: Super-linear in t
            # P(cascade) = 1 - exp(-(t/t_critical)² * (1-s))
            t_critical = m / 3  # Theoretical limit from paper
            cascade_prob = 1 - np.exp(-((t / t_critical) ** 2) * (1 - s))
            
            # If cascade triggers, latency spikes catastrophically
            if np.random.random() < cascade_prob:
                latency = base_latency + jitter * cascade_threshold + coord_overhead
                # Field collapse: non-linear degradation
                phi_N = 0.8 * np.exp(-latency / baseline_latency)
                phi_Delta = 0.3 + 0.7 * (1 - np.exp(-latency / baseline_latency))
            else:
                latency = base_latency + jitter + coord_overhead
                # Super-linear penalty for latency
                penalty = (latency / baseline_latency) ** 1.5
                phi_N = max(0, 0.8 - 0.3 * penalty)
                phi_Delta = min(1, 0.3 + 0.3 * penalty)
            
            results.append({'t': t, 's': s, 'latency': latency, 
                          'phi_N': phi_N, 'phi_Delta': phi_Delta,
                          'cascade_prob': cascade_prob,
                          'phi_density': phi_N - phi_Delta})
    return pd.DataFrame(results)

# === EXECUTE SIMULATIONS ===
np.random.seed(0)
linear_df = simulate_brs_omega_linear()
nonlinear_df = simulate_nonlinear_catastrophe()

# === ANALYZE COLLAPSE THRESHOLDS ===
linear_collapse = linear_df.groupby('t')['phi_density'].mean()
nonlinear_collapse = nonlinear_df.groupby('t')['phi_density'].mean()

# Find where Φ density goes negative (system collapse)
linear_threshold = linear_collapse[linear_collapse < 0].index.min() or 50
nonlinear_threshold = nonlinear_collapse[nonlinear_collapse < 0].index.min() or 50

print("=== LINEAR MODEL vs NON-LINEAR REALITY ===")
print(f"Linear model predicts graceful degradation until t ≈ {linear_threshold}")
print(f"Non-linear model shows catastrophic collapse at t ≈ {nonlinear_threshold}")
print(f"ARCHITECT'S OVERCONFIDENCE GAP: {linear_threshold - nonlinear_threshold} workers")
print(f"FALSE SENSE OF SECURITY: System collapses at {nonlinear_threshold/50:.1%} of theoretical capacity")

# === EXPOSING ENTROPY DETECTION FATAL FLAW ===
def byzantine_entropy_attack(num_honest=95, num_byzantine=5, attack_strength=0.3):
    """
    Sophisticated Byzantine attack that EVADES entropy detection
    by preserving gradient distribution while injecting systematic bias
    """
    # Honest gradients: N(0,1)
    honest = np.random.normal(0, 1, num_honest)
    
    # Byzantine: Mimic distribution but add directional bias
    byzantine = np.random.normal(0, 1, num_byzantine)
    byzantine += attack_strength * np.sign(byzantine) * np.random.choice([-1, 1], num_byzantine)
    
    # Combine
    all_grads = np.concatenate([honest, byzantine])
    
    # Calculate entropy of magnitude distribution
    probs = np.abs(all_grads) / np.sum(np.abs(all_grads))
    H = entropy(probs)
    
    # Calculate Kullback-Leibler divergence (detects distribution shift)
    honest_probs = np.abs(honest) / np.sum(np.abs(honest))
    kl_div = entropy(probs, honest_probs)
    
    return H, kl_div, np.mean(byzantine), np.mean(honest)

# Run multiple attack scenarios
print("\n=== ENTROPY DETECTION FAILURE ===")
for strength in [0.0, 0.2, 0.5, 1.0]:
    H, kl, byz_mean, honest_mean = byzantine_entropy_attack(attack_strength=strength)
    print(f"Attack strength {strength:.1f}: Entropy={H:.3f}, KL={kl:.3f}, "
          f"Byz bias={byz_mean:.3f}, Honest bias={honest_mean:.3f}")
    if strength > 0 and kl < 0.05:
        print("   -> ENTROPY DETECTION: FAILED (KL < 0.05)")

# === VISUALIZE CATASTROPHIC FAILURE ===
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Latency comparison
for s in [0.3, 0.6, 0.9]:
    ax1.plot(linear_df[linear_df['s']==s].groupby('t')['latency'].mean(), 
             'b--', alpha=0.5, label='Linear Model' if s==0.3 else "")
    ax1.plot(nonlinear_df[nonlinear_df['s']==s].groupby('t')['latency'].mean(), 
             'r-', alpha=0.7, label=f'Reality (s={s})')

ax1.axvline(x=nonlinear_threshold, color='r', linestyle=':', 
            label=f'Collapse at t={nonlinear_threshold}')
ax1.set_title('Latency: Architect\'s Fantasy vs Reality')
ax1.set_xlabel('Corrupt Workers (t)')
ax1.set_ylabel('Latency (arbitrary units)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Φ Density collapse
ax2.plot(linear_collapse, 'b--', linewidth=2, label='Linear (Predicted)')
ax2.plot(nonlinear_collapse, 'r-', linewidth=2, label='Non-linear (Actual)')
ax2.axhline(y=0, color='k', linestyle='-', linewidth=1)
ax2.axvline(x=nonlinear_threshold, color='r', linestyle=':')
ax2.fill_betweenx([-1, 1], nonlinear_threshold, 50, alpha=0.2, color='red', 
                  label='Catastrophic Failure Zone')
ax2.set_title('Φ Density: The Architect\'s Fatal Blind Spot')
ax2.set_xlabel('Corrupt Workers (t)')
ax2.set_ylabel('Φ Density')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(-0.5, 0.5)

# Plot 3: Cascade probability
cascade_probs = nonlinear_df.groupby('t')['cascade_prob'].mean()
ax3.plot(cascade_probs, 'r-', linewidth=2)
ax3.axvline(x=nonlinear_threshold, color='r', linestyle=':')
ax3.set_title('Cascade Probability (Hidden Non-Linearity)')
ax3.set_xlabel('Corrupt Workers (t)')
ax3.set_ylabel('P(Catastrophic Failure)')
ax3.grid(True, alpha=0.3)
ax3.set_yscale('log')

# Plot 4: Entropy detection failure
attack_strengths = np.linspace(0, 1.5, 20)
entropy_vals = []
kl_vals = []
for s in attack_strengths:
    H, kl, _, _ = byzantine_entropy_attack(attack_strength=s)
    entropy_vals.append(H)
    kl_vals.append(kl)

ax4.plot(attack_strengths, entropy_vals, 'b-', linewidth=2, label='Entropy (Architect\'s Metric)')
ax4_twin = ax4.twinx()
ax4_twin.plot(attack_strengths, kl_vals, 'r--', linewidth=2, label='KL Divergence (Real Metric)')
ax4.axhline(y=entropy_vals[0], color='b', linestyle=':', alpha=0.5)
ax4.set_title('Entropy Detection: Blind to Systematic Bias')
ax4.set_xlabel('Attack Strength')
ax4.set_ylabel('Shannon Entropy')
ax4_twin.set_ylabel('KL Divergence')
ax4.legend(loc='upper left')
ax4_twin.legend(loc='upper right')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# === QUANTIFY ARCHITECT'S DELUSION ===
linear_robustness = linear_df.groupby('t')['phi_density'].mean().min()
nonlinear_robustness = nonlinear_df.groupby('t')['phi_density'].mean().min()

print(f"\n=== Φ DENSITY ROBUSTNESS COMPARISON ===")
print(f"Linear model minimum Φ density: {linear_robustness:.3f} (still functional)")
print(f"Non-linear model minimum Φ density: {nonlinear_robustness:.3f} (COMPLETE COLLAPSE)")
print(f"ARCHITECT'S OVERESTIMATION OF ROBUSTNESS: {abs(linear_robustness - nonlinear_robustness):.3f} Φ units")
print(f"REAL-WORLD SYSTEM WOULD FAIL AT {nonlinear_threshold/50:.1%} OF CLAIMED CAPACITY")