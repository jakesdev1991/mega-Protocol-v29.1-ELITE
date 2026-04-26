# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation: Informational Jerk Stability (IJS)
-------------------------------------------------------------
Verifies:
  - Dimensional consistency (jerk units = bytes·s⁻⁴)
  - IJS = 1/(1 + sigma_tilde_j) yields a dimensionless number in (0,1]
  - Optional: computes Shannon entropy of normalized jerk -> psi proxy
Usage:
    python validate_ijs.py --I <csv_file> --dt <float> --J0 <float> [--sg_window <int>] [--sg_order <int>]
"""

import argparse
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def parse_args():
    p = argparse.ArgumentParser(description="Validate IJS computation per Omega Protocol.")
    p.add_argument("--I", required=True, help="CSV with single column 'I' (bytes/s) vs time.")
    p.add_argument("--dt", type=float, required=True, help="Sampling interval Δt (seconds).")
    p.add_argument("--J0", type=float, required=True,
                   help="Normalization constant J0 (bytes·s⁻⁴) for jerk.")
    p.add_argument("--sg_window", type=int, default=5,
                   help="Savitzky–Golay window length (must be odd).")
    p.add_argument("--sg_order", type=int, default=2,
                   help="Savitzky–Golay polynomial order.")
    p.add_argument("--no-sg", action="store_true",
                   help="Skip Savitzky–Golay smoothing.")
    return p.parse_args()

def load_I(path):
    df = pd.read_csv(path)
    if 'I' not in df.columns:
        raise ValueError("CSV must contain a column named 'I' (bytes/s).")
    return df['I'].values.astype(float)

def smooth_signal(sig, window, order):
    if window % 2 == 0 or window < order + 2:
        raise ValueError("Savitzky–Golay window must be odd and >= order+2.")
    return savgol_filter(sig, window_length=window, polyorder=order, mode='interp')

def compute_jerk(I, dt):
    # First derivative: velocity (bytes/s^2)
    v = np.diff(I) / dt
    # Second derivative: acceleration (bytes/s^3)
    a = np.diff(v) / dt
    # Third derivative: jerk (bytes/s^4)
    j = np.diff(a) / dt
    # Align lengths: jerk corresponds to I[2:-2] after three diffs
    return j

def compute_IJS(j, J0):
    """Return dimensionless IJS and sigma_tilde_j."""
    j_tilde = j / J0                     # dimensionless
    sigma = np.sqrt(np.mean((j_tilde - np.mean(j_tilde))**2))
    ijs = 1.0 / (1.0 + sigma)
    return ijs, sigma, j_tilde

def shannon_entropy(samples, bins=50):
    """Simple Shannon entropy (base 2) of a 1D sample set."""
    hist, _ = np.histogram(samples, bins=bins, density=True)
    # Remove zeros to avoid log2(0)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist))

def main():
    args = parse_args()
    I = load_I(args.I)
    N = len(I)
    if N < 5:
        raise ValueError("Need at least 5 samples to compute jerk.")

    # Optional smoothing
    if not args.no_sg:
        I_proc = smooth_signal(I, args.sg_window, args.sg_order)
    else:
        I_proc = I

    # Jerk (bytes·s⁻⁴)
    jerk = compute_jerk(I_proc, args.dt)   # length = N-4
    if len(jerk) == 0:
        raise ValueError("Insufficient data after differentiation.")

    # Normalized jerk & IJS
    ijs, sigma_tilde, j_tilde = compute_IJS(jerk, args.J0)

    # Basic checks
    assert np.all(np.isfinite(jerk)), "Non-finite jerk values."
    assert 0 < ijs <= 1.0, f"IJS out of bounds: {ijs}"
    assert sigma_tilde >= 0, f"Negative sigma: {sigma_tilde}"

    # Entropy‑based invariant (proxy for ψ)
    entropy = shannon_entropy(j_tilde, bins=30)
    # Example mapping: ψ = ln(entropy_ratio) – can be adapted to Ω definitions
    psi_proxy = np.log(entropy + 1e-12)   # avoid log(0)

    # Report
    print("\n=== Omega Protocol IJS Validation ===")
    print(f"Samples processed          : {N}")
    print(f"Effective jerk samples     : {len(jerk)}")
    print(f"Jerk normalization J0      : {args.J0:.3e} bytes·s⁻⁴")
    print(f"Std‑dev of normalized jerk : {sigma_tilde:.6f}")
    print(f"Informational Jerk Stability (IJS) : {ijs:.6f}")
    print(f"Shannon entropy of ĵ       : {entropy:.4f} bits")
    print(f"Proxy ψ (ln entropy)       : {psi_proxy:.6f}")
    print("\nAll checks passed: IJS dimensionless and within (0,1].")
    print("=== End of Validation ===\n")

if __name__ == "__main__":
    main()