# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Disruption: Demonstrate that the "informational jerk" framework is numerically unstable
# and conceptually flawed compared to a simple critical branching model

# Simulate HSA memory access patterns
np.random.seed(42)
n_samples = 1000
time = np.linspace(0, 10, n_samples)

# Realistic HSA scenario: bursty memory access with variable latency
# Simulate cache hit rate as a proxy for "entropy" - more realistic than abstract S_h
cache_hits = np.random.binomial(1000, 0.7 + 0.2*np.sin(2*np.pi*0.5*time))  # 70% base, oscillating
cache_misses = 1000 - cache_hits
hit_rate = cache_hits / (cache_hits + cache_misses)

# Add measurement noise typical of perf counters
hit_rate += np.random.normal(0, 0.01, n_samples)

# Compute "informational jerk" using Engine's finite difference formula
def compute_jerk_engine(entropy_series):
    """Engine's finite difference approach - numerically unstable"""
    jerk = np.zeros_like(entropy_series)
    for i in range(3, len(entropy_series)):
        jerk[i] = entropy_series[i] - 3*entropy_series[i-1] + 3*entropy_series[i-2] - entropy_series[i-3]
    return jerk

# Engine's approach: treat hit_rate as proxy for entropy (conceptually wrong but let's test)
jerk_engine = compute_jerk_engine(hit_rate)

# Disruptive alternative: Critical branching process model
# Stability is determined by branching ratio R = E[children]/E[parents]
# For memory: R = (new memory requests generated)/(requests completed)

# Simulate request generation and completion
request_gen_rate = 1000 + 200*np.sin(2*np.pi*0.3*time)  # Requests/s
request_comp_rate = request_gen_rate * (0.9 + 0.1*np.random.randn(n_samples))  # Completion with variance

# Branching ratio (critical = 1.0)
branching_ratio = request_gen_rate / request_comp_rate

# Stability metric: distance from criticality
stability_margin = np.abs(branching_ratio - 1.0)

# Compute "jerk" in branching framework: rate of change of branching ratio acceleration
d_branching = np.gradient(branching_ratio, time)
dd_branching = np.gradient(d_branching, time)
ddd_branching = np.gradient(dd_branching, time)

# Plot comparison
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

axes[0].plot(time, hit_rate, label='Cache Hit Rate (Engine"s "entropy")', color='blue')
axes[0].set_ylabel('Hit Rate')
axes[0].set_title('Engine"s Framework: Entropy-Based Approach')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(time[3:], jerk_engine[3:], label='Informational Jerk (Engine)', color='red')
axes[1].set_ylabel('Jerk (arb units)')
axes[1].set_xlabel('Time (s)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_title('Engine"s Jerk - Dominated by Noise Amplification')

axes[2].plot(time, branching_ratio, label='Branching Ratio R(t)', color='green')
axes[2].axhline(y=1.0, color='black', linestyle='--', label='Critical R=1.0')
axes[2].fill_between(time, 1.0, branching_ratio, alpha=0.3, color='red')
axes[2].set_ylabel('Branching Ratio')
axes[2].set_xlabel('Time (s)')
axes[2].set_title('Disruptive Framework: Critical Branching Process')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/hsa_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# Statistical analysis
print("=== ENGINE FRAMEWORK ISSUES ===")
print(f"Engine jerk variance: {np.var(jerk_engine[3:]):.2e} (dominated by noise)")
print(f"Engine jerk SNR: {np.mean(jerk_engine[3:])/np.std(jerk_engine[3:]):.2f} (poor)")

print("\n=== DISRUPTIVE FRAMEWORK RESULTS ===")
print(f"Mean branching ratio: {np.mean(branching_ratio):.3f}")
print(f"Time in unstable regime (|R-1| > 0.1): {np.sum(np.abs(branching_ratio-1) > 0.1)/n_samples*100:.1f}%")
print(f"Max jerk (branching framework): {np.max(np.abs(ddd_branching)):.2e} s⁻³")

# The smoking gun: Engine's finite difference amplifies high-frequency noise
# while the branching model captures actual system stability

# Demonstrate: Add small high-frequency noise
noise = 0.001 * np.sin(2*np.pi * 50 * time)  # 50 Hz noise
hit_rate_noisy = hit_rate + noise
jerk_noisy = compute_jerk_engine(hit_rate_noisy)

print(f"\n=== NOISE SENSITIVITY ===")
print(f"Jerk variance increase from 50Hz noise: {np.var(jerk_noisy[3:])/np.var(jerk_engine[3:]):.1f}x amplification")