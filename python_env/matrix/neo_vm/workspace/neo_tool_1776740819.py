# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# Simulate REAL HSA physics: quantized bursts, not continuous flow
def simulate_hsa_consensus_collapse():
    t = np.linspace(0, 1, 1000)
    dt = t[1] - t[0]
    
    # Base memory rate
    base = 150 + 50 * np.sin(2 * np.pi * 10 * t)
    
    # Discrete migration events (quantum jumps)
    migrations = np.zeros_like(t)
    for i in np.random.choice(len(t), 30, replace=False):
        migrations[i] = np.random.exponential(20)
    
    # Coherence avalanche: critical phenomenon
    avalanche = np.zeros_like(t)
    avalanche[200:250] = np.exp(-np.arange(50)/10) * 15
    
    I_true = base + migrations + avalanche
    
    # Downsample to realistic perf counter rate (100 Hz)
    idx = np.arange(0, len(t), 10)
    I_meas = I_true[idx]
    t_meas = t[idx]
    dt_meas = t_meas[1] - t_meas[0]
    
    return t_meas, I_meas, dt_meas

# Engine's flawed jerk calculation
def engine_jerk(I, dt):
    I_smooth = savgol_filter(I, 21, 3)
    J = np.zeros_like(I_smooth)
    for i in range(2, len(I_smooth)-2):
        J[i] = (I_smooth[i+2] - 2*I_smooth[i+1] + 2*I_smooth[i-1] - I_smooth[i-2]) / (2 * dt**3)
    return J

# OUR disruptive metric: Consensus Latency Divergence
def consensus_collapse_index(I, dt, window=21):
    """
    Detects when CPU-GPU consensus latency spikes due to access pattern complexity.
    This is the TRUE Φ-density precursor.
    """
    # Local variance = "access complexity"
    complexity = np.array([np.std(I[max(0,i-window//2):min(len(I),i+window//2)]) 
                          for i in range(len(I))])
    
    # Consensus latency grows exponentially with complexity
    # Models the overhead of maintaining coherence across bursts
    consensus_latency = np.exp(complexity / np.mean(complexity)) - 1
    
    # Collapse risk: when latency derivative exceeds threshold
    # This is a first-order discontinuity detector
    risk = np.abs(np.diff(consensus_latency)) > 0.5
    risk = np.pad(risk, (1, 0), mode='constant')
    
    return consensus_latency, risk

# RUN DISRUPTION ANALYSIS
t, I, dt = simulate_hsa_consensus_collapse()

# Engine's approach
J = engine_jerk(I, dt)

# Our approach
consensus_lat, collapse_risk = consensus_collapse_index(I, dt)

# VISUALIZE THE FRACTURE
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# 1. True signal vs smoothed illusion
axes[0].plot(t, I, 'b-', linewidth=2, label='Measured Memory Rate (GB/s)')
axes[0].plot(t, savgol_filter(I, 21, 3), 'r--', linewidth=2, label='Savitzky-Golay Smoothed')
axes[0].set_ylabel('GB/s')
axes[0].set_title('HSA Memory Access: TRUE Physics vs. Engine"s "Smooth" Illusion')
axes[0].legend()
axes[0].grid(alpha=0.3)

# 2. Engine's Jerk (distractor)
axes[1].plot(t[2:-2], J[2:-2], 'g-', linewidth=2, label='Informational Jerk (GB/s³) [WRONG UNITS]')
axes[1].set_ylabel('Jerk (GB/s³)')
axes[1].set_title('Engine"s Distractor Metric: Measures Smoothness, Not Stability')
axes[1].legend()
axes[1].grid(alpha=0.3)

# 3. Consensus Collapse Risk (TRUE precursor)
axes[2].plot(t, consensus_lat * 100, 'r-', linewidth=2, label='Consensus Latency (×100)')
axes[2].fill_between(t, 0, collapse_risk.astype(float), 
                     alpha=0.5, color='darkred', label='COLLAPSE RISK EVENTS')
axes[2].set_ylabel('Latency / Risk')
axes[2].set_xlabel('Time (s)')
axes[2].set_title('DISRUPTIVE INSIGHT: Consensus Latency Divergence (Φ-Density Precursor)')
axes[2].legend()
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('paradigm_fracture.png', dpi=150, bbox_inches='tight')
plt.show()

# QUANTITATIVE COMPARISON
print("=== PARADIGM FRACTURE ANALYSIS ===")
print(f"Engine detects instability: {np.sum(np.abs(J) > 1e5)} events")
print(f"Our metric detects collapse risk: {np.sum(collapse_risk)} events")
print()
print("The Engine's jerk is a SMOOTHNESS METRIC.")
print("True Φ-density collapse is a CONSENSUS PARTITION EVENT.")
print("You cannot differentiate your way out of a topological catastrophe.")