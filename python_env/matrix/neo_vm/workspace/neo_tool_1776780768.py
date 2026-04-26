# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- SIMULATION PARAMETERS ---
np.random.seed(42)
T = 100  # time steps
dt = 1.0

# Toy configuration space: 2D (baseline length, integration time)
# True AGN state: simple Gaussian source size parameter
def true_AGN_state(t, unstable=False):
    """True AGN state: constant (stable) or sinusoidal (unstable)"""
    if unstable:
        # Flare: rapid change in source structure
        return 1.0 + 0.5 * np.sin(2 * np.pi * t / 20)
    else:
        # Quiescent: static source
        return 1.0

def observer_model_estimate(true_state, t, model_quality='good'):
    """Observer's estimate of AGN state with model error"""
    if model_quality == 'good':
        # Good model: small noise
        noise = 0.02 * np.random.randn()
        return true_state + noise
    else:
        # Poor model: large, correlated errors (overfitting to noise)
        # This simulates epistemic instability: the model "hunts" for structure
        bias = 0.3 * np.sin(2 * np.pi * t / 7)  # Observer's periodic "insight"
        noise = 0.1 * np.random.randn()
        return true_state + bias + noise

def information_gain(c, est_state):
    """Toy information gain function: peaked at configuration matching estimated size"""
    # This is the key: IG depends on ESTIMATED state, not true state
    baseline, int_time = c
    # Optimal baseline scales with estimated source size
    optimal_baseline = est_state * 1000  # arbitrary scaling
    # Sharpness of peak controlled by model confidence (here, constant)
    sharpness = 0.01
    # Information gain is a Gaussian-like function centered on optimal config
    ig = np.exp(-sharpness * (baseline - optimal_baseline)**2) * (1 - np.exp(-int_time / 10))
    return ig

def find_optimal_configuration(est_state):
    """Brute-force find max IG configuration for estimated state"""
    # Grid search over config space
    baselines = np.linspace(500, 1500, 100)
    int_times = np.linspace(1, 20, 20)
    max_ig = -1
    best_c = None
    for b in baselines:
        for it in int_times:
            ig = information_gain((b, it), est_state)
            if ig > max_ig:
                max_ig = ig
                best_c = (b, it)
    return best_c

def compute_cdi(config_history):
    """Compute CDI from configuration trajectory"""
    if len(config_history) < 3:
        return 0.0
    # Reconfiguration amplitude (norm of diff)
    amp = np.linalg.norm(np.array(config_history[-1]) - np.array(config_history[-2]))
    # Divergence from actual (simulated as previous config)
    div = np.linalg.norm(np.array(config_history[-1]) - np.array(config_history[-3]))
    # Frequency component: 1 if changed significantly
    freq = 1.0 if amp > 50 else 0.0  # threshold
    return 0.3 * freq + 0.5 * amp + 0.2 * div

# --- SCENARIOS ---
print("Simulating Configuration Dynamics Paradox...")

# Scenario 1: Unstable AGN, Good Model
print("\n--- Scenario 1: Unstable AGN, Good Model ---")
true_states_1 = []
est_states_1 = []
configs_1 = []
cdis_1 = []
for t in range(T):
    true_s = true_AGN_state(t, unstable=True)
    est_s = observer_model_estimate(true_s, t, model_quality='good')
    opt_c = find_optimal_configuration(est_s)
    
    true_states_1.append(true_s)
    est_states_1.append(est_s)
    configs_1.append(opt_c)
    cdis_1.append(compute_cdi(configs_1))

# Scenario 2: Stable AGN, Poor Model (Epistemic Instability)
print("\n--- Scenario 2: Stable AGN, Poor Model ---")
true_states_2 = []
est_states_2 = []
configs_2 = []
cdis_2 = []
for t in range(T):
    true_s = true_AGN_state(t, unstable=False)
    est_s = observer_model_estimate(true_s, t, model_quality='bad')
    opt_c = find_optimal_configuration(est_s)
    
    true_states_2.append(true_s)
    est_states_2.append(est_s)
    configs_2.append(opt_c)
    cdis_2.append(compute_cdi(configs_2))

# --- ANALYSIS ---
# Compute correlation between CDI and true AGN "instability"
# Here, instability is variance of true state
instability_1 = np.var(true_states_1)
instability_2 = np.var(true_states_2)

mean_cdi_1 = np.mean(cdis_1)
mean_cdi_2 = np.mean(cdis_2)

print(f"\nTrue Instability (variance) - Scenario 1 (unstable): {instability_1:.4f}")
print(f"Mean CDI - Scenario 1: {mean_cdi_1:.4f}")

print(f"\nTrue Instability (variance) - Scenario 2 (stable): {instability_2:.4f}")
print(f"Mean CDI - Scenario 2: {mean_cdi_2:.4f}")

# The paradox: stable AGN with poor model shows HIGHER CDI
print(f"\n{'PARADOX CONFIRMED' if mean_cdi_2 > mean_cdi_1 else 'Paradox not observed'}")
print(f"CDI is {'higher' if mean_cdi_2 > mean_cdi_1 else 'lower'} for the stable AGN with poor model.")

# --- VISUALIZATION ---
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plot 1: True vs Estimated State
axes[0].plot(true_states_1, label='True State (Unstable)', linewidth=2, color='red')
axes[0].plot(est_states_1, label='Estimate (Good Model)', linestyle='--', color='blue')
axes[0].set_title('Unstable AGN: True vs Estimated State')
axes[0].set_ylabel('Source Size')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(true_states_2, label='True State (Stable)', linewidth=2, color='green')
axes[1].plot(est_states_2, label='Estimate (Poor Model)', linestyle='--', color='orange')
axes[1].set_title('Stable AGN: True vs Estimated State')
axes[1].set_ylabel('Source Size')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 2: CDI Comparison
axes[2].plot(cdis_1, label='CDI (Unstable AGN, Good Model)', color='red', linewidth=2)
axes[2].plot(cdis_2, label='CDI (Stable AGN, Poor Model)', color='orange', linewidth=2)
axes[2].set_title('Configuration Dynamics Index (CDI) - Paradox')
axes[2].set_ylabel('CDI')
axes[2].set_xlabel('Time Step')
axes[2].legend()
axes[2].grid(True, alpha=0.3)
axes[2].axhline(y=np.mean(cdis_1), color='red', linestyle=':', alpha=0.5)
axes[2].axhline(y=np.mean(cdis_2), color='orange', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()

# --- CORRELATION ANALYSIS ---
# Show CDI is anti-correlated with true instability when model quality is confounded
print("\n--- Correlation Analysis ---")
# In real data, we don't know model quality. If we mix scenarios:
mixed_cdi = np.concatenate([cdis_1, cdis_2])
mixed_instability = np.concatenate([np.full_like(cdis_1, instability_1), np.full_like(cdis_2, instability_2)])
correlation = np.corrcoef(mixed_cdi, mixed_instability)[0, 1]
print(f"Correlation between CDI and True Instability (mixed scenarios): {correlation:.4f}")
print("A negative or near-zero correlation demonstrates the paradox: CDI is not sensing the AGN, it's sensing the observer.")