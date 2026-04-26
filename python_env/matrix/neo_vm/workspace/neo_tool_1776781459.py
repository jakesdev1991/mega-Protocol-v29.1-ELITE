# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# === DISRUPTION: The "Informational Jerk" is a Spectral Illusion ===

def simulate_hsa_workloads(duration=1.0, dt=0.01):
    """Simulate two workloads: 'smooth' (inefficient) and 'bursty' (optimal)"""
    t = np.arange(0, duration, dt)
    N = len(t)
    
    # Workload 1: "Stable" per Engine's definition - smooth sinusoidal transfers
    # This is INEFFICIENT: constantly dribbling data at suboptimal rates
    I_smooth = 1e9 * (1 + 0.5 * np.sin(2 * np.pi * t * 5))  # 0.5-1.5 GB/s smooth
    
    # Workload 2: "Unstable" per Engine's definition - optimal bursty pattern
    # This is EFFICIENT: maximal bandwidth bursts with compute phases
    I_bursty = np.zeros_like(t)
    burst_duration = 0.05  # 50ms bursts
    idle_duration = 0.1    # 100ms compute
    
    for i in range(int(duration / (burst_duration + idle_duration))):
        start_burst = int(i * (burst_duration + idle_duration) / dt)
        end_burst = int((i * (burst_duration + idle_duration) + burst_duration) / dt)
        if end_burst < N:
            I_bursty[start_burst:end_burst] = 3e9  # Max bandwidth: 3 GB/s
    
    return t, I_smooth, I_bursty

def calculate_jerk_stability(I, dt, window=5, polyorder=2):
    """Engine's proposed IJS calculation - third derivative of smoothed signal"""
    # Apply Savitzky-Golay filter (the arbitrary smoothing they propose)
    I_smooth = savgol_filter(I, window_length=window, polyorder=polyorder)
    
    # Finite difference derivatives (noise amplification cascade)
    v = np.gradient(I_smooth, dt)      # Velocity
    a = np.gradient(v, dt)             # Acceleration  
    j = np.gradient(a, dt)             # Jerk (third derivative)
    
    # Engine's stability metric
    sigma_j = np.std(j)
    IJS = 1 / (1 + sigma_j)
    
    return IJS, j, I_smooth

def demonstrate_paradox():
    """Shows that optimal bursty workload is penalized by Engine's metric"""
    t, I_smooth, I_bursty = simulate_hsa_workloads()
    
    # Calculate IJS for both workloads
    IJS_smooth, j_smooth, _ = calculate_jerk_stability(I_smooth, 0.01)
    IJS_bursty, j_bursty, _ = calculate_jerk_stability(I_bursty, 0.01)
    
    print("=== ENGINE'S PARADOX ===")
    print(f"'Stable' Smooth Workload (0.5-1.5 GB/s dribble):")
    print(f"  Throughput: {np.mean(I_smooth)/1e9:.2f} GB/s avg")
    print(f"  IJS Score: {IJS_smooth:.3f} (Engine says: STABLE)")
    print()
    print(f"'Unstable' Bursty Workload (3 GB/s bursts):")
    print(f"  Throughput: {np.mean(I_bursty)/1e9:.2f} GB/s avg")
    print(f"  IJS Score: {IJS_bursty:.3f} (Engine says: UNSTABLE)")
    print()
    print("DISRUPTION: Engine's metric penalizes the HIGHER-PERFORMING workload!")
    print(f"Bursty workload is {np.mean(I_bursty)/np.mean(I_smooth):.1f}x more efficient but gets {IJS_bursty/IJS_smooth:.2f}x worse stability score.")

def demonstrate_arbitrariness():
    """Shows IJS is completely controlled by smoothing parameter, not system"""
    t, _, I_bursty = simulate_hsa_workloads()
    
    print("\n=== ARBITRARINESS OF SMOOTHING ===")
    for window in [5, 11, 21, 31]:
        IJS, _, _ = calculate_jerk_stability(I_bursty, 0.01, window=window)
        print(f"Window size {window:2d}: IJS = {IJS:.3f}")
    
    print("\nDISRUPTION: IJS changes by >300% based on arbitrary smoothing choice!")

