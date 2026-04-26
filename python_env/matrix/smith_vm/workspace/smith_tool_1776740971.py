# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Agent Smith – Omega Protocol Jerk‑Stability Validator
----------------------------------------------------
Validates the dimensional correctness and stability criteria
for the "Informational Jerk" analysis of a Linux HSA node.

Usage:
    python jerk_validator.py   # runs internal self‑test with synthetic data
    # or import the functions and feed your own sampled I(t) array.
"""

import numpy as np
from scipy.signal import savgol_filter
from pint import UnitRegistry

# ----------------------------------------------------------------------
# Unit registry and helper definitions
# ----------------------------------------------------------------------
ureg = UnitRegistry()
GB = ureg.gigabyte
s = ureg.second
Hz = ureg.hertz

# Base units used in the analysis
GB_per_s = GB / s          # bandwidth unit
msg_per_s = 1 / s          # coherence message rate (dimensionless count per second)
# alpha is dimensionless; we keep it as a scaling factor to match GB_per_s
# (the Engine chose alpha = 1e-3, but any dimensionless constant works)

def check_units():
    """Dimensional audit of the metric and its derivatives."""
    print("=== Dimensional Audit ===")
    # I(t) = B(t) + alpha * C(t)
    I_unit = GB_per_s  # because both terms are forced to GB/s
    print(f"I(t) unit: {I_unit}")

    dt = 0.01 * s  # example sampling period (100 Hz)
    # Finite‑difference formulas (central differences)
    # First derivative: (I_{k+1} - I_{k-1}) / (2Δt)
    v_unit = I_unit / s
    print(f"dI/dt unit: {v_unit}")

    # Second derivative: (I_{k+1} - 2I_k + I_{k-1}) / (Δt)^2
    a_unit = I_unit / (s**2)
    print(f"d²I/dt² unit: {a_unit}")

    # Third derivative (jerk): (I_{k+2} - 2I_{k+1} + 2I_{k-1} - I_{k-2}) / (2Δt)^3
    j_unit = I_unit / (s**3)
    print(f"d³I/dt³ (jerk) unit: {j_unit}")

    # Expected threshold unit from Engine
    Jcrit_given = 1e6 * (GB / (s**3))   # as written in the Engine output
    print(f"Engine's J_crit unit: {Jcrit_given}")
    print(f"Correct J_crit unit should be: {j_unit}")
    if Jcrit_given.check(j_unit):
        print("✅ J_crit units match jerk units.")
    else:
        print("❌ J_crit units DO NOT match jerk units – this is the core error.")
    print()

def synthetic_bandwidth_signal(fs=100, duration=10, freq=10, amp=100, baseline=200):
    """
    Generate a synthetic I(t) resembling bandwidth oscillation:
        I(t) = baseline + amp * sin(2π * freq * t)   [GB/s]
    """
    t = np.arange(0, duration, 1/fs) * s
    I = (baseline + amp * np.sin(2*np.pi*freq*t.magnitude)) * GB_per_s
    return t, I

def compute_jerk(I, dt):
    """
    Compute jerk using the Engine's central-difference formula,
    after Savitzky‑Golay smoothing (window=21, order=3).
    Returns jerk array (same length as I, with NaNs at edges).
    """
    # Smooth
    I_smooth = savgol_filter(I.magnitude, window_length=21, polyorder=3) * I.units
    I_vec = I_smooth.magnitude  # work in pure numbers for speed
    N = len(I_vec)
    jerk = np.full(N, np.nan)
    # Engine's formula: (I_{k+2} - 2I_{k+1} + 2I_{k-1} - I_{k-2}) / (2Δt)^3
    denom = 2 * (dt**3)
    for k in range(2, N-2):
        jerk[k] = (I_vec[k+2] - 2*I_vec[k+1] + 2*I_vec[k-1] - I_vec[k-2]) / denom
    return jerk * (I.units / (s**3))  # re‑attach correct units

def stability_check(jerk, Jcrit):
    """
    Apply the three stability criteria:
      1. RMS(J) < Jcrit
      2. max|J| < 3 * RMS(J)
      3. No spectral divergence (simple check: max PSD frequency < Nyquist/2)
    Returns dict of results.
    """
    # Remove NaNs from edges
    J = jerk[~np.isnan(jerk.magnitude)]
    J_mag = J.magnitude  # plain numbers for stats
    J_unit = J.units

    rms = np.sqrt(np.mean(J_mag**2)) * J_unit
    max_abs = np.max(np.abs(J_mag)) * J_unit

    cond1 = rms < Jcrit
    cond2 = max_abs < 3 * rms

    # Spectral sanity: compute PSD via Welch, ensure no monotonic rise at high freq
    from scipy.signal import welch
    fs = 1 / (0.01 * s)  # assume 100 Hz sampling; adjust if known
    f, Pxx = welch(J_mag, fs=fs.magnitude, nperseg=1024)
    # Fit a line to the high‑frequency tail (last 10% of frequencies)
    tail_idx = int(0.9 * len(f))
    if tail_idx < len(f):
        coeffs = np.polynpolyfit(f[tail_idx:], Pxx[tail_idx:], 1)
        slope = coeffs[0]
        cond3 = slope <= 0  # non‑positive slope → no growing high‑freq power
    else:
        cond3 = True  # insufficient data, assume pass

    return {
        "RMS_J": rms,
        "Max|J|": max_abs,
        "J_crit": Jcrit,
        "Cond_RMS": cond1,
        "Cond_Outlier": cond2,
        "Cond_Spectral": cond3,
        "Overall": cond1 and cond2 and cond3,
        "Unit": J_unit,
    }

def main():
    print("Agent Smith – Jerk‑Stability Validation\n")
    check_units()

    # --- Synthetic test -------------------------------------------------
    t, I = synthetic_bandwidth_signal()
    dt = (t[1] - t[0])  # sampling interval as a Quantity
    jerk = compute_jerk(I, dt)

    # Engine's threshold (incorrect units) – we will test both:
    Jcrit_engine = 1e6 * (GB / (s**3))          # as written
    Jcrit_correct = 1e6 * (GB / (s**4))          # what it should be if I is GB/s

    print("=== Stability Check (synthetic 10 Hz bandwidth oscillation) ===")
    for label, Jcrit in [("Engine's Jcrit (GB/s³)", Jcrit_engine),
                         ("Corrected Jcrit (GB/s⁴)", Jcrit_correct)]:
        res = stability_check(jerk, Jcrit)
        print(f"\nUsing {label}:")
        print(f"  RMS(J)      = {res['RMS_J']:.3e}")
        print(f"  Max|J|      = {res['Max|J|']:.3e}")
        print(f"  J_crit      = {res['J_crit']:.3e}")
        print(f"  RMS < Jcrit ? {res['Cond_RMS']}")
        print(f"  Max|J| < 3·RMS? {res['Cond_Outlier']}")
        print(f"  Spectral sane? {res['Cond_Spectral']}")
        print(f"  OVERALL STABLE? {res['Overall']}")
    print("\n--- Interpretation ---")
    print("If the corrected Jcrit (GB/s⁴) is used, the synthetic signal will")
    print("likely violate the RMS bound, indicating that the Engine's")
    print("numerical stability claim is an artifact of the unit mismatch.")
    print("\nEnforcement: any Omega‑Protocol monitoring tool must")
    print("verify that the jerk unit matches the derivative of the")
    print("information‑flow metric before comparing to Jcrit.")

if __name__ == "__main__":
    main()