# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.signal import periodogram
from scipy.stats import levy_stable

# --------------------------------------------------------------
# 1. Simulate a realistic financial data pipeline with heavy‑tailed,
#    non‑periodic batch arrivals (no fixed “rotation”).
# --------------------------------------------------------------
def generate_pipeline_trace(duration_sec=600, avg_batch_rate=10.0):
    """
    Generate timestamps and synthetic sensor metrics.
    Batch inter‑arrival times follow a stable distribution (heavy tails).
    """
    # heavy‑tailed inter‑arrival (α=1.5, β=0)
    intervals = levy_stable.rvs(alpha=1.5, beta=0, size=int(duration_sec*avg_batch_rate*2))
    # Ensure positivity
    intervals = np.abs(intervals)
    # Normalize to match average rate
    intervals = intervals / np.mean(intervals) / avg_batch_rate
    # Generate timestamps
    timestamps = np.cumsum(intervals)
    timestamps = timestamps[timestamps < duration_sec]
    
    # Sensor metrics: latency jitter, throughput, CPU load, error rate
    # Each metric is a noisy function of the instantaneous inter‑arrival
    n = len(timestamps)
    latency = 0.5 + 0.1*np.random.randn(n) + 0.05*levy_stable.rvs(alpha=1.8, beta=0, size=n)
    throughput = 1.0 / (intervals[:n] + 0.01) + 0.2*np.random.randn(n)
    cpu = 0.3 + 0.4*(throughput / np.max(throughput)) + 0.1*np.random.randn(n)
    error_rate = np.maximum(0, 0.01 + 0.005*np.random.randn(n) + 0.002*(latency > 1.0))
    
    # Inject a fault at t=300s (spike in latency & errors)
    fault_idx = np.searchsorted(timestamps, 300)
    latency[fault_idx:fault_idx+20] += np.linspace(0, 3, 20)
    error_rate[fault_idx:fault_idx+20] += np.linspace(0, 0.05, 20)
    
    return timestamps, latency, throughput, cpu, error_rate

# --------------------------------------------------------------
# 2. POASH‑Ω “order analysis” on a *fixed* 1‑second grid.
#    This is the flawed step: pretending a periodic phase exists.
# --------------------------------------------------------------
def compute_phi_fixed_grid(timestamps, *metrics, fs=1.0):
    """
    Resample each metric onto a uniform grid (fs) and compute FFT
    to obtain harmonic amplitudes A_k. Then compute PHI as defined.
    """
    # Create uniform time axis
    t_max = timestamps[-1]
    t_grid = np.arange(0, t_max, 1/fs)
    phi_values = []
    for metric in metrics:
        # Interpolate metric onto uniform grid
        f_interp = interp1d(timestamps, metric, kind='linear', fill_value='extrapolate')
        y_grid = f_interp(t_grid)
        # Remove mean to avoid DC bias
        y_grid -= np.mean(y_grid)
        # Compute periodogram (squared magnitude of FFT)
        f, Pxx = periodogram(y_grid, fs=fs, scaling='density')
        # Harmonic amplitudes (sqrt of power)
        A = np.sqrt(Pxx)
        # Normalized power distribution
        power = A**2
        if np.sum(power) == 0:
            phi_values.append(0.0)
            continue
        p = power / np.sum(power)
        # Shannon entropy
        I = -np.sum(p * np.log(p + 1e-12))
        # PHI = 1 - I / log(N)  (scaled to [0,1])
        N = len(p)
        phi = 1.0 - I / np.log(N)
        phi_values.append(phi)
    return np.mean(phi_values)

