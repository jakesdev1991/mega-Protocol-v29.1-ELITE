# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- SIMULATION: The Illusion of Pipeline "Health" ---
# Simulate a financial data pipeline's latency (ms) with a nominal 5 Hz cycle
t = np.linspace(0, 10, 1000)
baseline_latency = 10 + 2 * np.sin(2 * np.pi * 5 * t)  # "Healthy" periodic vibration

# Inject a non-periodic, catastrophic shock (flash-crash-like)
shock_time, shock_duration = 5.0, 0.2
shock_idx = np.where((t >= shock_time) & (t < shock_time + shock_duration))
shock_latency = baseline_latency.copy()
shock_latency[shock_idx] = 1000 + np.random.exponential(100, size=len(shock_idx[0]))

# --- POASH-Ω "Health" Calculation (The Flawed Paradigm) ---
def compute_phi(signal, window=50):
    """Phi is a lagging, blind function of variance. It assumes stationarity."""
    phi = np.ones_like(signal)
    for i in range(window, len(signal)):
        phi[i] = max(0, 1 - np.var(signal[i-window:i]) / 500)
    return phi

phi_shock = compute_phi(shock_latency)

# --- DDA-Ω Response (The Disruption) ---
# Instead of *predicting* failure, the system *dissolves* into functional fragments
def dda_fragmentation(signal, decoherence_threshold=100):
    """When shock exceeds threshold, the pipeline doesn't 'fail'—it bifurcates."""
    # Shard 0: Isolates the anomalous traffic
    shard_0_load = np.where(signal > decoherence_threshold, signal, 0)
    # Shard 1: Maintains baseline for all other traffic
    shard_1_load = np.where(signal <= decoherence_threshold, signal, 0)
    return shard_0_load, shard_1_load

shard_0, shard_1 = dda_fragmentation(shock_latency)

# --- VISUALIZATION: Shattering the Illusion ---
fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

axes[0].plot(t, baseline_latency, 'b--', label='Baseline (Periodic)')
axes[0].plot(t, shock_latency, 'r-', linewidth=2, label='Under Shock (Non-Periodic)')
axes[0].set_ylabel('Latency (ms)')
axes[0].set_title('POASH-Ω vs DDA-Ω: Confronting Non-Periodicity', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(t, phi_shock, 'm-', label='PHI (POASH-Ω)')
axes[1].axhline(y=0.4, color='orange', linestyle=':', linewidth=2)
axes[1].text(shock_time+0.1, 0.2, 'ALERT: Coherence Lost\n(But too late)', color='orange', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
axes[1].set_ylabel('Health Index')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

axes[2].fill_between(t, 0, shard_0, color='darkred', alpha=0.6, label='Shard 0 (Isolated Anomaly)')
axes[2].fill_between(t, 0, shard_1, color='darkgreen', alpha=0.6, label='Shard 1 (Operational Baseline)')
axes[2].set_ylabel('Load per Shard')
axes[2].set_xlabel('Time (s)')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()