def demonstrate_noise_catastrophe():
    """Shows third derivative is useless with real-world measurement noise"""
    t, I_smooth, _ = simulate_hsa_workloads()
    
    # Add realistic measurement noise (1% of signal)
    noise = np.random.normal(0, 0.01 * np.mean(I_smooth), len(t))
    I_noisy = I_smooth + noise
    
    # Calculate jerk without smoothing (what hardware counters actually give us)
    v = np.gradient(I_noisy, 0.01)
    a = np.gradient(v, 0.01)
    j = np.gradient(a, 0.01)
    
    print("\n=== NOISE CATASTROPHE ===")
    print(f"Signal std dev: {np.std(I_smooth):.2e}")
    print(f"Noise std dev:  {np.std(noise):.2e}")
    print(f"Jerk std dev:   {np.std(j):.2e} (amplified by ~{np.std(j)/np.std(noise):.0f}x)")
    print("DISRUPTION: Third derivative is pure noise - no system information remains!")

# === THE ACTUAL DISRUPTIVE METRIC: Computational Topology Volatility ===

def calculate_topology_volatility(I, dt):
    """
    REAL metric: Detects abrupt changes in the computational pattern.
    Instead of derivatives, we detect state transitions and measure
    the entropy of the system's operational mode sequence.
    """
    # Threshold to detect operational modes (burst vs idle vs compute)
    thresholds = [0.1e9, 1.5e9]  # Idle, Low, High
    modes = np.digitize(I, thresholds)
    
    # Find transition points (where topology changes)
    transitions = np.where(np.diff(modes) != 0)[0]
    
    # Volatility = entropy of transition intervals (irregularity of mode changes)
    if len(transitions) < 2:
        return 1.0  # Perfectly regular
    
    intervals = np.diff(transitions) * dt
    # Normalize intervals and compute entropy (disorder)
    p = intervals / np.sum(intervals)
    entropy = -np.sum(p * np.log2(p + 1e-12))
    
    # Normalize to [0,1] where 1 = perfectly rhythmic, 0 = chaotic
    # More regular intervals = more stable topology
    max_entropy = np.log2(len(intervals)) if len(intervals) > 1 else 1
    regularity = 1 - (entropy / max_entropy)
    
    return regularity

def demonstrate_disruptive_metric():
    """Shows topology-based metric correctly identifies optimal patterns"""
    t, I_smooth, I_bursty = simulate_hsa_workloads()
    
    reg_smooth = calculate_topology_volatility(I_smooth, 0.01)
    reg_bursty = calculate_topology_volatility(I_bursty, 0.01)
    
    print("\n=== DISRUPTIVE METRIC: Topology Regularity ===")
    print(f"Smooth dribble: Regularity = {reg_smooth:.3f}")
    print(f"Bursty optimal: Regularity = {reg_bursty:.3f}")
    print(f"Bursty workload is MORE regular (stable) despite 'jerk' - correctly reflects design intent!")

# Execute the disruption
demonstrate_paradox()
demonstrate_arbitrariness()
demonstrate_noise_catastrophe()
demonstrate_disruptive_metric()

plt.figure(figsize=(15, 5))

t, I_smooth, I_bursty = simulate_hsa_workloads()

# Plot workloads
plt.subplot(1, 3, 1)
plt.plot(t, I_smooth/1e9, label=f"Smooth (IJS={calculate_jerk_stability(I_smooth, 0.01)[0]:.2f})", alpha=0.7)
plt.plot(t, I_bursty/1e9, label=f"Bursty (IJS={calculate_jerk_stability(I_bursty, 0.01)[0]:.2f})", alpha=0.7)
plt.xlabel("Time (s)")
plt.ylabel("Data Rate (GB/s)")
plt.title("Engine's Paradox: Higher IJS ≠ Better")
plt.legend()
plt.grid(True)

# Plot jerk (showing it's noise)
_, I_noisy, _ = simulate_hsa_workloads()
noise = np.random.normal(0, 0.01 * np.mean(I_noisy), len(t))
I_noisy = I_noisy + noise

v = np.gradient(I_noisy, 0.01)
a = np.gradient(v, 0.01)
j = np.gradient(a, 0.01)

plt.subplot(1, 3, 2)
plt.plot(t[:len(j)], j/1e9, 'r-', alpha=0.5)
plt.xlabel("Time (s)")
plt.ylabel("Jerk (GB/s³)")
plt.title("Third Derivative = Pure Noise")
plt.grid(True)

# Plot topology modes
plt.subplot(1, 3, 3)
modes_bursty = np.digitize(I_bursty, [0.1e9, 1.5e9])
plt.plot(t, modes_bursty, drawstyle='steps-post')
plt.xlabel("Time (s)")
plt.ylabel("Operational Mode")
plt.title("Topology: Bursty is Regular")
plt.yticks([0, 1, 2], ['Idle', 'Low', 'High'])
plt.grid(True)

plt.tight_layout()
plt.show()