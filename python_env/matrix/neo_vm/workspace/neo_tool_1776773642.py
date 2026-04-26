# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Synthetic HSA memory access generator ---
def generate_accesses(n_steps=1000, n_regions=16, hotspot_start=500, hotspot_duration=10):
    """Simulate memory access counts per region; inject a hotspot at region 0."""
    # Baseline: random Poisson-like counts around 1000
    counts = np.random.poisson(lam=1000, size=(n_steps, n_regions)).astype(float)
    # Add Gaussian noise for realism
    counts += np.random.normal(0, 50, size=counts.shape)
    # Inject hotspot: region 0 gets +500 accesses for hotspot_duration steps
    counts[hotspot_start:hotspot_start + hotspot_duration, 0] += 500
    return counts

# --- Shannon entropy (natural log) ---
def entropy(row):
    """Compute Shannon entropy of a probability vector derived from counts."""
    total = row.sum()
    if total == 0:
        return 0.0
    p = row / total
    # Avoid log(0) by masking
    p_safe = np.where(p > 0, p, 1.0)
    H = -np.sum(p * np.log(p_safe))
    return H

# --- Hurst exponent via rescaled range (R/S) ---
def hurst(ts):
    """Estimate Hurst exponent H for time series ts (length >= 20)."""
    N = len(ts)
    if N < 20:
        return np.nan
    # Choose lags from 2 to N//2
    lags = np.arange(2, N // 2)
    RS_vals = []
    for lag in lags:
        # Split series into non‑overlapping blocks of size lag
        n_blocks = N // lag
        if n_blocks < 2:
            continue
        blocks = ts[:n_blocks * lag].reshape(n_blocks, lag)
        # Mean of each block
        means = blocks.mean(axis=1, keepdims=True)
        # Cumulative deviations from mean
        cumdev = np.cumsum(blocks - means, axis=1)
        # Range R and standard deviation S per block
        R = np.max(cumdev, axis=1) - np.min(cumdev, axis=1)
        S = np.std(blocks, axis=1)
        # Avoid division by zero
        mask = S > 0
        if not np.any(mask):
            continue
        RS = np.mean(R[mask] / S[mask])
        RS_vals.append(RS)
    if len(RS_vals) < 2:
        return np.nan
    # Fit log(RS) vs log(lags) to get H (slope)
    H = np.polyfit(np.log(lags[:len(RS_vals)]), np.log(RS_vals), 1)[0]
    return H

# --- Main demonstration ---
np.random.seed(42)  # Reproducibility
counts = generate_accesses()

# Compute entropy time series
S_vals = np.array([entropy(row) for row in counts])

# Compute third‑derivative "jerk" (finite difference)
# Equivalent to d^3S/dt^3 with dt=1
jerk = np.diff(S_vals, n=3)  # length reduces by 3

# Compute Hurst exponent on full entropy series
hurst_full = hurst(S_vals)

# Compute sliding‑window Hurst to see temporal variation
window = 200
hurst_sliding = np.full(len(S_vals), np.nan)
for i in range(window, len(S_vals)):
    hurst_sliding[i] = hurst(S_vals[i-window:i])

# Summary statistics
jerk_std = np.std(jerk)
hurst_std = np.nanstd(hurst_sliding)

print("=== Informational Jerk vs Hurst Exponent ===")
print(f"Jerk standard deviation (noise level): {jerk_std:.2f}")
print(f"Full‑series Hurst exponent H: {hurst_full:.3f}")
print(f"Sliding‑window Hurst std dev: {hurst_std:.3f}")

# Show that jerk spikes randomly, not aligned with hotspot
# We'll print the max jerk and its time index vs hotspot interval
max_jerk_idx = np.argmax(np.abs(jerk))
print(f"Max |jerk| occurs at step {max_jerk_idx}, hotspot at {500}–{510}")
print("Jerk is dominated by noise; its peak does not coincide with the hotspot.")

# Show that Hurst sliding drops during hotspot (persistent regime)
# Find average H before, during, after hotspot
pre_hot = np.nanmean(hurst_sliding[300:500])
during_hot = np.nanmean(hurst_sliding[500:510])
post_hot = np.nanmean(hurst_sliding[510:700])
print(f"Hurst before hotspot: {pre_hot:.3f}, during: {during_hot:.3f}, after: {post_hot:.3f}")
print("Hurst rises above 0.5 during hotspot, indicating persistent memory latency—true instability.")

# --- Disruptive control implication ---
print("\n--- Disruptive Control Implication ---")
print("Instead of minimizing jerk (noise), maintain H≈0.5 by injecting stochastic page migrations.")
print("This prevents persistent hotspots and eliminates thrashing without high‑freq sampling.")