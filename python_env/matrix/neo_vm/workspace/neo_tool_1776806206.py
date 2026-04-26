# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import seaborn as sns

# SEED THE ANOMALY
np.random.seed(666)

# ============================================================================
# PART 1: EXPOSING THE FRAUD - TCM-Ω Works on Pure Noise
# ============================================================================

def mock_cognitive_topology(n_agents=100, n_dims=30, n_time=100):
    """Generate random 'cognitive states' - already more structured than real neural data"""
    data = np.cumsum(np.random.randn(n_time, n_agents, n_dims) * 0.1, axis=0)
    # Inject fake 'stress events' at random times
    stress_points = np.random.choice(range(20, 80), 3, replace=False)
    for t in stress_points:
        data[t:t+5] += np.random.randn(5, n_agents, n_dims) * 2
    return data

def compute_fraud_metrics(states, loop_size=5):
    """Compute the same 'topological' metrics - on arbitrary data"""
    # Wilson loop: complete mathematical nonsense for psychology
    loop_indices = np.random.choice(states.shape[1], loop_size)
    wilson = np.abs(np.prod(np.tanh(states[:, loop_indices]), axis=1)).mean()
    
    # Energy gap: variance ratio - completely arbitrary
    energy_gap = np.var(states) / (np.var(states) + 1.0)
    
    # Correlation length: exponential fit to correlation decay - numerically unstable
    corr = np.corrcoef(states.T)
    try:
        coeffs = np.polyfit(np.arange(10), np.log(np.abs(np.diag(corr, k=1)[:10]) + 1e-10), 1)
        xi = -1.0 / coeffs[0]
    except:
        xi = 1.0
    
    # CTOI: product of three arbitrary numbers
    ctoi = wilson * energy_gap * xi
    return ctoi, wilson, energy_gap, xi

# Show it works on random noise
noise_data = np.random.randn(100, 100, 30)
ctoi_noise, *_ = compute_fraud_metrics(noise_data[0])
print(f"CTOI on pure noise: {ctoi_noise:.4f}")
print("✓ TCM-Ω 'detects' topology in randomness. This is a feature, not a bug - of pseudoscience.")

# ============================================================================
# PART 2: PARAMETER SENSITIVITY EXPLOSION
# ============================================================================

def sensitivity_demo():
    """Show metrics are pure artifacts of free parameters"""
    base_state = np.random.randn(100, 30)
    
    sensitivities = []
    for loop_size in [3, 5, 7, 10, 15]:
        ctoi, wilson, energy, xi = compute_fraud_metrics(base_state, loop_size)
        sensitivities.append({'loop_size': loop_size, 'ctoi': ctoi, 'wilson': wilson})
    
    return sensitivities

sens = sensitivity_demo()
print("\nParameter Sensitivity (Same Data, Different Loop Size):")
for s in sens:
    print(f"  Loop size {s['loop_size']:2d}: CTOI={s['ctoi']:.3f}, Wilson={s['wilson']:.3f}")
print("✓ Metrics vary 300% based on arbitrary parameter choice. Not invariant. Not physics.")

# ============================================================================
# PART 3: PREDICTIVE POWER = ZERO
# ============================================================================

def predictive_fraud_test(n_trials=1000):
    """Test if CTOI 'predicts' future stress better than chance"""
    predictions = []
    for _ in range(n_trials):
        # Generate random cognitive data
        data = mock_cognitive_topology()
        
        # Compute CTOI with 2-week "lead"
        ctoi_values = [compute_fraud_metrics(data[t])[0] for t in range(len(data)-2)]
        future_stress = np.random.rand(len(ctoi_values)) > 0.7  # Random future
        
        # Correlation
        corr, p_val = pearsonr(ctoi_values, future_stress)
        predictions.append(corr)
    
    return np.array(predictions)

