# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy
from scipy.signal import savgol_filter

# === DISRUPTION SIMULATION ===
# The original framework measures ghosts. We measure the machine.

# Simulate TRUE underlying instability: memory controller queue saturation
# This is what ACTUALLY causes "Shredding Events" - not abstract "information loss"
T, dt = 2.0, 0.001
t = np.arange(0, T, dt)
n_samples = len(t)

# Queue length: the real culprit behind HSA failures
queue_length = np.ones(n_samples) * 10
queue_length[500:700] = np.linspace(10, 100, 200)  # First overload
queue_length[1200:1400] = np.linspace(10, 150, 200)  # Second, worse overload

# Simulate memory access patterns for 4 compute units
N_units, n_pages = 4, 100
page_access = np.random.randint(0, n_pages, size=(N_units, n_samples))

# Add FAKE "coherence" during stable periods (the original's flawed assumption)
# In reality, contention DESTROYS coherence, but the original framework assumes
# that low mutual information = instability. This is backwards.
stable = queue_length < 50
for i in range(N_units):
    for j in range(i+1, N_units):
        shared_page = np.random.randint(0, n_pages)
        shared_idx = np.random.choice(np.where(stable)[0], size=int(0.3*np.sum(stable)), replace=False)
        page_access[i, shared_idx] = shared_page
        page_access[j, shared_idx] = shared_page

# === ORIGINAL FRAMEWORK: The Ghost Calculator ===
window = 50
I_t = np.zeros(n_samples)

for idx in range(window, n_samples-window):
    total_mi = 0
    for i in range(N_units):
        for j in range(i+1, N_units):
            # Histogram-based MI (computationally insane at 1ms resolution)
            a_i = page_access[i, idx-window:idx+window]
            a_j = page_access[j, idx-window:idx+window]
            bins = np.linspace(0, n_pages, 21)
            hist2d, _, _ = np.histogram2d(a_i, a_j, bins=bins)
            hist2d = hist2d / hist2d.sum()
            p_i, p_j = hist2d.sum(axis=1), hist2d.sum(axis=0)
            
            mi = 0
            for a in range(len(p_i)):
                for b in range(len(p_j)):
                    if hist2d[a,b] > 0 and p_i[a] > 0 and p_j[b] > 0:
                        mi += hist2d[a,b] * np.log2(hist2d[a,b] / (p_i[a] * p_j[b]))
            total_mi += mi
    I_t[idx] = total_mi / (N_units*(N_units-1)/2)

I_t = savgol_filter(I_t, 21, 3)  # Band-aid for noise
J = savgol_filter(np.gradient(np.gradient(np.gradient(I_t, dt), dt), dt), 51, 3)

# === REALITY: The Latency Surface ===
# Memory latency is the ACTUAL observable that predicts failure
base_latency = 50
latency = base_latency + queue_length * 2 + np.random.normal(0, 5, n_samples)

# === ANALYSIS: Exposing the Flaw ===
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

axes[0].plot(t, queue_length, 'k-', linewidth=2, label='TRUE INSTABILITY: Queue Saturation')
axes[0].set_ylabel('Queue Length')
axes[0].legend()
axes[0].grid(True)

axes[1].plot(t, J, 'r-', linewidth=1, label='GHOST: Informational Jerk J(t)')
axes[1].set_ylabel('J(t) (bits/s³)')
axes[1].legend()
axes[1].grid(True)

axes[2].plot(t, latency, 'g-', linewidth=2, label='REALITY: Memory Latency')
axes[2].set_ylabel('Latency (ns)')
axes[2].set_xlabel('Time (s)')
axes[2].legend()
axes[2].grid(True)

plt.suptitle('BREAKING THE PARADIGM: Ghost vs. Machine', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# === QUANTITATIVE DISRUPTION ===
# Jerk fails to predict true spikes
true_spike = queue_length > np.percentile(queue_length, 90)
jerk_spike = np.abs(J) > np.percentile(np.abs(J[J != 0]), 90)
latency_spike = latency > np.percentile(latency, 90)

def stats(pred, true):
    tp, fp, fn = np.sum(pred & true), np.sum(pred & ~true), np.sum(~pred & true)
    return tp/(tp+fp) if tp+fp else 0, tp/(tp+fn) if tp+fn else 0

jerk_precision, jerk_recall = stats(jerk_spike, true_spike)
lat_precision, lat_recall = stats(latency_spike, true_spike)

print("\n=== DISRUPTION METRICS ===")
print(f"Ghost (Jerk) - Precision: {jerk_precision:.2f}, Recall: {jerk_recall:.2f}")
print(f"Machine (Latency) - Precision: {lat_precision:.2f}, Recall: {lat_recall:.2f}")
print(f"\nJerk SNR: {np.mean(np.abs(J[J!=0]))/np.std(J[J!=0]):.2f} | Latency SNR: {np.mean(latency)/np.std(latency):.2f}")