# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
POASH‑Ω Coherence Catastrophe Demo

Simulates a three‑sensor pipeline (latency, throughput, CPU) with a periodic
baseline and a sudden transient fault (non‑harmonic).  Computes the POASH‑Ω
stiffness invariants (λ_N, λ_Δ) and the Pipeline Health Index (PHI).
Shows that:
  1.  As coherence drops, λ_N, λ_Δ blow up (ξ → 0) – false "rigidity".
  2.  PHI remains high during the transient – missed fault.
  3.  Entropy‑based I(t) barely changes – no early warning.
"""

import numpy as np
import scipy.signal as sig

# ------------------------------------------------------------
# 1.  Simulate pipeline sensors
# ------------------------------------------------------------
fs = 100.0        # sampling rate (Hz)
T = 120.0         # total time (s)
t = np.arange(0, T, 1/fs)

# Baseline periodic signals (1 Hz batch interval)
latency = 10.0 + 2.0*np.sin(2*np.pi*1.0*t) + 0.5*np.random.randn(len(t))
throughput = 1000.0 + 100.0*np.sin(2*np.pi*1.0*t + np.pi/4) + 10.0*np.random.randn(len(t))
cpu = 50.0 + 10.0*np.sin(2*np.pi*1.0*t + np.pi/2) + 2.0*np.random.randn(len(t))

# Inject a *non‑harmonic* transient at t=60 s (a 2‑second latency spike)
transient_start = int(60.0 * fs)
transient_end   = int(62.0 * fs)
latency[transient_start:transient_end] += 50.0   # huge spike

# Stack into a data matrix (sensors × time)
X = np.vstack([latency, throughput, cpu])

# ------------------------------------------------------------
# 2.  Compute harmonic amplitudes (order k=1 only, for simplicity)
# ------------------------------------------------------------
def harmonic_amplitude(x, f0=1.0, fs=fs):
    """Extract amplitude of the f0 component via STFT."""
    f, t_stft, Zxx = sig.stft(x, fs=fs, nperseg=int(fs), noverlap=int(fs//2))
    # Find bin closest to f0
    idx = np.argmin(np.abs(f - f0))
    amp = np.abs(Zxx[idx, :])
    # Interpolate back to original time grid (simple nearest‑neighbor)
    t_new = np.linspace(0, T, amp.shape[0])
    amp_interp = np.interp(t, t_new, amp)
    return amp_interp

A_lat = harmonic_amplitude(latency)
A_thr = harmonic_amplitude(throughput)
A_cpu = harmonic_amplitude(cpu)
A = np.vstack([A_lat, A_thr, A_cpu])   # shape (3, time)

# ------------------------------------------------------------
# 3.  Compute PHI (as defined in proposal)
# ------------------------------------------------------------
# "Healthy" baselines and std devs (computed from first 30 s of "clean" data)
healthy_slice = slice(0, int(30*fs))
mu = A[:, healthy_slice].mean(axis=1)
sigma = A[:, healthy_slice].std(axis=1)
# Weights w_k (simple uniform)
w = np.array([1/3, 1/3, 1/3])

# PHI(t) = 1 - Σ w_k |A_k(t) - μ_k|/σ_k
PHI = 1.0 - np.sum(w[:, None] * np.abs(A - mu[:, None]) / sigma[:, None], axis=0)

# ------------------------------------------------------------
# 4.  Compute "information field" I(t) = -Σ p_k log p_k
# ------------------------------------------------------------
# p_k(t) = |A_k|² / Σ |A_j|²
p = A**2 / np.sum(A**2, axis=0)[None, :]
# Avoid log(0)
p = np.clip(p, 1e-12, None)
I = -np.sum(p * np.log(p), axis=0)

# ------------------------------------------------------------
# 5.  Compute cross‑coherence between sensor pairs
# ------------------------------------------------------------
def avg_coherence(x, y, fs=fs):
    """Average magnitude‑squared coherence over all frequency bins."""
    f, Cxy = sig.coherence(x, y, fs=fs, nperseg=int(fs), noverlap=int(fs//2))
    return np.mean(Cxy)

# Compute pairwise average coherence in a sliding window (window = 5 s)
window = int(5*fs)
coherence_ts = np.full_like(t, np.nan)
for i in range(window, len(t)-window):
    # window slices
    x_win = X[0, i-window:i]
    y_win = X[1, i-window:i]
    z_win = X[2, i-window:i]
    # average across three pairs
    c_xy = avg_coherence(x_win, y_win)
    c_xz = avg_coherence(x_win, z_win)
    c_yz = avg_coherence(y_win, z_win)
    coherence_ts[i] = (c_xy + c_xz + c_yz) / 3.0

# Fill edges
coherence_ts[:window] = coherence_ts[window]
coherence_ts[-window:] = coherence_ts[-window-1]

# ------------------------------------------------------------
# 6.  Compute POASH‑Ω stiffness invariants λ_N, λ_Δ
# ------------------------------------------------------------
# Coupling constant λ (proposal says [time]⁻², we set λ = 1.0 for demo)
lam = 1.0
# Avoid division by zero in coherence
coh = np.clip(coherence_ts, 1e-6, None)
lam_N = lam * (3.0/coh + 1.0/coh**2)
lam_D = lam * (1.0/coh + 3.0/coh**2)

# ------------------------------------------------------------
# 7.  Summarize fault detection performance
# ------------------------------------------------------------
print("=== POASH‑Ω Fault Detection Summary ===")
print(f"Transient injected at t = 60–62 s")
# Detection thresholds (ad‑hoc)
phi_alarm = np.mean(PHI[transient_start:transient_end])
i_change = np.max(I[transient_start:transient_end]) - np.mean(I[:transient_start])
print(f"Mean PHI during transient: {phi_alarm:.3f} (threshold ≈ 0.4) -> {'NO ALARM' if phi_alarm > 0.4 else 'ALARM'}")
print(f"Max I‑change during transient: {i_change:.3f} (baseline ≈ {np.mean(I[:transient_start]):.3f}) -> {'NO ALARM' if i_change < 0.05 else 'ALARM'}")
# Stiffness catastrophe
print(f"λ_N near transient: min={lam_N[transient_start:transient_end].min():.1e}, max={lam_N[transient_start:transient_end].max():.1e}")
print(f"λ_Δ near transient: min={lam_D[transient_start:transient_end].min():.1e}, max={lam_D[transient_start:transient_end].max():.1e}")
print("→ As coherence drops, stiffness eigenvalues diverge (ξ→0), predicting infinite rigidity during failure. This is the *coherence catastrophe*.")