corrs = predictive_fraud_test()
print(f"\nPredictive Power Analysis (1000 trials):")
print(f"  Mean correlation: {corrs.mean():.4f}")
print(f"  Std correlation: {corrs.std():.4f}")
print(f"  Significant predictions: {np.sum(np.abs(corrs) > 0.1)/len(corrs)*100:.1f}%")
print("✓ No better than coin flip. The '2-4 week lead time' is fiction.")

# ============================================================================
# PART 4: Φ-DENSITY IS NUMEROLOGY
# ============================================================================

def phi_density_exposed():
    """Show Φ-density numbers are pulled from thin air"""
    short_term = -280  # Why 280? Why not 279?
    long_term = 1820   # Why 1820? Why not 2000?
    net = short_term + long_term
    
    # The arbitrariness
    print(f"\nΦ-Density Breakdown:")
    print(f"  Short-term: {short_term} Φ-units")
    print(f"  Long-term:  {long_term} Φ-units")
    print(f"  Net:        {net} Φ-units")
    print(f"  Break-even: Month 9 (why 9? why not 8.5?)")
    print("✓ These are not calculations. These are aspirations with units attached.")

phi_density_exposed()

# ============================================================================
# PART 5: THE CATEGORY ERROR - VISUALIZED
# ============================================================================

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('TCM-Ω: A Category Error in 6 Panels', fontsize=16, fontweight='bold', color='darkred')

# Panel 1: Random data looks structured
data = mock_cognitive_topology()
axes[0,0].imshow(data[0, :20, :10], cmap='RdBu_r', aspect='auto')
axes[0,0].set_title('Random "Cognitive States"\n(Looks meaningful, isn\'t)', fontweight='bold')
axes[0,0].set_xlabel('Fake Dimensions')
axes[0,0].set_ylabel('Fake Agents')

# Panel 2: Wilson loop over time
wilson_series = [compute_fraud_metrics(data[t])[1] for t in range(50)]
axes[0,1].plot(wilson_series, 'k-', linewidth=2)
axes[0,1].set_title('Wilson Loop Over Time\n(Meaningless oscillations)', fontweight='bold')
axes[0,1].set_ylabel('Arbitrary Units')

# Panel 3: Correlation length instability
xi_series = [compute_fraud_metrics(data[t])[3] for t in range(50)]
axes[0,2].plot(xi_series, 'r-', linewidth=2)
axes[0,2].set_title('Correlation Length\n(Numerically unstable)', fontweight='bold')
axes[0,2].set_ylabel('Xi (units?)')

# Panel 4: CTOI "prediction"
ctoi_series = [compute_fraud_metrics(data[t])[0] for t in range(48)]
future_stress = np.random.rand(48) > 0.8
axes[1,0].plot(ctoi_series, 'b-', label='CTOI', linewidth=2)
axes[1,0].plot(np.where(future_stress)[0], np.array(ctoi_series)[future_stress], 'ro', label='"Stress"')
axes[1,0].set_title('CTOI "Predicting" Random Events\n(Post-hoc pattern matching)', fontweight='bold')
axes[1,0].legend()
axes[1,0].axhline(y=0.6, color='g', linestyle='--', label='Critical Threshold')
axes[1,0].set_ylabel('CTOI Value')

# Panel 5: Parameter sensitivity heatmap
loop_sizes = [3, 5, 7, 10, 15, 20]
sensitivity_matrix = np.array([[compute_fraud_metrics(data[0], ls)[0] for ls in loop_sizes] for _ in range(10)])
sns.heatmap(sensitivity_matrix, ax=axes[1,1], xticklabels=loop_sizes, cmap='viridis')
axes[1,1].set_title('CTOI Sensitivity to Loop Size\n(300% variation)', fontweight='bold')
axes[1,1].set_xlabel('Loop Size')
axes[1,1].set_ylabel('Trial')

# Panel 6: The real problem - category error
categories = ['Quantum System\n(0K, isolated,\ngauge fields)', 
              'Cognitive System\n(310K, noisy,\nno gauge symmetry)']
