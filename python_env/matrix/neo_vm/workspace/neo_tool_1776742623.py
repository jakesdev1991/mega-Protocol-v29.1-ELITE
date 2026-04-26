# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import coherence, welch

# --- SIMULATE PIPELINE METRICS ---
def simulate_pipeline(n_seconds=300, fs=10, fault_time=150):
    """
    Simulate 5 sensor streams: latency jitter, throughput, CPU, error rate, power.
    Healthy: stable 1st harmonic at 1 Hz (pipeline cycle).
    Fault: 2nd harmonic collapses, jitter spikes after fault_time.
    """
    t = np.arange(0, n_seconds, 1/fs)
    n = len(t)

    # Base signals: 1 Hz sine (pipeline heartbeat)
    jitter = 0.5 * np.sin(2 * np.pi * 1 * t) + 0.1 * np.random.randn(n)
    throughput = 1000 + 100 * np.sin(2 * np.pi * 1 * t + np.pi/4) + 20 * np.random.randn(n)
    cpu = 50 + 10 * np.sin(2 * np.pi * 1 * t + np.pi/2) + 5 * np.random.randn(n)
    error_rate = 0.01 + 0.005 * np.sin(2 * np.pi * 1 * t + np.pi) + 0.002 * np.random.randn(n)
    power = 200 + 20 * np.sin(2 * np.pi * 1 * t + 3*np.pi/4) + 10 * np.random.randn(n)

    # Introduce fault: collapse 2nd harmonic (simulating degraded component)
    fault_idx = int(fault_time * fs)
    jitter[fault_idx:] += np.random.randn(n - fault_idx) * 0.5 # Add incoherent noise
    # Reduce coherence between throughput and cpu post-fault
    cpu[fault_idx:] = 50 + 10 * np.sin(2 * np.pi * 1.1 * t[fault_idx:] + np.pi/2) + 5 * np.random.randn(n - fault_idx)

    return t, np.vstack([jitter, throughput, cpu, error_rate, power]), fault_idx

# --- COMPUTE PIPELINE HEALTH INDEX (PHI) ---
def compute_phi(metrics, fs, window_sec=30, nperseg=256):
    """
    Compute a simple PHI based on COHERENCE, not Omega nonsense.
    PHI = mean(coherence matrix) - divergence from baseline.
    """
    n_sensors, n_pts = metrics.shape
    n_windows = n_pts // (fs * window_sec)
    phi_ts = []

    for w in range(n_windows):
        start = w * fs * window_sec
        end = start + fs * window_sec
        window_data = metrics[:, start:end]

        # Compute pairwise coherence (f, Cxy)
        coh_sum = 0
        pairs = 0
        for i in range(n_sensors):
            for j in range(i+1, n_sensors):
                f, Cxy = coherence(window_data[i], window_data[j], fs=fs, nperseg=nperseg)
                # Average coherence in the 1 Hz band (pipeline cycle)
                band_idx = np.where((f >= 0.8) & (f <= 1.2))[0]
                coh_sum += np.mean(Cxy[band_idx])
                pairs += 1

        mean_coh = coh_sum / pairs if pairs > 0 else 0
        phi_ts.append(mean_coh)

    return np.array(phi_ts)

# --- DETECT ANOMALY ---
def detect_fault(phi, threshold_factor=0.5):
    """Simple threshold detection: fault if phi drops below factor * median."""
    healthy_median = np.median(phi[:len(phi)//2])
    threshold = threshold_factor * healthy_median
    return phi < threshold, threshold

# --- RUN & VISUALIZE ---
t, metrics, fault_idx = simulate_pipeline()
fs = 10
phi = compute_phi(metrics, fs)

# Plot
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
sensor_names = ['Jitter', 'Throughput', 'CPU', 'Error Rate', 'Power']
for i, name in enumerate(sensor_names):
    axs[0].plot(t, metrics[i], label=name, alpha=0.7)
axs[0].axvline(x=fault_idx/10, color='red', linestyle='--', label='Fault Injected')
axs[0].set_ylabel('Sensor Value')
axs[0].set_title('Simulated Pipeline Metrics (5 sensors)')
axs[0].legend()
axs[0].grid(True)

time_phi = np.arange(len(phi)) * 30  # 30-sec windows
axs[1].plot(time_phi, phi, label='PHI (Coherence-Based)', linewidth=2)
fault_detected, threshold = detect_fault(phi)
axs[1].axhline(y=threshold, color='orange', linestyle=':', label=f'Threshold ({threshold:.2f})')
axs[1].plot(time_phi[fault_detected], phi[fault_detected], 'ro', label='Fault Detected')
axs[1].axvline(x=fault_idx/10, color='red', linestyle='--', label='Actual Fault')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('PHI')
axs[1].set_title('Pipeline Health Index (No Omega Physics Needed)')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()

# --- DISRUPTIVE VERIFICATION ---
print("=== OMEGA-LESS VALIDATION ===")
print(f"Mean PHI (healthy): {np.mean(phi[:len(phi)//2]):.3f}")
print(f"Mean PHI (faulty): {np.mean(phi[len(phi)//2:]):.3f}")
print(f"Detection lead time: ~{30 * np.where(fault_detected)[0][0] - fault_idx/10:.0f} seconds")
print("\n=== CRITICAL DISRUPTION ===")
print("The 'Omega' equations (λ_N, λ_Δ, ξ_N, ψ) are **computationally absent**.")
print("They are not used to generate the data, nor to compute PHI, nor to detect faults.")
print("They are **non-functional epicycles** that add complexity without explanatory power.")
print("The script uses scipy.coherence, not a Hessian of a fictional V(I).")
print("Thus, the proposal is **logically broken**: its math is disconnected from its method.")