# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validate Informational Jerk stability for an HSA node
as described in Agent Smith's analysis.
"""

import numpy as np
from scipy.signal import savgol_filter

# ----------------------------------------------------------------------
# Parameters (matching the agent's description)
# ----------------------------------------------------------------------
Fs = 100.0               # sampling frequency [Hz]
dt = 1.0 / Fs            # sampling period [s]
T  = 30.0                # total simulation time [s]
N  = int(T * Fs)         # number of samples

# Synthetic I(t): bandwidth oscillates 150‑250 GB/s at 10 Hz
# plus a small coherence term (scaled by alpha) to mimic the metric.
t = np.arange(N) * dt
B = 200.0 + 50.0 * np.sin(2 * np.pi * 10.0 * t)   # GB/s
alpha = 1e-3                                        # scale coherence to GB/s
C = 2000.0 * np.sin(2 * np.pi * 10.0 * t)         # arbitrary coherence traffic [msg/s]
I = B + alpha * C                                   # GB/s (effective information flow)

# ----------------------------------------------------------------------
# Step 1 – Smoothing (Savitzky‑Golay, window=21, order=3)
# ----------------------------------------------------------------------
window_length = 21
polyorder = 3
I_smooth = savgol_filter(I, window_length, polyorder, mode='interp')

# ----------------------------------------------------------------------
# Step 2 – Derivatives using the stencils from the analysis
# ----------------------------------------------------------------------
# Velocity (first derivative) – central difference
v = np.empty_like(I_smooth)
v[1:-1] = (I_smooth[2:] - I_smooth[:-2]) / (2 * dt)
# forward/backward differences at boundaries (not used for jerk interior)
v[0]    = (I_smooth[1] - I_smooth[0]) / dt
v[-1]   = (I_smooth[-1] - I_smooth[-2]) / dt

# Acceleration (second derivative) – central difference
a = np.empty_like(I_smooth)
a[2:-2] = (I_smooth[4:] - 2*I_smooth[3:-1] + I_smooth[:-4]) / (dt**2)
# simple forward/backward for edges (again, not needed for jerk interior)
a[0] = (I_smooth[2] - 2*I_smooth[1] + I_smooth[0]) / (dt**2)
a[1] = (I_smooth[3] - 2*I_smooth[2] + I_smooth[1]) / (dt**2)
a[-2] = (I_smooth[-1] - 2*I_smooth[-2] + I_smooth[-3]) / (dt**2)
a[-1] = (I_smooth[-1] - 2*I_smooth[-2] + I_smooth[-3]) / (dt**2)

# Jerk (third derivative) – fourth‑point stencil
j = np.empty_like(I_smooth)
# valid indices: 2 .. N-3 (inclusive)
j[2:-2] = (I_smooth[4:] - 2*I_smooth[3:-1] + 2*I_smooth[1:-3] - I_smooth[:-4]) / (2 * dt**3)
# fill edges with NaN so they are ignored in statistics
j[:2] = np.nan
j[-2:] = np.nan

# ----------------------------------------------------------------------
# Step 3 – Stability metrics
# ----------------------------------------------------------------------
# Remove NaNs for RMS/max calculations
j_valid = j[~np.isnan(j)]
rms_jerk = np.sqrt(np.mean(j_valid**2))
max_jerk = np.max(np.abs(j_valid))

# Criteria from the agent
J_crit = 1e6                     # GB/s^3
criterion1 = rms_jerk < J_crit
criterion2 = max_jerk < 3 * rms_jerk
# Spectral sanity: check that no frequency bin above Nyquist/2 exceeds
# 5× the median power (a simple proxy for "no growing peaks")
freqs = np.fft.rfftfreq(len(j_valid), d=dt)
psd   = np.abs(np.fft.rfft(j_valid))**2
median_psd = np.median(psd)
criterion3 = np.all(psd[freqs > 0] < 5 * median_psd)  # ignore DC

# ----------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------
print("=== Informational Jerk Stability Check ===")
print(f"RMS Jerk          : {rms_jerk:.3e} GB/s^3")
print(f"Max |Jerk|        : {max_jerk:.3e} GB/s^3")
print(f"J_crit (threshold): {J_crit:.3e} GB/s^3")
print(f"Criterion 1 (RMS < J_crit)        : {'PASS' if criterion1 else 'FAIL'}")
print(f"Criterion 2 (max < 3*RMS)         : {'PASS' if criterion2 else 'FAIL'}")
print(f"Criterion 3 (spectral sanity)     : {'PASS' if criterion3 else 'FAIL'}")
overall = criterion1 and criterion2 and criterion3
print(f"Overall Verdict   : {'STABLE (PASS)' if overall else 'UNSTABLE (FAIL)'}")