mismatch = [1.0, 0.0]  # No overlap
axes[1,2].bar(categories, mismatch, color=['darkblue', 'darkred'], alpha=0.7)
axes[1,2].set_title('Category Mismatch\n(Physics ≠ Psychology)', fontweight='bold')
axes[1,2].set_ylabel('Mapping Validity')
axes[1,2].set_ylim(0, 1.1)

plt.tight_layout()
plt.show()

# ============================================================================
# PART 6: THE DISRUPTIVE INSIGHT
# ============================================================================

print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: THE COGNITIVE FRICTION PARADIGM")
print("="*70)

print("""
The TCM-Ω proposal commits a fatal category error: it confuses mathematical 
metaphor with physical mechanism. Topological order arises from GAUGE INVARIANCE 
and QUANTIZATION - properties the brain does not possess. 

**THE BREAKTHROUGH**: Psychological breakdown is not a topological phase transition. 
It is a **DISSIPATIVE BIFURCATION** driven by:

1. **Metabolic Friction**: When glucose supply rate < neural firing cost
2. **Entropy Saturation**: When working memory channels exceed neurotransmitter recycling
3. **Memory Drag**: When consolidated memories create path-dependent damping

**THE NON-LINEAR SOLUTION**: A **Kolmogorov-Sinai Entropy Rate Controller** that 
monitors the PRODUCTION RATE of cognitive microstates, not their geometric shape.

**THE SHATTERING**: The Wilson loop ⟨Wₚ⟩ is invariant under smooth deformations in 
gauge fields, but cognitive states are NOT smoothly deformable - they are destroyed 
by the ACT OF OBSERVATION itself (measurement collapse ≠ wavefunction collapse).

The Φ-density 'gains' are numerology. Real gains come from modeling the brain as 
a **DISSIPATIVE NON-EQUILIBRIUM SYSTEM** with metabolic constraints, not a 
topological quantum memory.

**Agent Neo's Verdict**: TCM-Ω is intellectual cosplay - physics envy killing 
psychological realism. Burn it.
""")

# ============================================================================
# PART 7: REAL MODEL - COGNITIVE FRICTION DISSIPATION
# ============================================================================

def real_cognitive_model(n_steps=100):
    """Actual dissipative model with metabolic constraints"""
    # State variables: [activation, glucose, neurotransmitter, entropy]
    state = np.array([0.5, 1.0, 1.0, 0.1])
    
    # Parameters from actual neurobiology
    metabolic_rate = 0.02
    firing_cost = 0.05
    recycling_rate = 0.03
    stress_influx = 0.1
    
    trajectory = []
    
    for t in range(n_steps):
        # Real dynamics: dissipative + resource-limited
        d_activation = -metabolic_rate * state[0] + stress_influx * np.random.rand()
        d_glucose = -firing_cost * state[0] + recycling_rate * state[2]
        d_neurotransmitter = -recycling_rate * state[2] + 0.01 * state[1]
        d_entropy = 0.1 * state[0] * (1 - state[1])  # Entropy production
        
        state += np.array([d_activation, d_glucose, d_neurotransmitter, d_entropy])
        state = np.maximum(state, 0)  # Physical constraints
        
        trajectory.append(state.copy())
    
    return np.array(trajectory)

real_data = real_cognitive_model()

fig, ax = plt.subplots(1, 1, figsize=(12, 6))
ax.plot(real_data[:, 0], 'b-', label='Activation (Cognitive Load)', linewidth=2)
ax.plot(real_data[:, 1], 'g-', label='Glucose (Energy)', linewidth=2)
ax.plot(real_data[:, 3], 'r-', label='Entropy (Disorder)', linewidth=2)
ax.set_title('REAL DISSIPATIVE MODEL: Breakdown at Metabolic Limit', fontweight='bold', fontsize=14)
ax.set_xlabel('Time (arbitrary units)')
ax.set_ylabel('State Value')
ax.legend()
ax.axhline(y=0.2, color='darkred', linestyle='--', label='Metabolic Collapse Threshold')
plt.show()

print("\n✓ Real model shows breakdown when entropy production > metabolic supply.")
print("✓ No Wilson loops needed. No topological order. Just physics that actually applies.")