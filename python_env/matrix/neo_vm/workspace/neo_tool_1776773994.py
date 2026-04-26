# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import cwt, morlet2
from scipy.stats import linregress

# --- Synthetic Pipeline Metric ---
np.random.seed(0)
n = 5000
t = np.arange(n)

# Baseline: white noise
baseline = np.random.normal(0, 1, n)

# Inject non-stationary bursts (regime changes) and a final fault
burst_times = [1000, 2000, 3000, 4000]
for start in burst_times:
    length = 200
    baseline[start:start+length] += np.random.normal(0, 3, length)

# Fault at t=4500: permanent variance increase
baseline[4500:] = np.random.normal(0, 4, n-4500)

# Add slow drift (non-periodic)
drift = 0.5 * np.sin(t / 1000) + 0.2 * t / n
signal = baseline + drift

# --- Naive Harmonic PHI (Flawed) ---
def compute_phi_harmonic(ts, window=200, nominal_period=100):
    """Compute PHI assuming a fixed 'pipeline rotation' period."""
    phi_series = np.full_like(ts, np.nan, dtype=float)
    # Baseline amplitudes from first healthy segment
    healthy = ts[:1000]
    fft_healthy = np.fft.rfft(healthy)
    freqs = np.fft.rfftfreq(len(healthy), d=1.0)
    # Extract "order" harmonics around nominal_period
    target_freqs = np.array([1/nominal_period, 2/nominal_period, 3/nominal_period])
    base_amps = np.array([np.abs(fft_healthy[np.argmin(np.abs(freqs - f))]) for f in target_freqs])
    
    for i in range(window, len(ts) - window):
        segment = ts[i-window//2:i+window//2]
        fft_seg = np.fft.rfft(segment)
        seg_amps = np.array([np.abs(fft_seg[np.argmin(np.abs(freqs - f))]) for f in target_freqs])
        # Normalized deviation
        dev = np.mean(np.abs(seg_amps - base_amps) / (base_amps + 1e-9))
        phi_series[i] = 1.0 - dev
    return phi_series

phi = compute_phi_harmonic(signal)

# --- Multifractal Criticality Index (Δh) ---
def wavelet_modulus_maxima_spectrum(ts, scales=np.arange(1, 31)):
    """Estimate singularity spectrum width Δh via wavelet leaders."""
    # Continuous wavelet transform with complex Morlet
    widths = scales
    cwtmatr = cwt(ts, morlet2(widths, widths), widths)
    # Modulus maxima: local maxima along scales at each time point
    modulus = np.abs(cwtmatr)
    # Partition function Z(q, s) = sum_i (max_i |W(t,s)|)^q
    Z = np.zeros((len(scales), 3))  # q = -1, 0, 1
    for i, s in enumerate(scales):
        maxima = np.max(modulus[i, :])
        Z[i, 0] = maxima**(-1) if maxima > 0 else 0
        Z[i, 1] = np.log(maxima) if maxima > 0 else 0
        Z[i, 2] = maxima**1
    
    # Scaling exponents τ(q) from log(Z) vs log(s)
    tau = np.zeros(3)
    for q_idx in range(3):
        valid = Z[:, q_idx] > 0
        if valid.sum() > 2:
            slope, _, _, _, _ = linregress(np.log(scales[valid]), np.log(Z[valid, q_idx]))
            tau[q_idx] = slope
    
    # Legendre transform to get D(h) spectrum (approximated)
    # Simple linear estimate of Δh = max(h) - min(h) where h = dτ/dq
    # Approximate derivative with finite differences
    h_est = np.gradient(tau, [-1, 0, 1])
    delta_h = np.max(h_est) - np.min(h_est) if not np.all(np.isnan(h_est)) else 0
    return delta_h

# Sliding window Δh
window_multif = 500
delta_h_series = np.full_like(signal, np.nan, dtype=float)
for i in range(window_multif, len(signal) - window_multif):
    delta_h_series[i] = wavelet_modulus_maxima_spectrum(signal[i-window_multif:i+window_multif])

# --- Plot ---
fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

ax[0].plot(t, signal, label='Pipeline Metric')
ax[0].axvline(4500, color='r', linestyle='--', label='Fault Onset')
ax[0].set_ylabel('Signal')
ax[0].legend()

ax[1].plot(t, phi, label='Harmonic PHI (Flawed)', color='orange')
ax[1].set_ylabel('PHI')
ax[1].legend()

ax[2].plot(t, delta_h_series, label='Multifractal Width Δh', color='green')
ax[2].set_ylabel('Δh')
ax[2].set_xlabel('Time')
ax[2].legend()

plt.suptitle('Harmonic PHI vs. Multifractal Criticality Index')
plt.tight_layout()
plt.show()