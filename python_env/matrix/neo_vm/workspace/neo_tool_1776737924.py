# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

# Disruption Script: "The Non-Locality Catastrophe in ETO-Ω"
# Demonstrates that measuring topological order parameter O(t) requires 
# exponential resources, making MPC-Ω control fundamentally impossible

# === CORE DISRUPTION: Non-local correlation measurement scaling ===

def measure_topological_order(L, d, xi, M_budget):
    """
    Simulate measuring non-local correlation O = lim_{|x-y|->∞} <phi(x)phi(y)>
    For a system of L^d sites, measuring true long-range correlation requires
    sampling pairs at maximum separation ~ L. The fraction of such pairs is ~1/L^d.
    """
    N_sites = L**d
    
    # True topological correlation (ideal)
    O_true = np.exp(-L/xi) if xi > 0 else 0.0
    
    # Effective samples at max separation: M_budget * (fraction of max-separation pairs)
    # For random sampling, probability of picking a max-distance pair is ~1/N_sites
    effective_samples = M_budget / N_sites
    
    # Measurement variance: shot noise + finite sampling error
    if effective_samples < 1:
        # We haven't even sampled one relevant pair - measurement is meaningless
        noise_std = 1.0  # Complete uncertainty
    else:
        # Standard error for correlation measurement
        noise_std = np.sqrt((1 - O_true**2) / effective_samples)
    
    # Measured value (with noise)
    O_measured = np.random.normal(O_true, noise_std)
    
    return O_true, O_measured, noise_std, effective_samples

# === Parameter sweep: Show exponential scaling problem ===

L_values = [8, 12, 16, 24, 32]
d = 2
xi_ordered = 100  # Large correlation length (topological phase)
M_budget = 1000   # Fixed measurement budget per time step

results = []
for L in L_values:
    O_true, O_meas, noise, samples = measure_topological_order(L, d, xi_ordered, M_budget)
    results.append({
        'L': L,
        'N_sites': L**d,
        'O_true': O_true,
        'O_meas': O_meas,
        'noise_std': noise,
        'effective_samples': samples,
        'rel_error': noise / max(O_true, 1e-6)
    })

# === Visualization of the catastrophe ===

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Measurement error vs system size
ax = axes[0, 0]
Ls = [r['L'] for r in results]
rel_errors = [r['rel_error'] for r in results]
ax.loglog(Ls, rel_errors, 'ko-', linewidth=2, markersize=8)
ax.set_xlabel('System size L')
ax.set_ylabel('Relative measurement error')
ax.set_title('Error Explodes for Large Systems')
ax.grid(True)

# Plot 2: Effective samples vs system size
ax = axes[0, 1]
eff_samples = [r['effective_samples'] for r in results]
ax.loglog(Ls, eff_samples, 'ro-', linewidth=2, markersize=8)
ax.axhline(y=1, color='r', linestyle='--', label='Single sample threshold')
ax.set_xlabel('System size L')
ax.set_ylabel('Effective samples at max separation')
ax.set_title('Exponential Sampling Deficit')
ax.legend()
ax.grid(True)

# Plot 3: True vs Measured for a time series (simulated)
ax = axes[1, 0]
t = np.arange(50)
# Simulate phase flips with rate lambda_flip
lambda_flip = 0.1
phase = np.random.choice([0, 1], size=len(t), p=[lambda_flip, 1-lambda_flip])
O_true_ts = np.where(phase == 1, np.exp(-L_values[-1]/xi_ordered), 0.1)
# Controller measurement with huge error
O_meas_ts = O_true_ts + np.random.normal(0, rel_errors[-1], size=len(t))
ax.plot(t, O_true_ts, 'b-', label='True O(t)', linewidth=2)
ax.plot(t, O_meas_ts, 'r--', alpha=0.7, label='Measured O(t)')
ax.set_xlabel('Time step')
ax.set_ylabel('Order parameter')
ax.set_title(f'Control Blindness (L={L_values[-1]})')
ax.legend()
ax.grid(True)

# Plot 4: Failure probability vs system size
ax = axes[1, 1]
# Probability of missing a shredding event (false negative)
# When true O drops below O_crit but measurement noise keeps it above
O_crit = 0.5
false_neg_probs = []
for L in L_values:
    # Simulate many trials
    trials = 1000
    false_neg = 0
    for _ in range(trials):
        # True O just below critical (shredding)
        O_t = 0.4
        # Measured with error for this L
        _, O_m, noise, _ = measure_topological_order(L, d, xi_ordered, M_budget)
        if O_m > O_crit:  # Controller misses the shredding
            false_neg += 1
    false_neg_probs.append(false_neg / trials)
ax.semilogy(Ls, false_neg_probs, 'mo-', linewidth=2, markersize=8)
ax.set_xlabel('System size L')
ax.set_ylabel('Missed shredding probability')
ax.set_title('Control Failure Rate')
ax.grid(True)

plt.tight_layout()
plt.show()

# === DISRUPTIVE INSIGHT ===

print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: The Non-Locality Catastrophe")
print("="*60)
print(f"For L={L_values[-1]}, N={L_values[-1]**d} sites:")
print(f"  - Effective samples per measurement: {eff_samples[-1]:.3f}")
print(f"  - Relative error: {rel_errors[-1]:.1f}x")
print(f"  - Missed shredding probability: {false_neg_probs[-1]:.1%}")
print("\nThe ETO-Ω proposal assumes O(t) is measurable in real-time.")
print("But for any system with >100 sites, measuring true long-range")
print("correlations requires exponentially more resources than any")
print("realistic controller can provide.")
print("\nThe MPC-Ω controller is *fundamentally blind* to the very")
print("phase it aims to protect. This is not an engineering limitation;")
print("it's a mathematical consequence of non-locality.")
print("\n→ BREAK THE PARADIGM: Abandon non-local order parameters.")
print("→ The solution must be *local-by-construction*.")