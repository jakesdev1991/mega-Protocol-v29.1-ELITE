# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Jerk-Stability Validator for Linux HSA Unified Memory
--------------------------------------------------------------------
Implements the corrected curvature bound and dimensionally‑consistent
entropy‑gauge bound as discussed in the audit.
"""

import numpy as np
from scipy.signal import savgol_filter
from scipy.optimize import curve_fit

# -------------------------- Helper Functions --------------------------

def exp_decay(t, tau):
    """Single‑sided exponential decay for autocorrelation fit."""
    return np.exp(-t / tau)

def estimate_stiffness(signal, dt):
    """
    Estimate stiffness ξ from the autocorrelation time constant.
    ξ ≈ τ (the decay time) because ξ has dimension of time in our
    natural‑unit mapping (mass⁻¹ ↔ seconds).
    """
    # autocorrelation (biased)
    acorr = np.correlate(signal, signal, mode='full')
    acorr = acorr[len(signal)-1:]          # keep non‑negative lags
    lags = np.arange(len(acorr)) * dt
    # normalize
    acorr = acorr / acorr[0]
    # fit exponential decay (skip zero lag)
    popt, _ = curve_fit(exp_decay, lags[1:], acorr[1:], p0=[0.01])
    tau = popt[0]                          # decay time constant
    return tau                            # ξ ≈ τ

def compute_jerk(psi, dt, window=5, order=3):
    """
    Robust third derivative using Savitzky‑Golay filter.
    Returns jerk array same length as psi.
    """
    # SavGol returns derivatives directly if deriv>0
    jerk = savgol_filter(psi, window_length=window, polyorder=order,
                         deriv=3, delta=dt)
    return jerk

def shannon_entropy(counts):
    """Shannon entropy from histogram counts (natural log)."""
    p = counts / counts.sum()
    p = p[p > 0]                     # avoid log(0)
    return -np.sum(p * np.log(p))

# -------------------------- Synthetic HSA Workload --------------------------

def simulate_hsa(t):
    """
    Generate B(t), L(t), F(t) resembling the spike described.
    Units: B in GB/s, L in ns, F in faults/s.
    """
    B = np.where(t < 0.5, 40.0, 10.0)               # drop at t=0.5s
    L = np.where(t < 0.5, 50.0, 200.0)              # rise at t=0.5s
    # Fault rate: Gaussian peak around t=0.5s
    F = 5000 * np.exp(-((t - 0.5) ** 2) / (2 * 0.05 ** 2))
    return B, L, F

# -------------------------- Main Validation Routine --------------------------

def main():
    # Simulation parameters
    TOTAL_TIME = 1.0          # seconds
    DT = 0.001                # 1 ms sampling
    t = np.arange(0, TOTAL_TIME, DT)
    N = len(t)

    # 1. Generate raw metrics
    B, L, F = simulate_hsa(t)

    # 2. Asymmetry A(t)
    B_cpu = B * 0.6   # assume CPU gets 60% of total bandwidth
    B_gpu = B * 0.4
    A = np.abs(B_cpu - B_gpu) / (B_cpu + B_gpu + 1e-12)

    # 3. Construct Φ_N and Φ_Δ (as per the paper)
    B_max = 100.0
    L_0   = 100.0
    beta  = 0.5
    gamma = 0.1
    Phi_N = (B / B_max) * np.exp(-beta * L / L_0)
    Phi_Delta = A + gamma * F

    # 4. Estimate stiffnesses ξ_N, ξ_Δ via autocorrelation decay
    xi_N = estimate_stiffness(Phi_N, DT)
    xi_Delta = estimate_stiffness(Phi_Delta, DT)

    # 5. Invariant ψ = ln(ξ_Δ/ξ_N)
    psi = np.log(xi_Delta / xi_N)

    # 6. Jerk 𝒥 = d³ψ/dt³
    jerk = compute_jerk(psi, DT)

    # 7. Curvature bound: |𝒥| < 1/(ξ_N² ξ_Δ)
    curvature_bound = 1.0 / (xi_N**2 * xi_Delta + 1e-30)
    curvature_ok = np.all(np.abs(jerk) < curvature_bound)

    # 8. Entropy gauge
    # Build histogram of fault counts per 10 ms window (coarser for stats)
    win_samples = int(0.01 / DT)          # 10 ms
    n_win = N // win_samples
    S_F = np.zeros(n_win)
    dS_dt = np.zeros(n_win)
    t_win = t[:n_win*win_samples:win_samples]
    for i in range(n_win):
        seg = F[i*win_samples:(i+1)*win_samples]
        hist, _ = np.histogram(seg, bins=10, range=(0, seg.max()+1))
        S_F[i] = shannon_entropy(hist)
    # derivative of entropy (central difference)
    dS_dt[1:-1] = (S_F[2:] - S_F[:-2]) / (2 * 0.01)
    dS_dt[0]    = (S_F[1] - S_F[0])   / 0.01
    dS_dt[-1]   = (S_F[-1] - S_F[-2]) / 0.01

    # Entropy coupling constant κ with mass dimension +2.
    # Choose reference mass m0 = (1 ns)^-1 = 1e9 s^-1 → m0^2 = 1e18 s^-2.
    m0 = 1e9          # s^-1
    kappa = 0.1 * m0**2   # dimension M^2 (in natural units)
    entropy_bound = kappa * np.abs(dS_dt)
    entropy_ok = np.all(np.abs(jerk[:n_win]) < entropy_bound)

    # 9. Reporting
    print("\n=== Omega Protocol Jerk‑Stability Audit ===")
    print(f"Estimated stiffnesses: ξ_N = {xi_N*1e3:.2f} ms, ξ_Δ = {xi_Delta*1e3:.2f} ms")
    print(f"ψ range: [{psi.min():.3f}, {psi.max():.3f}]")
    print(f"Jerk peak: {np.max(np.abs(jerk)):.2e} s⁻³")
    print(f"Curvature bound min: {np.min(curvature_bound):.2e} s⁻³")
    print(f"Curvature bound satisfied? {'YES' if curvature_ok else 'NO'}")
    print(f"Entropy bound (κ={kappa:.2e}) satisfied? {'YES' if entropy_ok else 'NO'}")
    overall = curvature_ok and entropy_ok
    print(f"Overall Omega‑Protocol compliance: {'PASS' if overall else 'FAIL'}")
    if not overall:
        print("\n⚠️  Violation detected – trigger mitigation protocol.")
    else:
        print("\n✅  All invariants respected.")

if __name__ == "__main__":
    main()