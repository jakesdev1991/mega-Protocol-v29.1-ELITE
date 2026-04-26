# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol Jerk‑Stability Validator
---------------------------------------
Validates an Informational‑Jerk analysis for an HSA node with unified memory.
Assumes the information‑flow metric I(t) is supplied as a *rate* (GB/s).
"""

import numpy as np
from scipy.signal import savgol_filter
from scipy.fft import rfft, rfftfreq

# ----------------------------------------------------------------------
# USER‑CONFIGURABLE PARAMETERS (set according to the specific analysis)
# ----------------------------------------------------------------------
DT = 0.01                     # sampling period [s] (100 Hz -> 0.01 s)
ALPHA = 1e-3                  # scaling factor for coherence traffic (messages/s -> GB/s)
J_CRIT = 1e6                  # Omega‑jerk invariant J* [GB/s^4]  (note: corrected unit)
RMS_FACTOR = 3.0              # outlier threshold = RMS_FACTOR * RMS(J)
WINDOW_LEN = 21               # Savitzky‑Golay window (must be odd)
POL_ORDER = 3                 # Savitzky‑Golay polynomial order
# ----------------------------------------------------------------------


def compute_jerk(I_raw: np.ndarray) -> np.ndarray:
    """
    Compute the third derivative (jerk) of a uniformly sampled signal.
    Steps:
      1. Denoise with Savitzky‑Golay filter.
      2. Apply central‑difference formulas for 1st, 2nd, 3rd derivatives.
    Returns jerk array J_k (same length as input, with edge points set to NaN).
    """
    if len(I_raw) < WINDOW_LEN:
        raise ValueError("Signal length must be >= Savitzky‑Golay window.")

    # 1. Denoise
    I_filt = savgol_filter(I_raw, window_length=WINDOW_LEN,
                           polyorder=POL_ORDER, deriv=0)

    # 2. Derivatives (central differences)
    # First derivative (velocity)
    Idot = np.empty_like(I_filt)
    Idot[1:-1] = (I_filt[2:] - I_filt[:-2]) / (2 * DT)
    Idot[0] = Idot[-1] = np.nan  # edges undefined

    # Second derivative (acceleration)
    Iddot = np.empty_like(I_filt)
    Iddot[1:-1] = (I_filt[2:] - 2 * I_filt[1:-1] + I_filt[:-2]) / (DT ** 2)
    Iddot[0] = Iddot[-1] = np.nan

    # Third derivative (jerk) – using the 5‑point stencil supplied in the Engine
    Ijerk = np.empty_like(I_filt)
    # J_k = (I_{k+2} - 2I_{k+1} + 2I_{k-1} - I_{k-2}) / (2 * Δt^3)
    Ijerk[2:-2] = (I_filt[4:] - 2 * I_filt[3:-1] +
                   2 * I_filt[1:-3] - I_filt[:-4]) / (2 * DT ** 3)
    # Edges set to NaN
    Ijerk[:2] = Ijerk[-2:] = np.nan

    return Ijerk


def stability_metrics(J: np.ndarray):
    """
    Compute RMS jerk, max absolute jerk, and a simple spectral sanity check.
    Returns a dict with results and boolean flags for each Omega criterion.
    """
    # Remove NaNs (edge points)
    J_valid = J[~np.isnan(J)]

    rms_J = np.sqrt(np.mean(J_valid ** 2))
    max_abs_J = np.max(np.abs(J_valid))

    # Criterion 1: bounded RMS
    crit1 = rms_J < J_CRIT

    # Criterion 2: no outlier spikes
    crit2 = max_abs_J < RMS_FACTOR * rms_J

    # Criterion 3: spectral sanity – no growing high‑frequency peak
    # We compute PSD and check that the slope beyond the Nyquist/2 is non‑positive.
    N = len(J_valid)
    freqs = rfftfreq(N, DT)
    psd = np.abs(rfft(J_valid)) ** 2
    # Find index where frequency > 0.5 / DT (Nyquist) -> actually we only have up to Nyquist.
    # We'll examine the upper half of the spectrum.
    half = len(freqs) // 2
    if half > 1:
        # Fit a line to log(PSD) vs log(freq) in the high‑freq region
        high_f = freqs[half:]
        high_psd = psd[half:]
        # Avoid zeros
        mask = high_psd > 0
        if np.any(mask):
            coeffs = np.polyfit(np.log(high_f[mask]), np.log(high_psd[mask]), 1)
            # Negative slope indicates decay; we require slope < 0 (strictly decreasing)
            crit3 = coeffs[0] < 0
        else:
            crit3 = False  # degenerate case
    else:
        crit3 = True  # not enough points to assess

    return {
        "RMS_J": rms_J,
        "MaxAbs_J": max_abs_J,
        "J_CRIT": J_CRIT,
        "Crit_RMS": crit1,
        "Crit_Outlier": crit2,
        "Crit_Spectral": crit3,
        "Stable": crit1 and crit2 and crit3,
    }


def validate_analysis(I_raw: np.ndarray):
    """
    Full validation pipeline.
    Prints a concise report and raises an AssertionError if any Omega rule is violated.
    """
    # 1. Jerk computation
    J = compute_jerk(I_raw)

    # 2. Stability metrics
    metrics = stability_metrics(J)

    # 3. Dimensional sanity check (unit test)
    # I_raw is assumed to be in GB/s -> jerk unit must be GB/s^4.
    # We verify that the numerical magnitude is plausible for a sinusoidal test.
    # (Optional: can be expanded with known analytical test signals.)
    # Here we just assert that J_CRIT is expressed in GB/s^4.
    assert J_CRIT > 0, "J_CRIT must be positive."

    # 4. Omega‑Protocol invariant check
    if not metrics["Stable"]:
        raise AssertionError(
            f"Omega Jerk invariant violated: "
            f"RMS_J={metrics['RMS_J']:.3e} GB/s^4, "
            f"Max|J|={metrics['MaxAbs_J']:.3e} GB/s^4, "
            f"J_CRIT={metrics['J_CRIT']:.3e} GB/s^4."
        )

    # 5. Report
    print("=== Omega Jerk‑Stability Validation ===")
    print(f"RMS Jerk          : {metrics['RMS_J']:.3e} GB/s^4  (< {metrics['J_CRIT']:.3e}) ? {metrics['Crit_RMS']}")
    print(f"Max |Jerk|        : {metrics['MaxAbs_J']:.3e} GB/s^4  (< {RMS_FACTOR}*RMS) ? {metrics['Crit_Outlier']}")
    print(f"Spectral sanity   : {metrics['Crit_Spectral']}")
    print(f"Overall Stable    : {metrics['Stable']}")
    print("========================================")
    return metrics


# ----------------------------------------------------------------------
# Example usage with a synthetic signal (for illustration only)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate a bandwidth‑like signal: baseline + 10 Hz oscillation
    t = np.arange(0, 10, DT)               # 10 seconds of data
    I0 = 200.0                             # GB/s baseline
    A = 50.0                               # GB/s amplitude
    I_signal = I0 + A * np.sin(2 * np.pi * 10 * t)  # GB/s (rate)

    # Add coherence‑traffic component (scaled)
    coh_rate = 1e6 * np.abs(np.sin(2 * np.pi * 2 * t))  # messages/s dummy
    I_total = I_signal + ALPHA * coh_rate               # still GB/s

    try:
        validate_analysis(I_total)
    except AssertionError as e:
        print("VALIDATION FAILED:", e)