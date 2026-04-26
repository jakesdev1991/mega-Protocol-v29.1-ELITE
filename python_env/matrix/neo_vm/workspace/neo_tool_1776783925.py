# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# --- DISRUPTIVE SIMULATION ---
# The Engine's "Informational Jerk" is a derivative illusion: 
# a fragile metric built on smoothed noise. Let's expose it.

np.random.seed(0xDEADBEEF) # Neo's seed
n_samples = 2000
dt = 1e-3 # 1 ms sampling

# Simulate TRUE underlying system state: memory access burstiness
# 1. STABLE: Homogeneous Poisson access -> low variance
# 2. UNSTABLE: Heterogeneous with micro-bursts (race condition precursor) -> high variance
lambda_base = 100
burst_factor = 5
burst_prob = 0.005 # 0.5% of windows have a micro-burst

is_burst = np.random.random(n_samples) < burst_prob
access_counts = np.random.poisson(lambda_base, n_samples)
access_counts[is_burst] = np.random.poisson(lambda_base * burst_factor, np.sum(is_burst))

# Engine's "I_total(t)" is a derived scalar. Let's be explicit:
# It's the *entropy* of a histogram. For a single bin proxy, we use 
# I(t) ∝ log(std_dev(counts)) to capture "spread". This is the *first* abstraction.
I_raw = np.log(1 + access_counts + np.random.normal(0, 3, n_samples))

# Engine's STEP 1: Savitzky-Golay filter (assumes smoothness, but instability is *non-smooth*)
I_smooth = savgol_filter(I_raw, window_length=11, polyorder=3)

# Engine's STEP 2: Central-difference third derivative (amplifies noise & filter artifacts)
def compute_jerk_engine(I, dt):
    J = np.zeros_like(I)
    for i in range(2, len(I) - 2):
        J[i] = (-I[i-2] + 2*I[i-1] - 2*I[i+1] + I[i+2]) / (2 * dt**3)
    return J

Jerk = compute_jerk_engine(I_smooth, dt)
RMS_Jerk = np.sqrt(np.convolve(Jerk**2, np.ones(50)/50, mode='same'))

# --- ANOMALY: DIRECT METRIC ---
# The instability isn't in the *third derivative* of a smoothed log.
# It's in the *variance* itself. Measure burstiness DIRECTLY.
# Coefficient of Variation over a short window: no filters, no derivatives.
def coefficient_of_variation(signal, window=50):
    cv = np.zeros_like(signal, dtype=float)
    for i in range(window, len(signal) - window):
        w = signal[i-window:i]
        mean = np.mean(w)
        cv[i] = np.std(w) / mean if mean > 0 else 0
    return cv

CV_direct = coefficient_of_variation(I_raw, window=30) # Shorter window = faster response

# --- VISUAL DESTRUCTION ---
fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

axes[0].plot(I_raw, label='Raw I(t) (Proxy)', alpha=0.6, color='gray')
axes[0].plot(I_smooth, label='Smoothed I(t) (Engine)', linewidth=1.5, color='blue')
axes[0].set_title("Neo: Smoothing Imposes False Continuity", fontsize=10)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(Jerk, label='Informational Jerk (Third Derivative)', alpha=0.7, color='orange')
axes[1].axhline(0, color='k', linewidth=0.5)
axes[1].set_title("Neo: Jerk is Dominated by Filter Artifacts & Noise Amplification", fontsize=10)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

axes[2].plot(RMS_Jerk, label='RMS Jerk (Engine Stability Metric)', alpha=0.7, color='red')
axes[2].plot(CV_direct * 0.05, label='CV Direct (Scaled Burstiness)', alpha=0.7, color='purple', linewidth=2) # Scale for visual comparison
axes[2].axhline(0.025, color='r', linestyle='--', label='Instability Threshold')
axes[2].set_title("Neo: Direct CV Detects Bursts; RMS Jerk is Blind & Lagging", fontsize=10)
axes[2].legend()
axes[2].grid(True, alpha=0.3)
axes[2].set_xlabel('Time (ms)')

plt.tight_layout()
plt.show()

# --- MATHEMATICAL EXECUTION ---
# Let's quantify the fragility: 
# Signal-to-Noise Ratio (SNR) degradation at each stage.
def snr(signal, noise_floor_std):
    return np.var(signal) / (noise_floor_std**2)

print("\n=== Φ-DENSITY ANOMALY AUDIT ===")
print(f"SNR of Raw Signal: {snr(I_raw, 3):.2f}")
print(f"SNR Loss from Smoothing: {snr(I_smooth, 3) / snr(I_raw, 3):.2f}x")
print(f"SNR of Jerk (vs. Raw): {snr(Jerk, np.std(Jerk)) / snr(I_raw, 3):.6f}x (CATASTROPHIC)")
print(f"Mean CV (Stable region): {np.mean(CV_direct[:500]):.4f}")
print(f"Mean CV (Unstable region): {np.mean(CV_direct[1500:]):.4f} | Ratio: {np.mean(CV_direct[1500:]) / np.mean(CV_direct[:500]):.2f}x increase")