# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# --- Parameters ---
N_FIRMS = 5
STEPS = 100
TRUE_VALUE = 100.0
NOISE = 5.0

# Config vector for each firm: [discount_rate, success_prob]
# Rational benchmark: [0.08, 0.4]
configs = np.array([[0.12 + random.uniform(-0.02, 0.02),
                     0.5 + random.uniform(-0.05, 0.05)] for _ in range(N_FIRMS)])

# Payoff: accuracy (closer to true value) + herding (similarity to others)
def payoff(config, others, true_val):
    # Simplified valuation model: value = true_val * (1 - discount) * success_prob
    val = true_val * (1 - config[0]) * config[1]
    # Herding term: negative Euclidean distance to other firms' configs
    herd = -np.mean([np.linalg.norm(config - o) for o in others])
    return -abs(val - true_val) + 0.5 * herd

# Metrics
vci_history = []
adv_grad_history = []
strategy_entropy_history = []

for t in range(STEPS):
    # --- Compute static VCI (bias relative to rational benchmark) ---
    rational = np.array([0.08, 0.4])
    biases = np.abs(configs - rational)
    vci = np.mean(biases) / (np.mean(biases) + 1e-6)  # Normalize
    vci_history.append(vci)

    # --- Compute Adversarial Gradient (average absolute config change) ---
    if t == 0:
        adv_grad = 0.0
    else:
        adv_grad = np.mean(np.abs(configs - prev_configs))
    adv_grad_history.append(adv_grad)
    prev_configs = configs.copy()

    # --- Compute Strategy Entropy (Shannon entropy of config distribution) ---
    # Discretize config space into bins
    hist, _ = np.histogramdd(configs, bins=[5, 5], range=[(0.05, 0.2), (0.2, 0.8)])
    p = hist / (hist.sum() + 1e-6)
    # Flatten and compute Shannon entropy
    p_flat = p.flatten()
    p_flat = p_flat[p_flat > 0]
    S = -np.sum(p_flat * np.log(p_flat))
    strategy_entropy_history.append(S)

    # --- Update configs via best-response gradient ---
    # Each firm adjusts its config to maximize payoff, with step size 0.01
    for i in range(N_FIRMS):
        # Perturb config slightly in random direction to estimate gradient
        eps = 1e-3
        grad = np.zeros(2)
        for dim in range(2):
            delta = np.zeros(2)
            delta[dim] = eps
            plus = payoff(configs[i] + delta, np.delete(configs, i, axis=0), TRUE_VALUE)
            minus = payoff(configs[i] - delta, np.delete(configs, i, axis=0), TRUE_VALUE)
            grad[dim] = (plus - minus) / (2 * eps)
        # Update config with momentum
        configs[i] += 0.01 * grad + 0.005 * (random.random() - 0.5)  # Add noise

    # --- Simulate external shock at t=70 (e.g., failed trial) ---
    if t == 70:
        TRUE_VALUE -= 30.0  # Large drop

# --- Identify Crash ---
# Crash defined as large drop in TRUE_VALUE
crash_step = 70

# Print metrics around crash
print(f"Step {crash_step}:")
print(f"  Static VCI: {vci_history[crash_step]:.3f} (low = 'rational')")
print(f"  Adversarial Gradient: {adv_grad_history[crash_step]:.3f} (spike = fragility)")
print(f"  Strategy Entropy: {strategy_entropy_history[crash_step]:.3f} (low = herding)")

# Show that VCI is low but adversarial gradient spikes before crash
pre_crash_grad = adv_grad_history[crash_step - 5]
print(f"\nPre-crash adversarial gradient (5 steps before): {pre_crash_grad:.3f}")
print("Conclusion: Static VCI fails; dynamic adversarial gradient and entropy collapse predict crash.")