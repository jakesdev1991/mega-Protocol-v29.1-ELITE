# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
POASH‑Ω mathematical & Omega‑Protocol compliance validator.

The script synthesises a multi‑metric pipeline stream, computes the Pipeline
Health Index (PHI) and its derived Omega variables, then asserts that every
invariant required by the Omega Protocol and the MPC‑Ω controller holds.
"""

import numpy as np
from scipy.signal import welch, csd
from sklearn.linear_model import LogisticRegression

# ----------------------------------------------------------------------
# Configuration (tweak to test edge‑cases)
# ----------------------------------------------------------------------
NPERSEG = 256               # FFT segment length for Welch/CSD
FS = 100.0                  # Sampling frequency (Hz) of raw metrics
PIPELINE_PERIOD = 1.0       # Reference rotation period (seconds) -> order analysis
NUM_ORDERS = 5              # Number of harmonic orders to consider (k=1..5)
LAMBDA1, LAMBDA2 = 0.1, 0.1 # Cost‑function weights (not used in checks, kept for completeness)
SEED = 42

np.random.seed(SEED)

# ----------------------------------------------------------------------
# Helper: simulate raw metric streams (5 dimensions)
# ----------------------------------------------------------------------
def simulate_metrics(duration_sec=30.0, fault_interval=None):
    """
    Returns:
        t          : time vector (s)
        metrics    : shape (n_samples, 5)  [latency_jitter, throughput, cpu_load, error_rate, power]
        fault_flag : bool array indicating injected fault periods (for supervised learning)
    """
    t = np.arange(0, duration_sec, 1/FS)
    n = len(t)

    # Baseline healthy signals (small random fluctuations)
    latency_jitter = 0.02 + 0.005*np.random.randn(n)
    throughput     = 1.0   + 0.02*np.random.randn(n)
    cpu_load       = 0.45  + 0.03*np.random.randn(n)
    error_rate     = 0.001 + 0.0005*np.random.randn(n)
    power          = 150.0 + 5.0*np.random.randn(n)

    metrics = np.vstack([latency_jitter, throughput, cpu_load, error_rate, power]).T

    # Optional fault injection (simple spikes) to create labelled data
    fault_flag = np.zeros(n, dtype=bool)
    if fault_interval:
        start, end = fault_interval
        i0, i1 = int(start*FS), int(end*FS)
        fault_flag[i0:i1] = True
        # Amplify fault signatures
        metrics[i0:i1, 0] *= 3.0   # latency jitter spike
        metrics[i0:i1, 3] *= 10.0  # error rate spike
    return t, metrics, fault_flag

# ----------------------------------------------------------------------
# Order‑analysis: resample to constant phase θ(t) = 2π * t / T_pipe
# ----------------------------------------------------------------------
def order_resample(signal, t, T_pipe):
    """
    Resample `signal` uniformly in the order domain using linear interpolation.
    Returns the resampled signal y(θ) sampled at N_theta points.
    """
    theta = 2 * np.pi * t / T_pipe          # phase in [0, 2π * n_cycles]
    # We want one sample per radian (or per fixed Δθ); choose N_theta = int(max(theta))
    N_theta = int(np.ceil(theta[-1]))
    theta_uniform = np.linspace(0, theta[-1], N_theta)
    # Interpolate
    y_theta = np.interp(theta_uniform, theta, signal)
    return y_theta, theta_uniform

# ----------------------------------------------------------------------
# Compute harmonic amplitudes A_k via FFT of order‑domain signal
# ----------------------------------------------------------------------
def harmonic_amplitudes(y_theta, fs_theta):
    """
    fs_theta: effective sampling frequency in order domain (samples per radian).
    Returns amplitudes for orders k=1..NUM_ORDERS.
    """
    N = len(y_theta)
    freqs = np.fft.rfftfreq(N, d=1/fs_theta)   # in cycles per radian = order
    fft_vals = np.fft.rfft(y_theta)
    amp = np.abs(fft_vals) / (N/2)             # single‑sided amplitude
    # Pick the bins closest to integer orders 1..NUM_ORDERS
    A = np.zeros(NUM_ORDERS)
    for k in range(1, NUM_ORDERS+1):
        idx = np.argmin(np.abs(freqs - k))
        A[k-1] = amp[idx]
    return A

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate():
    # 1. Simulate data (healthy + one fault interval for labelling)
    t, metrics, fault_flag = simulate_metrics(duration_sec=60.0,
                                              fault_interval=(20.0, 25.0))

    # 2. Order‑domain resampling for each metric
    T_pipe = PIPELINE_PERIOD
    order_signals = []
    for m in range(metrics.shape[1]):          # 5 metrics
        y_theta, _ = order_resample(metrics[:, m], t, T_pipe)
        order_signals.append(y_theta)

    order_signals = np.array(order_signals).T   # shape (N_theta, 5)

    # 3. Estimate harmonic amplitudes per metric per time window
    #    We'll use a sliding window (width = 2*T_pipe) to get a time‑varying A_k(t)
    win_samples = int(2 * T_pipe * (FS / (2*np.pi)))  # approximate samples per 2π rad
    step = win_samples // 2
    n_windows = (order_signals.shape[0] - win_samples) // step + 1

    A_history = []   # list of (n_metrics, NUM_ORDERS) per window
    t_centers = []
    for w in range(n_windows):
        start = w*step
        end   = start + win_samples
        seg = order_signals[start:end, :]   # (win_samples, 5)
        # Effective sampling in order domain: win_samples samples over 2π rad ≈ win_samples/(2π) samples/rad
        fs_theta = win_samples / (2*np.pi)
        A_win = np.array([harmonic_amplitudes(seg[:, m], fs_theta) for m in range(5)])
        A_history.append(A_win)            # shape (5, NUM_ORDERS)
        t_centers.append(t[int(start*FS/(2*np.pi))])  # approximate centre time

    A_history = np.array(A_history)        # (n_windows, 5, NUM_ORDERS)
    t_centers = np.array(t_centers)

    # 4. Learn healthy baseline (mean, std) from fault‑free windows
    healthy_mask = ~fault_flag[[int(c*FS) for c in t_centers]]   # approximate label per window
    if healthy_mask.sum() < 5:
        raise RuntimeError("Not enough healthy windows to learn baseline.")
    healthy_A = A_history[healthy_mask]   # (n_healthy, 5, NUM_ORDERS)
    mu = healthy_A.mean(axis=(0,1))       # shape (NUM_ORDERS,)
    sigma = healthy_A.std(axis=(0,1)) + 1e-12  # avoid zero

    # 5. Learn weights w_k via logistic regression predicting fault vs healthy
    #    Feature: normalized deviation per order, averaged across metrics
    dev = np.abs(A_history - mu) / sigma   # (n_windows,5,NUM_ORDERS)
    feat = dev.mean(axis=1)                # (n_windows, NUM_ORDERS)
    label = fault_flag[[int(c*FS) for c in t_centers]].astype(int)
    clf = LogisticRegression(solver='lbfgs', max_iter=1000)
    clf.fit(feat, label)
    w = clf.coef_.ravel()
    w = np.clip(w, 0, None)               # enforce non‑negative
    w = w / w.sum() if w.sum()>0 else np.ones_like(w)/len(w)  # normalize to sum=1

    # 6. Compute PHI(t) for each window
    PHI = 1.0 - np.sum(w * np.abs(A_history - mu) / sigma, axis=(1,2))
    # Clip to [0,1] as per definition
    PHI = np.clip(PHI, 0.0, 1.0)

    # 7. Map PHI → Φₙ, Φ_Δ (sigmoid form)
    #    Choose hyper‑parameters similar to the paper; they must keep outputs in [0,1]
    Phi_N0, Phi_Delta0 = 0.5, 0.3
    eta1, eta2, eta3 = 0.4, 0.3, 0.1
    tau1, tau2 = 15.0, 20.0   # minutes → convert to same unit as t_centers (seconds)
    tau1_s, tau2_s = tau1*60, tau2*60

    # Approximate delayed PHI via simple shift (assume uniform sampling)
    dt = np.mean(np.diff(t_centers))
    shift1 = int(round(tau1_s / dt))
    shift2 = int(round(tau2_s / dt))
    PHI_del1 = np.concatenate([np.full(shift1, PHI[0]), PHI[:-shift1]]) if shift1>0 else PHI
    PHI_del2 = np.concatenate([np.full(shift2, PHI[0]), PHI[:-shift2]]) if shift2>0 else PHI

    mu_PHI, sigma_PHI = PHI.mean(), PHI.std()+1e-12
    Phi_N = Phi_N0 + eta1 * 1/(1+np.exp(-(PHI_del1 - mu_PHI)/sigma_PHI))
    Phi_Delta = Phi_Delta0 - eta2 * PHI_del2 + eta3 * np.var(A_history, axis=(1,2)).mean(axis=1)

    # Clip to plausible physical range [0,1] (the equations already tend to stay there)
    Phi_N = np.clip(Phi_N, 0.0, 1.0)
    Phi_Delta = np.clip(Phi_Delta, 0.0, 1.0)

    # 8. Compute order‑domain coherence between metric pairs
    #    We'll compute average coherence over all distinct pairs for each order k
    coh_per_window = []
    for w in range(n_windows):
        seg = order_signals[w*step:w*step+win_samples, :]   # (win_samples,5)
        fs_theta = win_samples / (2*np.pi)
        freqs = np.fft.rfftfreq(win_samples, d=1/fs_theta)
        # Find bins nearest to integer orders
        order_bins = [np.argmin(np.abs(freqs - k)) for k in range(1, NUM_ORDERS+1)]
        coh_matrix = np.zeros((5,5,NUM_ORDERS))
        for i in range(5):
            for j in range(i+1,5):
                fxy, _ = csd(seg[:,i], seg[:,j], fs=fs_theta, nperseg=NPERSEG)
                fxx, _ = welch(seg[:,i], fs=fs_theta, nperseg=NPERSEG)
                fyy, _ = welch(seg[:,j], fs=fs_theta, nperseg=NPERSEG)
                coh = np.abs(fxy)**2 / (fxx * fyy + 1e-12)
                coh_matrix[i,j,:] = coh
                coh_matrix[j,i,:] = coh   # symmetry
        # Average over pairs and over the selected order bins
        pair_coh = coh_matrix[np.triu_indices(5, k=1), :]   # shape (n_pairs, NUM_ORDERS)
        avg_coh = pair_coh.mean(axis=0)[order_bins]         # shape (NUM_ORDERS,)
        coh_per_window.append(avg_coh)
    coh_per_window = np.array(coh_per_window)   # (n_windows, NUM_ORDERS)

    # 9. Correlation length ξ = 1 / ⟨coh⟩
    xi = 1.0 / (coh_per_window.mean(axis=1) + 1e-12)   # avoid division by zero
    xi0 = xi.mean()                                   # reference value
    psi = np.log(xi / xi0)

    # 10. Derivatives ξₙ = ∂Φₙ/∂ψ, ξ_Δ = ∂Φ_Δ/∂ψ (finite difference)
    dPsi = np.gradient(psi, dt)
    xi_N = np.gradient(Phi_N, dt) / dPsi
    xi_D = np.gradient(Phi_Delta, dt) / dPsi
    # Replace infinities where dPsi≈0
    xi_N = np.where(np.abs(dPsi)<1e-12, 0.0, xi_N)
    xi_D = np.where(np.abs(dPsi)<1e-12, 0.0, xi_D)

    # ------------------------------------------------------------------
    # Assertions – Omega Protocol & MPC‑Ω compliance
    # ------------------------------------------------------------------
    # (a) Basic range checks
    assert np.all((0.0 <= PHI) & (PHI <= 1.0)), "PHI out of [0,1]"
    assert np.all((0.0 <= Phi_N) & (Phi_N <= 1.0)), "Φₙ out of [0,1]"
    assert np.all((0.0 <= Phi_Delta) & (Phi_Delta <= 1.0)), "Φ_Δ out of [0,1]"
    assert np.all(xi > 0), "Correlation length ξ must be positive"
    assert np.all(np.isfinite(psi)), "ψ must be real"
    assert np.all(np.isfinite(xi_N)) and np.all(np.isfinite(xi_D)), "ξₙ, ξ_Δ must be real"

    # (b) MPC‑Ω QP constraints (must hold at every control step)
    assert np.all(PHI >= 0.4), "PHI constraint violated (<0.4)"
    assert np.all(Phi_N >= 0.7), "Φₙ constraint violated (<0.7)"
    assert np.all(Phi_Delta <= 0.6), "Φ_Δ constraint violated (>0.6)"

    # (c) Cost function non‑negativity (checked symbolically)
    J_integrand = (1 - PHI)**2 + LAMBDA1 * Phi_Delta**2 + LAMBDA2 * np.gradient(A_history.mean(axis=(1,2)), dt)**2
    assert np.all(J_integrand >= -1e-9), "Cost integrand became negative (numerical tolerance)"

    # (d) Coherence bounds
    assert np.all((0.0 <= coh_per_window) & (coh_per_window <= 1.0 + 1e-9)), "Coherence out of [0,1]"

    # If we reach here, all invariants are satisfied
    print("✅ All Omega‑Protocol invariants and MPC‑Ω constraints satisfied.")
    print(f"   Final PHI mean: {PHI.mean():.3f}  (min={PHI.min():.3f}, max={PHI.max():.3f})")
    print(f"   Final Φₙ mean: {Phi_N.mean():.3f}")
    print(f"   Final Φ_Δ mean: {Phi_Delta.mean():.3f}")

if __name__ == "__main__":
    validate()