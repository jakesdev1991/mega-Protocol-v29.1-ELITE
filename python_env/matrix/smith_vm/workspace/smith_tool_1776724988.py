# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Jerk‑Stability Validator for Linux HSA Unified Memory
-------------------------------------------------------------------
This script enforces the Ω‑Protocol invariant J* (bounded informational jerk)
by:
  1. Defining I(t) as a *rate* (GB/s) + scaled coherence rate (GB/s).
  2. Computing jerk J(t) = d³I/dt³ → units GB·s⁻⁴.
  3. Comparing RMS(J) and max|J| to a calibrated threshold J_crit (GB·s⁻⁴).
  4. Verifying spectral sanity (no growing high‑frequency peaks).
  5. Emitting a PASS/FAIL verdict that can be fed into the MPC‑Ω loop.

Assumptions (adjust as needed for a real node):
  - Sampling frequency Fs = 100 Hz (Δt = 0.01 s)
  - Savitzky‑Golay window = 21, polyorder = 3
  - J_crit derived from historical stable operation: 1.0e8 GB·s⁻⁴
    (example value; replace with calibrated measurement).
"""

import numpy as np
from scipy.signal import savgol_filter, welch

# ----------------------------------------------------------------------
# Configuration (tune to match the target HSA node)
# ----------------------------------------------------------------------
FS = 100.0                     # Hz, sampling rate
DT = 1.0 / FS                  # s, time step
WINDOW = 21                    # Savitzky‑Golay window length (must be odd)
ORDER = 3                      # polynomial order
# Example threshold: 1e8 GB·s⁻⁴ (adjust after calibration)
J_CRIT = 1.0e8                 # GB·s⁻⁴
OUTLIER_FACTOR = 3.0           # max|J| < OUTLIER_FACTOR * RMS(J)
# ----------------------------------------------------------------------


def synthesize_signal(duration_sec: float = 10.0) -> np.ndarray:
    """
    Produce a plausible I(t) = bandwidth + alpha * coherence_traffic.
    Bandwidth: baseline 200 GB/s + 10 Hz sinusoid ±50 GB/s.
    Coherence traffic: baseline 1e5 msgs/s + 5 Hz bursty component.
    Alpha converts msgs/s to GB/s assuming avg. message size = 8 KB.
    """
    t = np.arange(0, duration_sec, DT)
    # Bandwidth component (GB/s)
    bw_base = 200.0
    bw_osc = 50.0 * np.sin(2 * np.pi * 10.0 * t)   # 10 Hz sync
    bandwidth = bw_base + bw_osc

    # Coherence component (messages/s)
    coh_base = 1.0e5
    coh_burst = 2.0e5 * (np.sin(2 * np.pi * 5.0 * t) > 0)  # on/off bursts
    coherence_raw = coh_base + coh_burst

    # Convert messages/s → GB/s (assume 8 KB per message)
    BYTES_PER_MSG = 8 * 1024          # 8 KB
    GB_PER_MSG = BYTES_PER_MSG / (1024**3)  # GB
    alpha = GB_PER_MSG                # scaling factor (GB per message)
    coherence = alpha * coherence_raw  # GB/s

    I_t = bandwidth + coherence
    return t, I_t


def compute_jerk(I: np.ndarray, dt: float) -> np.ndarray:
    """
    Third derivative using Savitzky‑Golay smoothing followed by
    numpy.gradient applied three times (equivalent to central differences
    for uniform sampling after smoothing).
    """
    I_smooth = savgol_filter(I, window_length=WINDOW, polyorder=ORDER, deriv=0)
    # First, second, third derivative via gradient (central differences)
    dI = np.gradient(I_smooth, dt, edge_order=2)
    d2I = np.gradient(dI, dt, edge_order=2)
    d3I = np.gradient(d2I, dt, edge_order=2)   # jerk, units GB·s⁻⁴
    return d3I


def spectral_sanity(j: np.ndarray, fs: float) -> bool:
    """
    Check that the power spectral density (PSD) of jerk does not show
    a monotonic increase with frequency (i.e., no growing high‑freq peak).
    We fit a line to log‑PSD vs log‑freq; slope > 0 indicates growth.
    """
    freqs, psd = welch(j, fs=fs, nperseg=min(256, len(j)))
    # Ignore DC component
    mask = freqs > 0
    log_f = np.log(freqs[mask])
    log_p = np.log(psd[mask])
    # Linear regression slope
    A = np.vstack([log_f, np.ones_like(log_f)]).T
    slope, _ = np.linalg.lstsq(A, log_p, rcond=None)[0]
    return slope <= 0.0   # non‑positive slope → no spectral growth


def validate_jerk_stability(I: np.ndarray, dt: float) -> dict:
    """Run all Ω‑Protocol jerk‑stability checks."""
    jerk = compute_jerk(I, dt)               # GB·s⁻⁴
    rms_jerk = np.sqrt(np.mean(jerk**2))
    max_jerk = np.max(np.abs(jerk))

    # Criteria
    crit1 = rms_jerk < J_CRIT
    crit2 = max_jerk < OUTLIER_FACTOR * rms_jerk
    crit3 = spectral_sanity(jerk, FS)

    passed = crit1 and crit2 and crit3

    return {
        "jerk": jerk,
        "rms_jerk": rms_jerk,
        "max_jerk": max_jerk,
        "J_CRIT": J_CRIT,
        "crit_rms": crit1,
        "crit_outlier": crit2,
        "crit_spectral": crit3,
        "passed": passed,
    }


def main():
    t, I_t = synthesize_signal(duration_sec=20.0)
    result = validate_jerk_stability(I_t, DT)

    print("=== Omega‑Protocol Jerk‑Stability Validation ===")
    print(f"RMS Jerk          : {result['rms_jerk']:.3e} GB·s⁻⁴")
    print(f"Max |Jerk|        : {result['max_jerk']:.3e} GB·s⁻⁴")
    print(f"J_crit (threshold): {result['J_CRIT"]:.3e} GB·s⁻⁴")
    print(f"RMS test          : {'PASS' if result['crit_rms'] else 'FAIL'}")
    print(f"Outlier test      : {'PASS' if result['crit_outlier'] else 'FAIL'}")
    print(f"Spectral sanity   : {'PASS' if result['crit_spectral'] else 'FAIL'}")
    print(f"Overall verdict   : {'PASS' if result['passed'] else 'FAIL'}")

    if not result["passed"]:
        # In a real MPC‑Ω loop this would trigger a corrective action
        print("\n[Ω‑ALERT] Jerk instability detected – invoke MPC‑Ω damping.")
    else:
        print("\n[Ω‑OK] Jerk within invariant bounds – Φ density preserved.")


if __name__ == "__main__":
    main()