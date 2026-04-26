# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import find_peaks

# Simulate a catastrophic coherence collapse scenario
t = np.linspace(0, 10, 10000)  # Real time
Phi_0 = 1.0

# Model: Stable plateau, then sudden exponential collapse
Phi_N = np.ones_like(t) * Phi_0
collapse_start_idx = len(t) // 2
t_collapse = 0.5  # Collapse time constant
Phi_N[collapse_start_idx:] = Phi_0 * np.exp(-(t[collapse_start_idx:] - t[collapse_start_idx]) / t_collapse)

# Compute intrinsic time tau(t) = integral of Phi_N(t)/Phi_0 dt
dtaudt = Phi_N / Phi_0
tau = np.cumsum(dtaudt) * (t[1] - t[0])  # Approximate integral

# Compute jerks
# Real-time jerk: d^3 Phi_N / dt^3
dPhi_dt = np.gradient(Phi_N, t)
d2Phi_dt2 = np.gradient(dPhi_dt, t)
j_real = np.gradient(d2Phi_dt2, t)

# Tau-time jerk: d^3 Phi_N / d tau^3
# We need d/dtau = (dt/dtau) * d/dt = (1 / (dtaudt)) * d/dt
# So j_tau = (1/dtaudt) * d/dt [ (1/dtaudt) * d/dt [ (1/dtaudt) * dPhi_dt ] ]

inv_dtaudt = 1.0 / dtaudt
dPhi_dtau = inv_dtaudt * dPhi_dt
d2Phi_dtau2 = inv_dtaudt * np.gradient(dPhi_dtau, t)
j_tau = inv_dtaudt * np.gradient(d2Phi_dtau2, t)

# Find peaks of jerk magnitude (instability events)
peaks_real, _ = find_peaks(np.abs(j_real))
peaks_tau, _ = find_peaks(np.abs(j_tau))

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)

# Plot 1: Coherence and Time Dilation
ax1 = axes[0]
ax1.plot(t, Phi_N, 'k-', label='Φ_N(t) (Consensus)', linewidth=2)
ax1.set_ylabel('Φ_N / Φ_0', fontsize=11)
ax1.set_xlabel('Real Time t', fontsize=11)
ax1.set_title('Catastrophic Coherence Collapse & Temporal Illusion', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right')

ax1_twin = ax1.twinx()
ax1_twin.plot(t, dtaudt, 'r--', label='dτ/dt = Φ_N/Φ_0', linewidth=1.5)
ax1_twin.set_ylabel('dτ/dt (Time Dilation Factor)', color='r', fontsize=11)
ax1_twin.tick_params(axis='y', labelcolor='r')
ax1_twin.legend(loc='lower left')

# Plot 2: Real vs Tau Jerk
ax2 = axes[1]
ax2.plot(t, j_real, 'b-', label='j_real(t) = d³Φ_N/dt³', linewidth=2)
ax2.plot(t, j_tau, 'g--', label='j_τ(t) = d³Φ_N/dτ³', linewidth=2)
ax2.axvline(t[collapse_start_idx], color='gray', linestyle=':', label='Collapse Onset')
if len(peaks_real) > 0:
    ax2.axvline(t[peaks_real[0]], color='b', linestyle=':', alpha=0.5)
if len(peaks_tau) > 0:
    ax2.axvline(t[peaks_tau[0]], color='g', linestyle=':', alpha=0.5)
ax2.set_ylabel('Jerk Magnitude', fontsize=11)
ax2.set_xlabel('Real Time t', fontsize=11)
ax2.set_title('Observer Blindness: Tau-Time Jerk is Delayed & Attenuated', fontsize=12)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: The Lethal Stability Metric S_j
# Simulate S_j = (1 + |κ|)^-1 where κ is excess kurtosis of j_tau over a sliding window
window_size = 500  # 50ms window at 10kHz equivalent
S_j = np.zeros_like(t)
for i in range(window_size, len(t)):
    window = j_tau[i-window_size:i]
    if np.std(window) < 1e-9:  # Constant jerk case
        kurt = -3.0  # Excess kurtosis for constant
    else:
        kurt = (np.mean((window - np.mean(window))**4) / (np.std(window)**4 + 1e-12)) - 3
    S_j[i] = 1.0 / (1 + abs(kurt))

ax3 = axes[2]
ax3.plot(t, S_j, 'm-', label='S_j(t) (Flawed Stability Metric)', linewidth=2)
ax3.axhline(0.7, color='r', linestyle='--', label='Trigger Threshold = 0.7')
ax3.axhline(0.25, color='orange', linestyle='--', label='Asymptotic Floor (S_j→0.25)')
ax3.axvline(t[collapse_start_idx], color='gray', linestyle=':', label='Real Collapse Onset')
ax3.fill_between(t, 0.7, 1.0, alpha=0.2, color='green', label='Perceived "Safe" Zone')
ax3.fill_between(t, 0.25, 0.7, alpha=0.2, color='red', label='Perceived "Unstable" Zone')
ax3.set_ylabel('Stability Metric S_j', fontsize=11)
ax3.set_xlabel('Real Time t', fontsize=11)
ax3.set_title('The Death Spiral: Collapse → Time Dilation → False Stability → No Action', fontsize=12, fontweight='bold')
ax3.legend(loc='lower right')
ax3.grid(True, alpha=0.3)
ax3.set_ylim([0, 1.1])

plt.tight_layout()
plt.show()

# Quantify the illusion
if len(peaks_real) > 0 and len(peaks_tau) > 0:
    real_peak_time = t[peaks_real[0]]
    tau_peak_time = t[peaks_tau[0]]
    delay = tau_peak_time - real_peak_time
    attenuation = np.abs(j_tau[peaks_tau[0]]) / np.abs(j_real[peaks_real[0]])
    print(f"--- DISRUPTIVE METRICS ---")
    print(f"Peak Jerk Detection Delay (τ-time lag): {delay:.3f}s")
    print(f"Peak Jerk Attenuation Factor: {attenuation:.3f}x")
    print(f"At collapse onset, dτ/dt = {dtaudt[collapse_start_idx]:.3f} (time slows {1/dtaudt[collapse_start_idx]:.1f}x)")
    print(f"S_j at real collapse onset: {S_j[collapse_start_idx]:.3f} (reads as {'SAFE' if S_j[collapse_start_idx] > 0.7 else 'UNSTABLE'})")
    print(f"S_j at τ-time 'detected' collapse: {S_j[peaks_tau[0]] if len(peaks_tau)>0 else 'N/A'}")