# --------------------------------------------------------------
# 3. Multifractal alternative: compute the singularity spectrum f(α)
#    from inter‑arrival times (no periodic assumption).
# --------------------------------------------------------------
def multifractal_spectrum(intervals, qvals=np.arange(-5, 5.1, 0.5)):
    """
    Compute the multifractal spectrum f(α) using the method of moments.
    Returns the most probable α (peak of f(α)) as a simple health indicator.
    """
    # Build the partition function Z(q,s) for multiple scales s
    scales = np.logspace(0.5, 2.5, 30).astype(int)
    Z = np.zeros((len(qvals), len(scales)))
    for i, q in enumerate(qvals):
        for j, s in enumerate(scales):
            # Partition the series into boxes of size s
            nbox = len(intervals) // s
            if nbox == 0:
                Z[i, j] = np.nan
                continue
            boxes = intervals[:nbox*s].reshape(nbox, s)
            # Box sum (integrated series)
            box_sum = np.sum(boxes, axis=1)
            # Moment
            if q == 0:
                Z[i, j] = np.sum(np.log(np.abs(box_sum) + 1e-12))
            else:
                Z[i, j] = np.sum(np.abs(box_sum)**q)
    # Compute scaling exponents τ(q) from log‑log regression
    tau = np.zeros_like(qvals, dtype=float)
    for i, q in enumerate(qvals):
        valid = ~np.isnan(Z[i, :])
        if np.sum(valid) < 3:
            tau[i] = np.nan
            continue
        coeff = np.polyfit(np.log(scales[valid]), np.log(Z[i, valid]), 1)
        tau[i] = coeff[0]
    # Legendre transform to get α and f(α)
    # α(q) = dτ/dq, f(α) = q*α - τ(q)
    # Use finite differences
    dq = qvals[1] - qvals[0]
    alpha = np.gradient(tau, dq)
    f_alpha = qvals * alpha - tau
    # Return the α at maximum f(α) (most common singularity)
    peak_idx = np.nanargmax(f_alpha)
    return alpha[peak_idx], f_alpha[peak_idx]

# --------------------------------------------------------------
# 4. Run simulation and compare POASH‑Ω PHI vs multifractal indicator.
# --------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    timestamps, latency, throughput, cpu, error_rate = generate_pipeline_trace(duration_sec=600)
    
    # Compute POASH‑Ω PHI on a sliding window (60‑second windows)
    window_sec = 60
    phi_series = []
    for start in np.arange(0, 540, 5):
        end = start + window_sec
        mask = (timestamps >= start) & (timestamps < end)
        if np.sum(mask) < 10:
            phi_series.append(np.nan)
            continue
        t_win = timestamps[mask]
        # Shift to relative time for interpolation stability
        t_win -= t_win[0]
        lat_win = latency[mask]
        thr_win = throughput[mask]
        cpu_win = cpu[mask]
        err_win = error_rate[mask]
        phi = compute_phi_fixed_grid(t_win, lat_win, thr_win, cpu_win, err_win, fs=1.0)
        phi_series.append(phi)
    
    # Compute multifractal indicator (peak alpha) on the same windows
    mf_alpha_series = []
    for start in np.arange(0, 540, 5):
        end = start + window_sec
        mask = (timestamps >= start) & (timestamps < end)
        if np.sum(mask) < 10:
            mf_alpha_series.append(np.nan)
            continue
        # Use inter‑arrival intervals within the window
        intervals = np.diff(timestamps[mask])
        if len(intervals) < 20:
            mf_alpha_series.append(np.nan)
            continue
        alpha_peak, _ = multifractal_spectrum(intervals)
        mf_alpha_series.append(alpha_peak)
    
    # Plot comparison
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    time_axis = np.arange(0, 540, 5)[:len(phi_series)]
    ax[0].plot(time_axis, phi_series, label='POASH‑Ω PHI (fixed‑grid)', marker='o')
    ax[0].axvline(300, color='r', linestyle='--', label='Injected fault')
    ax[0].set_ylabel('PHI')
    ax[0].legend()
    ax[0].grid(True)
    
    ax[1].plot(time_axis, mf_alpha_series, label='Multifractal α_peak', marker='s', color='green')
    ax[1].axvline(300, color='r', linestyle='--', label='Injected fault')
    ax[1].set_xlabel('Time (s)')
    ax[1].set_ylabel('Peak singularity α')
    ax[1].legend()
    ax[1].grid(True)
    
    plt.suptitle('POASH‑Ω vs Multifractal Health Indicator on Realistic Pipeline')
    plt.tight_layout()
    plt.show()
    
    # Simple predictive power check: compute correlation between indicator
    # and a binary fault flag (1 if within 30s after fault onset)
    fault_flag = np.array([1 if 300 <= t < 330 else 0 for t in time_axis])
    phi_arr = np.array(phi_series)
    mf_arr = np.array(mf_alpha_series)
    # Drop NaNs
    valid = ~(np.isnan(phi_arr) | np.isnan(mf_arr))
    phi_valid = phi_arr[valid]
    mf_valid = mf_arr[valid]
    fault_valid = fault_flag[valid]
    
    phi_corr = np.corrcoef(phi_valid, fault_valid)[0,1] if len(phi_valid) > 1 else np.nan
    mf_corr = np.corrcoef(mf_valid, fault_valid)[0,1] if len(mf_valid) > 1 else np.nan
    
    print(f"Correlation with fault (POASH‑Ω): {phi_corr:.3f}")
    print(f"Correlation with fault (Multifractal): {mf_corr:.3f}")