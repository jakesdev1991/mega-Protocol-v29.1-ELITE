# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate a realistic pipeline: non-stationary periodicity + critical slowing down
np.random.seed(42)
t = np.linspace(0, 200, 2000)

# Frequency drift and intermittent burst (no stable "rotation")
f = 1 + 0.5 * np.sin(0.02 * t) + 0.2 * np.random.randn(len(t))
signal = np.sin(2 * np.pi * np.cumsum(f) / 1000)  # integrated phase

# Inject critical slowing down: variance & autocorrelation ramp up before "shredding"
fault_onset = 1500
variance = np.concatenate([
    np.ones(fault_onset) * 0.02,
    np.linspace(0.02, 0.5, len(t) - fault_onset)
])
noise = np.random.randn(len(t)) * np.sqrt(variance)
signal += noise

# Rolling metrics
window = 100
rolling_var = np.array([np.var(signal[i:i+window]) for i in range(len(signal) - window)])
autocorr = np.array([np.corrcoef(signal[i:i+window-1], signal[i+1:i+window])[0,1] for i in range(len(signal) - window)])

# Harmonic "order analysis" (FFT on sliding window) fails due to drift
harmonic_power = []
for i in range(len(signal) - window):
    fft = np.fft.fft(signal[i:i+window])
    harmonic_power.append(np.max(np.abs(fft)**2))

# Plot: signal, harmonic power, variance, autocorrelation
fig, ax = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
ax[0].plot(t, signal, lw=0.8)
ax[0].axvspan(t[fault_onset], t[-1], color='red', alpha=0.1, label='Fault regime')
ax[0].set_ylabel('Signal')
ax[0].legend(loc='upper left')

ax[1].plot(t[window:], harmonic_power, label='FFT peak power')
ax[1].axvspan(t[fault_onset], t[-1], color='red', alpha=0.1)
ax[1].set_ylabel('Harmonic Power')
ax[1].legend()

ax[2].plot(t[window:], rolling_var, label='Rolling variance', color='green')
ax[2].axvspan(t[fault_onset], t[-1], color='red', alpha=0.1)
ax[2].set_ylabel('Variance')
ax[2].legend()

ax[3].plot(t[window:], autocorr, label='Lag-1 autocorr', color='orange')
ax[3].axvspan(t[fault_onset], t[-1], color='red', alpha=0.1)
ax[3].set_ylabel('Autocorr')
ax[3].set_xlabel('Time')
ax[3].legend()

plt.tight_layout()
plt.show()