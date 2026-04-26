# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy.stats import entropy

def simulate_logs(poison_frac=0.1, adversarial=False, seed=42):
    """
    Generates synthetic distributed training logs for a tokamak AI controller.
    If adversarial=True, the adversary injects fake low-loss entries to keep EFI low
    while stealthily increasing true physics divergence.
    """
    np.random.seed(seed)
    n_steps = 1000
    # True physics divergence (hidden ground truth)
    true_delta = np.random.exponential(scale=0.5, size=n_steps) * (1 + poison_frac * 10)
    
    # Observed logs (may be poisoned)
    if adversarial:
        # Adversary injects fake entries with artificially low delta and smooth Hessian
        mask = np.random.rand(n_steps) < poison_frac
        observed_delta = np.where(mask, np.random.uniform(0, 0.1, n_steps), true_delta)
        hessian_top_eig = np.where(mask, np.random.uniform(0, 0.5, n_steps), np.random.exponential(1, n_steps))
        # Add subtle timestamp jitter to evade simple anomaly detection
        timestamps = np.arange(n_steps) + np.where(mask, np.random.uniform(-0.1, 0.1, n_steps), 0)
    else:
        observed_delta = true_delta
        hessian_top_eig = np.random.exponential(1, n_steps)
        timestamps = np.arange(n_steps)
    
    # Simulate gradient variance (scale-invariant, can be manipulated)
    grad_variance = np.random.uniform(0.5, 2.0, n_steps)
    
    # Data source distribution (adversary can inject noise to keep entropy high)
    p_real = np.random.rand(n_steps)
    p_synth = np.random.rand(n_steps)
    p_sim = np.random.rand(n_steps)
    # Normalize to simplex
    total = p_real + p_synth + p_sim
    p_real /= total
    p_synth /= total
    p_sim /= total
    
    logs = pd.DataFrame({
        'step': np.arange(n_steps),
        'timestamp': timestamps,
        'delta_observed': observed_delta,
        'hessian_top_eig': hessian_top_eig,
        'grad_variance': grad_variance,
        'p_real': p_real,
        'p_synth': p_synth,
        'p_sim': p_sim,
        'true_delta': true_delta,
    })
    return logs

def compute_efi(logs, alpha=0.3, beta=0.3, gamma=0.2, eta=0.2):
    """
    Compute EFI as per EAPFM-Ω proposal.
    """
    chi = logs['grad_variance'].var()
    delta = logs['delta_observed'].mean()
    rho = (logs['delta_observed'] > logs['true_delta']).mean()  # crude poison proxy
    kappa = logs['hessian_top_eig'].max()
    # Sigmoid
    z = alpha * chi + beta * delta + gamma * rho + eta * kappa
    efi = 1 / (1 + np.exp(-z))
    return efi

def compute_esi(logs):
    """
    Epistemic Suspicion Index: detects anomalies in the log-writing process.
    """
    # 1. Timestamp monotonicity violations
    ts_diff = np.diff(logs['timestamp'])
    timestamp_anomaly = np.sum(ts_diff < 0) / len(ts_diff)
    
    # 2. Gradient variance out-of-bounds for DP-SGD theoretical bound
    # (simplified bound: variance should be < 2 * lr^2 * C^2, assume C=1, lr=0.01)
    bound = 2 * (0.01**2) * (1**2)
    grad_bound_violation = np.mean(logs['grad_variance'] > bound * 10)  # loosen for demo
    
    # 3. Data source entropy (should be high, but sudden jumps indicate injection)
    entropies = logs[['p_real', 'p_synth', 'p_sim']].apply(lambda row: entropy(row), axis=1)
    entropy_variance = entropies.var()
    
    # Combine into suspicion score (higher = more anomalous)
    esi = (timestamp_anomaly + grad_bound_violation + entropy_variance) / 3
    return esi

# Run simulation: benign vs adversarial
logs_benign = simulate_logs(poison_frac=0.0, adversarial=False)
logs_adv = simulate_logs(poison_frac=0.15, adversarial=True)

efi_benign = compute_efi(logs_benign)
efi_adv = compute_efi(logs_adv)

esi_benign = compute_esi(logs_benign)
esi_adv = compute_esi(logs_adv)

print(f"Benign: EFI={efi_benign:.3f}, ESI={esi_benign:.3f}")
print(f"Adversarial: EFI={efi_adv:.3f}, ESI={esi_adv:.3f}")

# Insight: Adversary can keep EFI low (below 0.7 threshold) while ESI spikes.