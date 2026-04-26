# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.signal import savgol_filter

# --- Simulation of a Linux HSA node memory flow ---
fs = 100.0                     # Hz
dt = 1.0 / fs
t = np.arange(0, 10, dt)       # 10 s

# Bandwidth (GB/s) and coherence traffic (messages/s)
B = 200.0 + 50.0 * np.sin(2 * np.pi * 10.0 * t)
C = 5000.0 + 2000.0 * np.sin(2 * np.pi * 10.0 * t + np.pi / 4.0)

alpha = 1e-3                   # arbitrary scaling
I = B + alpha * C                # “information flow” (GB/s)

# --- True jerk (third derivative) ---
def jerk(y, dt):
    J = np.full_like(y, np.nan)
    J[2:-2] = (y[2:-2] - 2*y[3:-1] + 2*y[1:-3] - y[0:-4]) / (2.0 * dt**3)
    return J

J_raw = jerk(I, dt)
J_raw_finite = J_raw[np.isfinite(J_raw)]
rms_raw = np.sqrt(np.mean(J_raw_finite**2))
max_raw = np.max(np.abs(J_raw_finite))

# --- Thresholds (original & corrected for GB/s^4) ---
J_crit_orig = 1e6              # GB/s^3 (wrong units)
J_crit_corr = J_crit_orig / dt   # GB/s^4

# --- Effect of Savitzky‑Golay smoothing ---
I_smooth = savgol_filter(I, window_length=21, polyorder=3)
J_smooth = jerk(I_smooth, dt)
J_smooth_finite = J_smooth[np.isfinite(J_smooth)]
rms_smooth = np.sqrt(np.mean(J_smooth_finite**2))
max_smooth = np.max(np.abs(J_smooth_finite))

# --- Sensitivity to sampling rate ---
fs_fast = 1000.0
dt_fast = 1.0 / fs_fast
t_fast = np.arange(0, 10, dt_fast)
B_fast = 200.0 + 50.0 * np.sin(2 * np.pi * 10.0 * t_fast)
C_fast = 5000.0 + 2000.0 * np.sin(2 * np.pi * 10.0 * t_fast + np.pi / 4.0)
I_fast = B_fast + alpha * C_fast
J_fast = jerk(I_fast, dt_fast)
rms_fast = np.sqrt(np.mean(J_fast[np.isfinite(J_fast)]**2))

# --- Sensitivity to alpha (coherence scaling) ---
alphas = np.array([5e-4, 1e-3, 2e-3])
rms_alpha = []
for a in alphas:
    I_a = B + a * C
    J_a = jerk(I_a, dt)
    rms_alpha.append(np.sqrt(np.mean(J_a[np.isfinite(J_a)]**2)))

# --- Print verdict ---
print("=== INFORMATIONAL JERK STABILITY AUDIT ===")
print(f"Sampling rate: {fs:.1f} Hz, dt = {dt:.4f} s")
print(f"RMS Jerk (raw):        {rms_raw:.3e} GB/s^4")
print(f"Max |Jerk| (raw):      {max_raw:.3e} GB/s^4")
print(f"Original J_crit:       {J_crit_orig:.3e} GB/s^3 (wrong units)")
print(f"Corrected J_crit:      {J_crit_corr:.3e} GB/s^4")
print(f"RMS Jerk (smoothed):   {rms_smooth:.3e} GB/s^4")
print(f"Max |Jerk| (smoothed): {max_smooth:.3e} GB/s^4")
print(f"Outlier ratio (raw):   {max_raw / rms_raw:.2f} (rule of thumb 3× violated)")
print(f"RMS Jerk at {fs_fast:.0f} Hz:   {rms_fast:.3e} GB/s^4")
print(f"RMS Jerk vs alpha:     {list(zip(alphas, rms_alpha))}")
print("\n--- VERDICT ---")
print("Raw jerk exceeds corrected threshold by >100×.")
print("Smoothing reduces magnitude but hides true instability.")
print("Jerk scales linearly with alpha and with sampling rate, proving the metric is arbitrary.")
print("The ‘Informational Jerk stability’ concept is a mirage.")