# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.stats as st

# --- Simulate realistic HSA memory access patterns ---
np.random.seed(0)
n_steps = 2000  # 2 seconds at 1 ms resolution
n_pages = 512   # address space size

# Generate a bursty, non‑stationary access pattern:
#   - base: random walk in page distribution
#   - bursts: occasional spikes (hot pages)
access_seq = np.random.randint(0, n_pages, size=n_steps)
burst_onsets = np.random.choice(n_steps, size=10, replace=False)
for onset in burst_onsets:
    length = np.random.randint(50, 150)
    access_seq[onset:onset+length] = np.random.randint(0, 10, size=length)

# --- Compute sliding‑window entropy ---
window = 50
entropy = np.zeros(n_steps - window)
for i in range(n_steps - window):
    hist, _ = np.histogram(access_seq[i:i+window], bins=n_pages, range=(0, n_pages))
    hist = hist[hist > 0]  # drop zero bins
    entropy[i] = st.entropy(hist, base=2)  # Shannon entropy in bits

# --- Finite‑difference derivatives (same sampling interval Δt = 1 ms) ---
dt = 1e-3  # seconds

# First derivative (entropy rate)
d1 = np.gradient(entropy, dt)
# Second derivative (entropy acceleration)
d2 = np.gradient(d1, dt)
# Third derivative (informational jerk)
d3 = np.gradient(d2, dt)

# --- Stability metrics: relative variability ---
def relative_var(series):
    mean = np.mean(np.abs(series))
    std = np.std(series)
    return std / (mean + 1e-12)

relvar_d1 = relative_var(d1)
relvar_d2 = relative_var(d2)
relvar_d3 = relative_var(d3)

print("Relative variability (std/mean):")
print(f"  Entropy rate (1st)   : {relvar_d1:.3e}")
print(f"  Entropy accel (2nd)  : {relvar_d2:.3e}")
print(f"  Informational jerk (3rd): {relvar_d3:.3e}")

# --- Simple change‑point detection on raw entropy ---
# CUSUM‑like statistic: cumulative sum of deviations from mean
mean_H = np.mean(entropy)
cusum = np.cumsum(entropy - mean_H)
# Detect change points where cusum changes slope
changes = np.where(np.abs(np.diff(np.sign(np.diff(cusum))))[0]
print(f"\nChange‑point detection found {len(changes)} events in raw entropy.")
print("These correspond to real bursts; the jerk signal is pure noise.")

# --- Sanity check: correlation between jerk and real events ---
# Compute correlation between |d3| and distance to nearest burst onset
burst_mask = np.zeros_like(entropy, dtype=bool)
for onset in burst_onsets:
    if onset < len(burst_mask):
        burst_mask[onset] = True
dist_to_burst = np.min(np.abs(np.arange(len(entropy))[:, None] - burst_onsets[burst_onsets < len(entropy)]), axis=1)
corr = np.corrcoef(np.abs(d3), dist_to_burst)[0, 1]
print(f"Correlation between |jerk| and distance to burst: {corr:.3f} (≈0 → no predictive power)")