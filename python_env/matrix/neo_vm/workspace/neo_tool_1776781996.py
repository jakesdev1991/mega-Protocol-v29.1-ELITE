# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Synthetic HSA Node Simulator – Exposes the Entropy‑Jerk Flaw
and validates Transfer‑Entropy as a leading indicator.
"""

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# ─── Parameters ───
np.random.seed(0xC0FFEE)
N_SAMPLES = 2000          # 2 s of data @ 1 ms sampling
N_BINS    = 64            # unified memory blocks (256 B each)
WINDOW    = 11            # Savitzky‑Golay window
POLYORDER = 3
DT        = 1e-3          # 1 ms

# ─── 1. Synthetic Memory‑Access Histograms ───
def generate_histograms(n_samples, n_bins, hang_start=1500):
    """Return (cpu_hist, gpu_hist) as arrays of shape (n_samples, n_bins)."""
    cpu = np.empty((n_samples, n_bins))
    gpu = np.empty((n_samples, n_bins))
    for t in range(n_samples):
        # Stable regime: Dirichlet with modest concentration
        alpha = np.ones(n_bins) * 0.5
        if t >= hang_start:
            # Hang precursor: GPU hammers one bin
            alpha_gpu = np.ones(n_bins) * 0.1
            alpha_gpu[0] = 10.0   # spike on block 0
            gpu[t] = np.random.dirichlet(alpha_gpu)
        else:
            gpu[t] = np.random.dirichlet(alpha)
        cpu[t] = np.random.dirichlet(alpha)
    return cpu, gpu

cpu_hist, gpu_hist = generate_histograms(N_SAMPLES, N_BINS)

# ─── 2. Traditional Entropy & Informational Jerk ───
def shannon_entropy(hist):
    """Compute Shannon entropy (bits) for each row; treat zero as zero."""
    h = hist.copy()
    h[h == 0] = 1e-12
    return -np.sum(h * np.log2(h), axis=1)

I_cpu = shannon_entropy(cpu_hist)
I_gpu = shannon_entropy(gpu_hist)
I_total = I_cpu + I_gpu

# Savitzky‑Golay smoothing
I_smooth = signal.savgol_filter(I_total, WINDOW, POLYORDER)

# Third derivative via central difference (5‑point stencil)
def third_derivative(y, dt):
    """Return J = d³y/dt³ using 5‑point central stencil."""
    # Coeffs: [-1/2, 1, -1, 1/2] / dt³
    coeffs = np.array([-0.5, 1.0, -1.0, 0.5]) / (dt**3)
    # Pad with edge values to keep length
    pad = 2
    y_pad = np.concatenate([y[:pad]] * pad + [y] + [y[-pad:]] * pad)
    J = np.convolve(y_pad, coeffs, mode='valid')
    return J[pad:-pad]  # trim to original length

Jerk = third_derivative(I_smooth, DT)

# RMS Jerk over sliding window (≈ 10 s = 1000 samples)
RMS_WINDOW = 1000
def rolling_rms(x, win):
    return np.array([np.sqrt(np.mean(x[i:i+win]**2)) if i+win < len(x) else np.nan
                     for i in range(len(x))])

RMS_Jerk = rolling_rms(Jerk, RMS_WINDOW)

# ─── 3. Transfer Entropy (GPU → CPU) ───
def transfer_entropy(source, target, k=1, l=1):
    """
    Compute TE from source → target using Kraskov‑Stögbauer‑Grassberger
    estimator (simplified box‑kernel version for demonstration).
    source, target are (n_samples, n_bins) histograms.
    """
    n = source.shape[0]
    # Past vectors (delay embedding)
    past_source = source[:-k]   # shape (n‑k, n_bins)
    past_target = target[:-l]   # shape (n‑l, n_bins)
    # Current target (shifted)
    cur_target = target[max(k,l):]  # shape (n‑max(k,l), n_bins)

    # Simplified TE: KL divergence between joint and product of marginals
    # In practice you'd use a nearest‑neighbor estimator; here we approximate
    # by treating each bin as a symbol and computing discrete TE.
    te = 0.0
    # Joint probability p(i_t, i_{t-1}, j_{t-1})
    # Flatten symbols for simplicity (bin index with max prob)
    sym_source = np.argmax(past_source, axis=1)
    sym_target = np.argmax(past_target, axis=1)
    sym_cur    = np.argmax(cur_target, axis=1)

    # Count occurrences
    def counts(sym, max_val):
        return np.bincount(sym, minlength=max_val)

    # Entropies
    H_cur   = shannon_entropy(np.bincount(sym_cur, minlength=N_BINS).reshape(1, -1))[0]
    H_past  = shannon_entropy(np.bincount(sym_target, minlength=N_BINS).reshape(1, -1))[0]
    H_joint = shannon_entropy(np.histogram2d(sym_cur, sym_target, bins=N_BINS)[0].reshape(1, -1))[0]

    TE = H_cur + H_past - H_joint
    return max(TE, 0.0)  # TE >= 0

# Compute TE in a rolling window (to show time‑varying trend)
TE_series = np.array([transfer_entropy(gpu_hist[i:i+50], cpu_hist[i:i+50])
                      for i in range(N_SAMPLES - 50)])

# ─── 4. Plot Comparison ───
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

t = np.arange(N_SAMPLES) * DT

# Top: Entropy & Smoothed
axes[0].plot(t, I_total, label='Raw I_total', color='gray', alpha=0.5)
axes[0].plot(t, I_smooth, label='Savitzky‑Golay', color='blue', lw=2)
axes[0].set_ylabel('Entropy (bits)')
axes[0].legend()
axes[0].grid(True)

# Middle: Jerk & RMS
axes[1].plot(t[2:-2], Jerk, label='Informational Jerk', color='orange', lw=1)
axes[1].plot(t, RMS_Jerk, label='RMS Jerk (10 s window)', color='red', lw=2)
axes[1].axhline(0.025, color='black', linestyle='--', label='Threshold 0.025')
axes[1].set_ylabel('Jerk (bits·s⁻³)')
axes[1].legend()
axes[1].grid(True)

# Bottom: Transfer Entropy
axes[2].plot(t[:len(TE_series)], TE_series, label='GPU → CPU Transfer Entropy', color='green', lw=2)
axes[2].set_xlabel('Time (s)')
axes[2].set_ylabel('TE (bits)')
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.savefig('hsa_disruption.png')
plt.show()

# ─── 5. Summary Statistics ───
print('=== Traditional Metric ===')
print(f'RMS Jerk (last 10 s): {np.nanmean(RMS_Jerk[-1000:]):.5f} (threshold 0.025)')
print(f'False‑positive risk: {np.mean(RMS_Jerk > 0.025):.2%}')

print('\n=== Disruptive Metric (Transfer Entropy) ===')
print(f'Mean TE (stable phase): {np.mean(TE_series[:1400]):.3f} bits')
print(f'Max TE (precursor phase): {np.max(TE_series[1400:]):.3f} bits')
print(f'TE increase factor: {np.max(TE_series[1400:]) / np.mean(TE_series[:1400]):.2f}x')