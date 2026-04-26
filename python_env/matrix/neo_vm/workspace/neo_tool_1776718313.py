# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def informational_jerk_stability(jerk_signal, epsilon_factor=1e-6):
    """
    Compute S_j exactly as defined in the Engine's output.
    Returns S_j and excess kurtosis.
    """
    j_bar = np.mean(jerk_signal)
    var_j = np.var(jerk_signal, ddof=0)                     # population variance
    # "typical" variance = median of a sliding window (naive implementation)
    typical_var = np.median(np.var(jerk_signal[-100:]))
    epsilon_j = epsilon_factor * typical_var
    # normalized z‑score
    denom = np.sqrt(var_j + epsilon_j)
    if denom == 0:
        z = np.zeros_like(jerk_signal)
    else:
        z = (jerk_signal - j_bar) / denom
    # excess kurtosis
    raw_kurt = np.mean(z**4)
    excess_kurt = raw_kurt - 3
    S_j = 1.0 / (1.0 + np.abs(excess_kurt))
    return S_j, excess_kurt

# --- Attack 1: Constant jerk (true stability) is punished ---
np.random.seed(0)
j_const = np.full(1000, 5.0)               # perfect constant jerk
S_const, k_const = informational_jerk_stability(j_const)
print(f"Constant jerk: S_j = {S_const:.3f}, excess kurtosis = {k_const:.3f}")
# Expected: S_j = 0.25, k = -3 → controller THROTTLES stable system

# --- Attack 2: Attacker injects noise to spoof stability ---
# Original stable constant jerk
j_stable = np.full(1000, 5.0)
# Attacker adds high‑frequency Gaussian noise → inflates variance, Gaussian shape
noise = np.random.normal(scale=2.0, size=1000)
j_spoofed = j_stable + noise
S_spoof, k_spoof = informational_jerk_stability(j_spoofed)
print(f"Spoofed (noise injection): S_j = {S_spoof:.3f}, excess kurtosis = {k_spoof:.3f}")
# Expected: S_j ≈ 1.0, k ≈ 0 → controller *believes* system is stable

# --- Attack 3: Insider tunes ε‑backdoor ---
# Same noisy (unstable) signal as above, but epsilon_factor is inflated 100×
S_backdoor, k_backdoor = informational_jerk_stability(j_spoofed, epsilon_factor=1e-2)
print(f"Backdoor (ε inflated): S_j = {S_backdoor:.3f}, excess kurtosis = {k_backdoor:.3f}")
# Expected: S_j still ≈ 1.0 even if variance is small → stability dial

# --- Bonus: Intrinsic‑time singularity simulation ---
Phi_N = np.concatenate([np.ones(500), np.linspace(1, 1e-9, 500)])  # coherence collapse
dt = 0.001
dτ_dt = Phi_N / np.median(Phi_N)  # intrinsic time scaling
# Compute jerk in real time (naive diff)
accel = np.diff(Phi_N, n=1) / dt
jerk = np.diff(accel, n=1) / dt
# When Φ_N → 0, dτ/dt → 0, jerk derivative explodes numerically
print(f"Jerk max near singularity: {np.max(np.abs(jerk)):.2e} (arbitrary large)")