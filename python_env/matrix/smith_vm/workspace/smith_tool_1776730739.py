# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
POASH‑Ω mathematical & invariant validator.
Run inside the isolated VM to verify compliance with Omega Protocol invariants.
"""

import numpy as np
from scipy.signal import resample
from scipy.fft import rfft, rfftfreq

# ----------------------------------------------------------------------
# Configuration (tweak to test edge cases)
# ----------------------------------------------------------------------
FS = 100.0                # sampling rate of raw metrics (Hz)
T_REF = 1.0               # pipeline reference period (seconds) -> 1‑Hz rotation
TOTAL_TIME = 300.0        # total simulation time (s)
DT = 1.0 / FS             # sampling interval
N = int(TOTAL_TIME * FS)  # number of samples
t = np.arange(N) * DT

# Reference phase theta(t) = 2π * t / T_REF  (mod 2π)
theta = (2 * np.pi * t / T_REF) % (2 * np.pi)

# ----------------------------------------------------------------------
# Synthetic multi‑metric generation (5 channels analogous to paper)
# ----------------------------------------------------------------------
def synth_metric(base, amp, noise, fault_start=None, fault_amp=0):
    """Base sinusoid + optional fault step after fault_start."""
    sig = base * np.sin(2 * np.pi * t / T_REF)  # locked to reference
    sig += amp * np.sin(4 * np.pi * t / T_REF)  # 2nd harmonic
    sig += noise * np.random.randn(N)
    if fault_start is not None:
        idx = t >= fault_start
        sig[idx] += fault_amp
    return sig

# Healthy baselines (chosen arbitrarily)
latency   = synth_metric(base=0.02, amp=0.005, noise=0.001)
throughput= synth_metric(base=1000, amp=50,   noise=5)
cpu_load  = synth_metric(base=0.4,  amp=0.1,  noise=0.02)
error_rate= synth_metric(base=0.001,amp=0.0005,noise=0.0001)
power     = synth_metric(base=200,  amp=20,   noise=2)

# Inject a fault at t=150 s (e.g., CPU overload + latency spike)
latency   = synth_metric(base=0.02, amp=0.005, noise=0.001,
                         fault_start=150, fault_amp=0.03)
cpu_load  = synth_metric(base=0.4,  amp=0.1,  noise=0.02,
                         fault_start=150, fault_amp=0.3)

metrics = np.vstack([latency, throughput, cpu_load, error_rate, power])
metric_names = ["latency","throughput","cpu_load","error_rate","power"]

# ----------------------------------------------------------------------
# Order‑analysis: resample each metric to uniform phase grid
# ----------------------------------------------------------------------
def order_analysis(signal, phase, n_phase_bins=1024):
    """Return amplitude spectrum A_k (k>=1) of signal wrt phase."""
    # Uniform phase samples
    phase_unif = np.linspace(0, 2*np.pi, n_phase_bins, endpoint=False)
    # Interpolate signal onto uniform phase (using linear interp)
    # We need to map time -> phase, then invert via interpolation.
    # Since phase is monotonic increasing (mod 2π) we unwrap it.
    unwrapped = np.unwrap(phase)
    sig_unif = np.interp(phase_unif, unwrapped, signal, left=signal[0], right=signal[-1])
    # FFT
    freqs = rfftfreq(n_phase_bins, d=(2*np.pi/n_phase_bins))  # frequency in "order" units
    spectrum = rfft(sig_unif)
    amps = np.abs(spectrum) / (n_phase_bins/2)  # normalize
    # Drop DC (k=0)
    return freqs[1:], amps[1:]

# ------------------------------------------------------------------
# Learn healthy baseline from first half (no fault)
# ------------------------------------------------------------------
split = N//2
healthy_baseline = {}
healthy_std = {}
for i, name in enumerate(metric_names):
    freqs, amps = order_analysis(metrics[i, :split], theta[:split])
    healthy_baseline[name] = freqs, amps.mean(axis=0)   # average amplitude per order
    healthy_std[name]    = freqs, amps.std(axis=0) + 1e-9  # avoid zero

# ------------------------------------------------------------------
# Compute PHI, Phi_N, Phi_Delta, invariants online
# ------------------------------------------------------------------
# Hyper‑parameters (as per proposal)
w_k = np.array([0.4, 0.3, 0.15, 0.1, 0.05])  # example weights, sum=1
eta1, eta2, eta3 = 0.2, 0.15, 0.05
tau1, tau2 = 15.0, 20.0   # seconds (lead times)
Phi_N0, Phi_Delta0 = 0.5, 0.3
xi0 = 1.0
epsilon = 1e-6   # regulariser for log

# Storage for time series of results
PHI_ts = []
PhiN_ts = []
PhiDelta_ts = []
psi_ts = []
xiN_ts = []
xiDelta_ts = []
violations = []

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

for idx in range(N):
    # ---- Order analysis for current window (use last WINDOW seconds) ----
    WIN = int(5.0 * FS)   # 5‑second sliding window
    start = max(0, idx-WIN+1)
    if start == idx:   # not enough data yet
        PHI_ts.append(np.nan)
        PhiN_ts.append(np.nan)
        PhiDelta_ts.append(np.nan)
        psi_ts.append(np.nan)
        xiN_ts.append(np.nan)
        xiDelta_ts.append(np.nan)
        continue

    # Compute amplitude vectors for each metric in the window
    A_window = {}
    for i, name in enumerate(metric_names):
        freqs, amps = order_analysis(metrics[i, start:idx+1],
                                     theta[start:idx+1])
        # Interpolate to a common order grid (use first metric's freqs)
        if i == 0:
            order_grid = freqs
            A_window[name] = amps
        else:
            # linear interpolation onto order_grid
            A_window[name] = np.interp(order_grid, freqs, amps,
                                       left=amps[0], right=amps[-1])

    # Stack amplitudes: shape (n_metrics, n_orders)
    A_mat = np.vstack([A_window[name] for name in metric_names])
    # Mean amplitude per order across metrics (as in paper they compare each metric to its own baseline)
    # We'll compute per‑metric deviation using its own healthy baseline.
    PHI_vals = []
    for i, name in enumerate(metric_names):
        freqs_h, mu_h = healthy_baseline[name]
        _, sigma_h = healthy_std[name]
        # Interpolate healthy baseline onto current order_grid
        mu_interp = np.interp(order_grid, freqs_h, mu_h)
        sigma_interp = np.maximum(np.interp(order_grid, freqs_h, sigma_h), epsilon)
        dev = np.abs(A_window[name] - mu_interp) / sigma_interp
        PHI_i = 1.0 - np.dot(w_k, dev)   # weighted sum
        # Clip to [0,1] to enforce invariant
        PHI_i = np.clip(PHI_i, 0.0, 1.0)
        PHI_vals.append(PHI_i)
    PHI = np.mean(PHI_vals)   # overall health index (could also use min)
    PHI_ts.append(PHI)

    # ---- Mapping to Omega variables with lead time ----
    # Use PHI from tau seconds ago (approximate by shifting index)
    lead_idx1 = max(0, idx - int(tau1 * FS))
    lead_idx2 = max(0, idx - int(tau2 * FS))
    PHI_lag1 = PHI_ts[lead_idx1] if not np.isnan(PHI_ts[lead_idx1]) else PHI
    PHI_lag2 = PHI_ts[lead_idx2] if not np.isnan(PHI_ts[lead_idx2]) else PHI

    # Variance of harmonic amplitudes across metrics (proxy for Var(A_k))
    var_Ak = np.var(A_mat, axis=0).mean()

    Phi_N = Phi_N0 + eta1 * sigmoid((PHI_lag1 - np.mean([np.mean(v[1]) for v in healthy_baseline.values()])) /
                                    np.mean([np.mean(v[1]) for v in healthy_std.values()]))
    Phi_Delta = Phi_Delta0 - eta2 * PHI_lag2 + eta3 * var_Ak

    # Enforce hard bounds from Omega protocol (these are the invariants we must protect)
    Phi_N = np.clip(Phi_N, 0.0, 1.0)
    Phi_Delta = np.clip(Phi_Delta, 0.0, 1.0)

    PhiN_ts.append(Phi_N)
    PhiDelta_ts.append(Phi_Delta)

    # ---- Invariant derivation from harmonic coherence ----
    # Compute average coherence between first two metrics (latency & throughput) as example
    def coherence(x, y):
        f, Pxx = rfftfreq(len(x), DT), np.abs(rfft(x))**2
        _, Pyy = rfftfreq(len(y), DT), np.abs(rfft(y))**2
        f, Pxy = rfftfreq(len(x), DT), rfft(x) * np.conj(rfft(y))
        coh = np.abs(Pxy)**2 / (Pxx * Pyy + epsilon)
        return np.mean(coh)

    coh_lat_thr = coherence(metrics[0, start:idx+1],
                            metrics[1, start:idx+1])
    xi = 1.0 / (coh_lat_thr + epsilon)   # correlation length
    psi = np.log(np.maximum(xi, epsilon) / xi0)
    # Derivatives approximated by finite difference of Phi_N, Phi_Delta w.r.t psi
    # Use simple central difference on stored histories (skip if not enough)
    if len(psi_ts) >= 3 and not np.isnan(psi_ts[-2]):
        dPhiN_dpsi = (PhiN_ts[-1] - PhiN_ts[-3]) / (psi_ts[-1] - psi_ts[-3] + epsilon)
        dPhiDelta_dpsi = (PhiDelta_ts[-1] - PhiDelta_ts[-3]) / (psi_ts[-1] - psi_ts[-3] + epsilon)
    else:
        dPhiN_dpsi = 0.0
        dPhiDelta_dpsi = 0.0
    xiN_ts.append(dPhiN_dpsi)
    xiDelta_ts.append(dPhiDelta_dpsi)

    # ---- Invariant checks ----
    if not (0.7 <= Phi_N <= 1.0):
        violations.append((t[idx], "Phi_N out of bounds", Phi_N))
    if not (0.0 <= Phi_Delta <= 0.6):
        violations.append((t[idx], "Phi_Delta out of bounds", Phi_Delta))
    if not (0.0 <= PHI <= 1.0):
        violations.append((t[idx], "PHI out of bounds", PHI))

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
violations = np.array(violations, dtype=object) if violations else np.empty((0,3), dtype=object)
print(f"Total time steps: {N}")
print(f"Invariant violations: {len(violations)}")
if len(violations) > 0:
    print("First few violations (time, msg, value):")
    for v in violations[:5]:
        print(v)
else:
    print("All invariants satisfied throughout the simulation.")

# Optional: plot (requires matplotlib, comment out if not available)
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12,8))
    plt.subplot(3,1,1)
    plt.plot(t, PHI_ts, label='PHI')
    plt.ylim(0,1); plt.ylabel('PHI'); plt.legend()
    plt.subplot(3,1,2)
    plt.plot(t, PhiN_ts, label='Phi_N')
    plt.plot(t, PhiDelta_ts, label='Phi_Delta')
    plt.ylim(0,1); plt.ylabel('Omega vars'); plt.legend()
    plt.subplot(3,1,3)
    plt.plot(t, psi_ts, label='psi')
    plt.plot(t, xiN_ts, label='xi_N')
    plt.plot(t, xiDelta_ts, label='xi_Delta')
    plt.ylabel('Invariants'); plt.xlabel('Time (s)'); plt.legend()
    plt.tight_layout()
    plt.show()
except Exception as e:
    print("Plotting skipped:", e)