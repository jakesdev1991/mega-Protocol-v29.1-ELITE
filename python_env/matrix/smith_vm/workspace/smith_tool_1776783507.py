# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega‑Protocol validation of Informational Jerk stability for Linux HSA unified memory.

The script reproduces the synthetic entropy trace from the thought,
computes the jerk‑based stability index, and checks two invariants:
    1. |j|_RMS <= J_STAR   (jerk magnitude bound)
    2. S >= S_MIN          (stability index not negative)

If either invariant fails, the execution is marked as a protocol violation.
"""

import numpy as np

# ----------------------------------------------------------------------
# USER‑CONFIGURABLE PARAMETERS (match your Omega‑Protocol spec)
# ----------------------------------------------------------------------
DT          = 0.01          # sampling interval [s]  (10 ms as in the thought)
TOTAL_TIME  = 1.0           # total observation window [s]
WINDOW_SAMPLES = 50         # sliding window length for RMS(j) and mean a
J_STAR      = 5.0           # maximum allowed RMS jerk [bits/s^3]  (example)
S_MIN       = 0.0           # minimum acceptable stability index (>=0 -> stable)
# ----------------------------------------------------------------------


def synthetic_entropy(t):
    """
    Entropy trace used in the thought:
        H(t) = 12.5 + 0.1*sin(2πt) + 0.05*sin(6πt) + η(t),
        η ~ N(0, 0.01)
    """
    deterministic = 12.5 + 0.1 * np.sin(2 * np.pi * t) + 0.05 * np.sin(6 * np.pi * t)
    noise = np.random.normal(loc=0.0, scale=np.sqrt(0.01), size=t.shape)
    return deterministic + noise


def compute_derivatives(signal, dt):
    """
    First, second, and third discrete derivatives using forward differences
    (matching the thought's formulation: v[t] = (H[t]-H[t-1])/dt, etc.).
    The first element is set to NaN because it lacks a predecessor.
    """
    v = np.diff(signal) / dt                     # velocity, length N-1
    a = np.diff(v) / dt                          # acceleration, length N-2
    j = np.diff(a) / dt                          # jerk, length N-3

    # Align arrays by padding with NaNs at the start for direct indexing
    v_full = np.empty_like(signal)
    v_full[:] = np.nan
    v_full[1:] = v

    a_full = np.empty_like(signal)
    a_full[:] = np.nan
    a_full[2:] = a

    j_full = np.empty_like(signal)
    j_full[:] = np.nan
    j_full[3:] = j

    return v_full, a_full, j_full


def stability_index(j_window, a_window, eps=1e-6):
    """
    Compute S = 1 - RMS(j) / max(|mean(a)|, eps) over the supplied windows.
    """
    rms_j = np.sqrt(np.nanmean(j_window**2))
    mean_a = np.nanmean(a_window)
    denom = max(np.abs(mean_a), eps)
    return 1.0 - rms_j / denom


def main():
    # ------------------------------------------------------------------
    # 1. Build time vector and synthetic entropy
    # ------------------------------------------------------------------
    t = np.arange(0, TOTAL_TIME + DT/2, DT)   # include endpoint if exact
    H = synthetic_entropy(t)

    # ------------------------------------------------------------------
    # 2. Derivatives
    # ------------------------------------------------------------------
    v, a, j = compute_derivatives(H, DT)

    # ------------------------------------------------------------------
    # 3. Sliding‑window evaluation (use the last WINDOW_SAMPLES points)
    # ------------------------------------------------------------------
    if len(H) < WINDOW_SAMPLES + 3:   # need enough points for j
        raise ValueError("Observation too short for the chosen window size.")

    j_win = j[-WINDOW_SAMPLES:]
    a_win = a[-WINDOW_SAMPLES:]

    # ------------------------------------------------------------------
    # 4. Metrics
    # ------------------------------------------------------------------
    rms_j = np.sqrt(np.nanmean(j_win**2))
    mean_a = np.nanmean(a_win)
    S = stability_index(j_win, a_win)

    # ------------------------------------------------------------------
    # 5. Invariant checks
    # ------------------------------------------------------------------
    jerk_ok   = rms_j <= J_STAR
    stab_ok   = S >= S_MIN

    # ------------------------------------------------------------------
    # 6. Reporting
    # ------------------------------------------------------------------
    print("\n=== Omega‑Protocol Jerk‑Stability Audit ===")
    print(f"Sampling interval Δt          : {DT} s")
    print(f"Observation window            : {TOTAL_TIME} s ({len(H)} samples)")
    print(f"Analysis window (last)        : {WINDOW_SAMPLES} samples")
    print(f"RMS jerk                      : {rms_j:.4f} bits/s³")
    print(f"Mean acceleration (window)    : {mean_a:.4f} bits/s²")
    print(f"Stability index S             : {S:.4f}")
    print(f"Jerk bound J*                 : {J_STAR} bits/s³  → {'PASS' if jerk_ok else 'FAIL'}")
    print(f"Stability‑index lower bound   : {S_MIN}          → {'PASS' if stab_ok else 'FAIL'}")
    print("\nOverall verdict:", "PASS" if (jerk_ok and stab_ok) else "FAIL")
    if not (jerk_ok and stab_ok):
        print("  -> Protocol violation detected.")
    else:
        print("  -> Execution complies with Omega Protocol invariants.")


if __name__ == "__main__":
    # For reproducibility in debugging, fix the seed; remove for production runs.
    np.random.seed(42)
    main()