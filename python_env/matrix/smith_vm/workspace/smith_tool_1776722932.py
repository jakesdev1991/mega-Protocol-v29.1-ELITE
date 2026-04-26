# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Jerk‑Stability Validator for Linux HSA Unified Memory
--------------------------------------------------------------------
Inputs:
    I_raw   : 1‑D array-like of raw information‑flow samples (GB/s)
    dt      : sampling period in seconds (e.g., 0.01 for 100 Hz)
    Jcrit   : jerk RMS threshold (default 1e6 GB/s³)
    outlier_factor : max|J| < outlier_factor * RMS(J) (default 3)
    sg_window : Savitzky‑Golay window length (must be odd, default 21)
    sg_order  : Savitzky‑Golay polynomial order (default 3)
    psd_nperseg : segment length for Welch PSD (default 256)
    psd_k : max allowed PSD bin as multiple of median (default 10)

Returns:
    bool : True if jerk‑stable, False otherwise
    dict : diagnostic details (RMS, maxJ, psd_ratio, etc.)
"""

import numpy as np
from scipy.signal import savgol_filter, welch

def jerk_stability(I_raw, dt, Jcrit=1e6, outlier_factor=3,
                   sg_window=21, sg_order=3,
                   psd_nperseg=256, psd_k=10.0):
    # ------------------------------------------------------------------
    # 1. Basic sanity checks
    # ------------------------------------------------------------------
    I_raw = np.asarray(I_raw, dtype=float)
    if I_raw.ndim != 1:
        raise ValueError("I_raw must be a 1‑D array")
    if len(I_raw) < sg_window:
        raise ValueError("Need at least sg_window samples for filtering")
    if sg_window % 2 == 0 or sg_window < sg_order + 2:
        raise ValueError("Invalid Savitzky‑Golay parameters")

    # ------------------------------------------------------------------
    # 2. Denoise
    # ------------------------------------------------------------------
    I = savgol_filter(I_raw, window_length=sg_window, polyorder=sg_order)

    # ------------------------------------------------------------------
    # 3. Compute jerk using 5‑point central stencil
    #    J[k] = (I[k+2] - 2*I[k+1] + 2*I[k-1] - I[k-2]) / (2*dt**3)
    # ------------------------------------------------------------------
    # Pad with NaN to keep same length; we will ignore the invalid edges.
    J = np.full_like(I, np.nan)
    J[2:-2] = (I[4:] - 2*I[3:-1] + 2*I[1:-3] - I[0:-4]) / (2.0 * dt**3)

    # Discard edge NaNs for statistics
    J_valid = J[~np.isnan(J)]

    if J_valid.size == 0:
        raise ValueError("Not enough valid jerk points after stencil")

    # ------------------------------------------------------------------
    # 4. Stability metrics
    # ------------------------------------------------------------------
    rms_J = np.sqrt(np.mean(J_valid**2))
    max_abs_J = np.max(np.abs(J_valid))

    # ------------------------------------------------------------------
    # 5. Spectral sanity (Welch PSD)
    # ------------------------------------------------------------------
    freqs, psd = welch(J_valid, fs=1.0/dt, nperseg=min(psd_nperseg, len(J_valid)))
    median_psd = np.median(psd)
    max_psd_ratio = np.max(psd) / median_psd if median_psd > 0 else np.inf

    # ------------------------------------------------------------------
    # 6. Decision logic
    # ------------------------------------------------------------------
    cond_rms = rms_J < Jcrit
    cond_peak = max_abs_J < outlier_factor * rms_J
    cond_spec = max_psd_ratio < psd_k  # no single bin dominates excessively

    stable = bool(cond_rms and cond_peak and cond_spec)

    diagnostics = {
        "rms_J": rms_J,
        "max_abs_J": max_abs_J,
        "Jcrit": Jcrit,
        "peak_factor": max_abs_J / rms_J if rms_J > 0 else np.inf,
        "psd_max_ratio": max_psd_ratio,
        "psd_k_limit": psd_k,
        "cond_rms": cond_rms,
        "cond_peak": cond_peak,
        "cond_spec": cond_spec,
        "jerk_stable": stable,
    }
    return stable, diagnostics


# ----------------------------------------------------------------------
# Example usage with synthetic data matching the agent's narrative
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate a 10 Hz oscillation of bandwidth between 150‑250 GB/s
    fs = 100.0          # Hz
    dt = 1.0 / fs
    t = np.arange(0, 10, dt)          # 10 seconds
    B = 200 + 50 * np.sin(2*np.pi*10*t)   # 150‑250 GB/s
    alpha = 1e-3
    C = 2000 + 500*np.cos(2*np.pi*10*t)   # dummy coherence traffic (msg/s)
    I_raw = B + alpha * C

    stable, info = jerk_stability(I_raw, dt)
    print("Jerk‑stable?", stable)
    for k, v in info.items():
        if isinstance(v, float):
            print(f"{k:>15}: {v:.3e}")
        else:
            print(f"{k:>15}: {v}")