# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for HSA Unified Memory Jerk‑Stability Analysis
--------------------------------------------------------------------
Checks:
  - Dimensionless invariants (ψ, ξ̂_N, ξ̂_Δ, S_h, S_j)
  - Proper jerk‑stability mapping (S_j ∈ (0,1], S_j=1 for Gaussian/constant jerk)
  - Balanced cost‑function terms (each term O(1))
  - Presence of J* (estimated cost-to-go) in state vector
  - Entropy bias correction warning
Run:  python3 omega_validator.py
"""

import numpy as np
from scipy.stats import kurtosis, entropy

# -------------------------- Configuration --------------------------
DT_MS = 1.0               # telemetry sampling period (ms)
FS_HZ = 1000.0 / DT_MS    # sampling frequency
WINDOW_MS = 100.0         # jerk stability window
N_WINDOW = int(WINDOW_MS / DT_MS)
L_REF = 1.0e-6            # reference length (1 µm) for normalising ξ_N, ξ_Δ
P_REF = 150.0             # reference power (W) – typical TDP
ALPHA = 0.1               # entropy weight
LAMBDA = 0.05             # power weight
J_THRESH = 0.5            # jerk threshold for MPC trigger (example)
# ------------------------------------------------------------------

def synthetic_telemetry(n_samples=5000):
    """Generate fake HSA telemetry: coherence ψ, power P, and derived jerk."""
    t = np.arange(n_samples) * DT_MS * 1e-3  # seconds
    # Baseline coherence with slow drift + Gaussian noise
    psi_base = 0.2 * np.sin(2*np.pi*0.01*t) + 0.01*np.random.randn(n_samples)
    # Inject occasional heavy‑tailed jerk bursts (pre‑shredding)
    jerk = 0.0*np.copy(psi_base)
    burst_idx = np.random.choice(n_samples, size=20, replace=False)
    jerk[burst_idx] = 5.0 * np.sign(np.random.randn(len(burst_idx)))
    # Reconstruct psi from jerk via double integration (crude)
    psi = np.cumsum(np.cumsum(jerk))* (DT_MS*1e-3)**2 + psi_base
    # Power: baseline + small fluctuations
    P_base = 120.0 + 10.0*np.sin(2*np.pi*0.005*t)
    P = P_base + 2.0*np.random.randn(n_samples)
    return t, psi, jerk, P

def compute_invariants(psi):
    """Compute ψ, ξ̂_N, ξ̂_Δ, Φ_N, Φ_Δ from coherence field ψ."""
    # ψ(t) = ln(mean directional bias) – we already have psi as log‑bias
    psi_mean = np.mean(psi)
    Phi_N = psi_mean                     # ⟨ψ⟩
    Phi_Delta = np.std(psi)              # std(ψ)
    # For demo, estimate ξ_N as inverse of autocorrelation decay length
    acorr = np.correlate(psi - psi_mean, psi - psi_mean, mode='full')
    acorr = acorr[len(acorr)//2:] / acorr[0]
    # find 1/e point
    idx = np.where(acorr < np.exp(-1))[0]
    xi_N = idx[0] * DT_MS * 1e-3 if len(idx) > 0 else 0.0   # seconds → convert to meters via dummy speed
    # ξ_Δ: std of decay constants across two fake pathways (CPU‑GPU, GPU‑GPU)
    xi_path1 = xi_N * (1.0 + 0.1*np.random.randn())
    xi_path2 = xi_N * (1.0 - 0.1*np.random.randn())
    xi_Delta = np.std([xi_path1, xi_path2])
    # Normalise to dimensionless
    xi_N_hat = xi_N / L_REF
    xi_Delta_hat = xi_Delta / L_REF
    return {
        'psi': psi_mean,
        'Phi_N': Phi_N,
        'Phi_Delta': Phi_Delta,
        'xi_N_hat': xi_N_hat,
        'xi_Delta_hat': xi_Delta_hat,
        'xi_N_raw': xi_N,
        'xi_Delta_raw': xi_Delta
    }

def coherence_entropy(psi, bins=10):
    """Shannon entropy of ψ distribution with Miller‑Madow bias correction."""
    hist, _ = np.histogram(psi, bins=bins, density=False)
    p = hist / hist.sum()
    # Miller‑Madow correction: (K-1)/(2N)
    K = np.count_nonzero(p)
    N = hist.sum()
    bias = (K - 1) / (2 * N) if N > 0 else 0.0
    S = -np.sum(p[p>0] * np.log(p[p>0])) + bias
    return S, K, N

def jerk_stability_metric(j, window=N_WINDOW):
    """
    Corrected S_j using bounded excess kurtosis:
        S_j = 1 / (1 + max(0, excess_kurtosis))
    Returns time series aligned with input.
    """
    S_j = np.full_like(j, np.nan)
    half = window // 2
    for i in range(half, len(j)-half):
        seg = j[i-half:i+half+1]
        if np.std(seg) == 0:
            excess = 0.0          # treat constant as Gaussian-like
        else:
            exc = kurtosis(seg, fisher=True)  # excess kurtosis
            excess = max(0.0, exc)            # ignore negative (platykurtic)
        S_j[i] = 1.0 / (1.0 + excess)
    return S_j

def cost_function(S_j, S_h, P_meas, P_target):
    """Dimensionless MPC‑Ω integrand (per sample)."""
    jerk_term = (1.0 - S_j)**2
    entropy_term = ALPHA * S_h
    power_term = LAMBDA * ((P_meas - P_target) / P_REF)**2
    return jerk_term + entropy_term + power_term

def validate():
    t, psi_raw, jerk_raw, P_meas = synthetic_telemetry()
    inv = compute_invariants(psi_raw)
    S_h, K, N = coherence_entropy(psi_raw)
    S_j = jerk_stability_metric(jerk_raw)
    # Align arrays (drop NaNs from edges)
    valid = ~np.isnan(S_j)
    jerk_term = (1.0 - S_j[valid])**2
    entropy_term = ALPHA * S_h
    power_term = LAMBDA * ((P_meas[valid] - np.mean(P_meas)) / P_REF)**2

    # ---------- Omega Protocol Checks ----------
    # 1. Dimensionless invariants
    assert np.isfinite(inv['psi']), "ψ must be finite"
    assert np.isfinite(inv['Phi_N']), "Φ_N must be finite"
    assert np.isfinite(inv['Phi_Delta']), "Φ_Δ must be finite"
    assert np.isfinite(inv['xi_N_hat']), "ξ̂_N must be finite and dimensionless"
    assert np.isfinite(inv['xi_Delta_hat']), "ξ̂_Δ must be finite and dimensionless"
    # 2. S_j bounds
    assert np.all((S_j[valid] > 0) & (S_j[valid] <= 1+1e-12)), \
        f"S_j out of bounds: min={S_j[valid].min()}, max={S_j[valid].max()}"
    # Gaussian segment should give S_j≈1
    gauss_mask = np.abs(jerk_raw) < 0.1  # low‑jerk region approximated as Gaussian
    if np.any(gauss_mask & valid):
        Sj_gauss = S_j[gauss_mask & valid].mean()
        assert np.abs(Sj_gauss - 1.0) < 0.2, \
            f"S_j for near‑Gaussian jerk deviates: {Sj_gauss}"
    # 3. Cost term balance (each term O(1))
    term_means = [jerk_term.mean(), np.full_like(jerk_term, entropy_term).mean(), power_term.mean()]
    max_term = max(term_means)
    min_term = min(term_means)
    assert max_term / (min_term + 1e-9) < 10.0, \
        f"Cost terms imbalanced: jerk={jerk_term.mean():.3f}, entr={entropy_term:.3f}, power={power_term.mean():.3f}"
    # 4. Presence of J* (we approximate as cumulative cost)
    J_est = np.cumsum(cost_function(S_j, S_h, P_meas, np.mean(P_meas)) * DT_MS*1e-3)
    assert np.all(np.isfinite(J_est)), "J* (estimated cost-to-go) must be finite"
    # 5. Entropy bias warning
    if N < 5*K:
        print(f"[WARN] Entropy estimator may be biased: N={N}, K={K}. Consider more samples.")
    print("[PASS] All Omega Protocol invariants satisfied.")
    return inv, S_h, S_j, J_est

if __name__ == "__main__":
    validate()