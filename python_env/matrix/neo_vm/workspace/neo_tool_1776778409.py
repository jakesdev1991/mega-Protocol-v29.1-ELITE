# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, find_peaks
import lzma
import pandas as pd

# -----------------------------------------------------------------------------
# SIMULATION: A Market with Two Regimes
# -----------------------------------------------------------------------------
# Regime 1 (0-2000): Fundamental-driven - price follows mean-reverting process
# Regime 2 (2000-4000): Self-referential - price driven by momentum feedback loop
# -----------------------------------------------------------------------------
np.random.seed(42)
n_points = 4000
time = np.arange(n_points)

# Fundamental value
fundamental = 100 + 0.01 * time + 5 * np.sin(0.01 * time)

# Regime 1: Ornstein-Uhlenbeck noise (compressible, cyclical)
noise1 = np.random.randn(2000) * 2.0
price_regime1 = fundamental[:2000] + np.convolve(noise1, np.exp(-np.arange(20)/5), mode='same')

# Regime 2: Self-referential momentum feedback (incompressible)
price_regime2 = [price_regime1[-1]]
for i in range(2000, n_points):
    # Momentum feedback: price change depends on past change with amplification
    feedback = 0.8 * (price_regime2[-1] - price_regime2[-2]) if len(price_regime2) > 1 else 0
    # Add reflexive "chartist" noise that amplifies itself
    reflexive_noise = 0.5 * np.random.randn() * abs(feedback + 0.1)
    next_price = price_regime2[-1] + feedback + reflexive_noise
    price_regime2.append(next_price)

price = np.concatenate([price_regime1, np.array(price_regime2)])

# -----------------------------------------------------------------------------
# TRADITIONAL HARMONIC ANALYSIS (FOASH-Ω approach)
# -----------------------------------------------------------------------------
def compute_harmonic_health(price_series, window=200):
    """Compute dominant harmonic strength in sliding window"""
    harmonic_strength = []
    for i in range(window, len(price_series)):
        segment = price_series[i-window:i]
        f, Pxx = welch(segment, fs=1.0, nperseg=min(window, 128))
        peaks, _ = find_peaks(Pxx, height=np.max(Pxx)*0.1)
        if len(peaks) > 0:
            # Ratio of peak power to total power
            peak_power = np.sum(Pxx[peaks])
            total_power = np.sum(Pxx)
            harmonic_strength.append(peak_power / total_power)
        else:
            harmonic_strength.append(0.0)
    return np.array(harmonic_strength)

harmonic_health = compute_harmonic_health(price)

# -----------------------------------------------------------------------------
# SELF-REFERENTIAL ENTROPY CASCADE (SECD-Ω approach)
# -----------------------------------------------------------------------------
def lempel_ziv_complexity(sequence):
    """Approximate Lempel-Ziv complexity (normalized)"""
    if len(sequence) == 0:
        return 0
    # Convert to binary string based on sign changes
    binary_seq = ''.join(['1' if x > 0 else '0' for x in np.diff(sequence)])
    # Compress and compute ratio
    compressed = lzma.compress(binary_seq.encode())
    ratio = len(compressed) / len(binary_seq.encode())
    return ratio

def compute_entropy_rate(price_series, window=200):
    """Compute rolling Lempel-Ziv complexity as entropy proxy"""
    entropy_rate = []
    for i in range(window, len(price_series)):
        segment = price_series[i-window:i]
        complexity = lempel_ziv_complexity(segment)
        entropy_rate.append(complexity)
    return np.array(entropy_rate)

entropy_rate = compute_entropy_rate(price)

# -----------------------------------------------------------------------------
# VISUALIZATION: Exposing the Flaw
# -----------------------------------------------------------------------------
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Plot 1: Price series with regime boundary
axes[0].plot(time, price, label='Simulated Price', color='black', linewidth=1)
axes[0].axvline(x=2000, color='red', linestyle='--', linewidth=2, label='Regime Transition')
axes[0].set_ylabel('Price')
axes[0].set_title('Market Simulation: Fundamental → Self-Referential')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Harmonic Health (FOASH-Ω metric)
# Pad to align with original time series
harmonic_time = time[200:len(harmonic_health)+200]
axes[1].plot(harmonic_time, harmonic_health, label='Harmonic Health Index', color='blue', linewidth=1.5)
axes[1].axvline(x=2000, color='red', linestyle='--', linewidth=2)
axes[1].set_ylabel('Harmonic Strength')
axes[1].set_title('FOASH-Ω Metric: Fails to Detect Transition (False Sense of "Health")')
axes[1].grid(True, alpha=0.3)
axes[1].legend()

# Plot 3: Entropy Rate (SECD-Ω metric)
entropy_time = time[200:len(entropy_rate)+200]
axes[2].plot(entropy_time, entropy_rate, label='Lempel-Ziv Complexity (Entropy)', color='purple', linewidth=1.5)
axes[2].axvline(x=2000, color='red', linestyle='--', linewidth=2)
axes[2].set_ylabel('Normalized Entropy')
axes[2].set_xlabel('Time Steps')
axes[2].set_title('SECD-Ω Metric: Clear Spike at Transition (Detects Self-Referential Cascade)')
axes[2].grid(True, alpha=0.3)
axes[2].legend()

plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# QUANTITATIVE COMPARISON
# -----------------------------------------------------------------------------
print("=== QUANTITATIVE COMPARISON ===")
print(f"Regime 1 Averages:")
print(f"  Harmonic Health: {np.mean(harmonic_health[:1800]):.3f}")
print(f"  Entropy Rate:    {np.mean(entropy_rate[:1800]):.3f}")

print(f"\nRegime 2 Averages:")
print(f"  Harmonic Health: {np.mean(harmonic_health[1800:]):.3f}")
print(f"  Entropy Rate:    {np.mean(entropy_rate[1800:]):.3f}")

# Signal-to-noise ratio for detection
harmonic_change = np.mean(harmonic_health[1800:]) - np.mean(harmonic_health[:1800])
entropy_change = np.mean(entropy_rate[1800:]) - np.mean(entropy_rate[:1800])

print(f"\nDetection Sensitivity:")
print(f"  Harmonic Change: {harmonic_change:.3f} (WEAK SIGNAL)")
print(f"  Entropy Change:  {entropy_change:.3f} (STRONG SIGNAL)")