# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.signal as signal
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')  # ignore log(0) warnings

# ─────────────────────────────────────────────────────────────────────────────
# 1. Synthetic data generator
# ─────────────────────────────────────────────────────────────────────────────
def generate_histograms(n_blocks=64, n_steps=2000, hang_start=1500, seed=0):
    """
    Returns (cpu_hist, gpu_hist) as (n_steps, n_blocks) arrays.
    Stable regime (t < hang_start): Dirichlet(α=1) → near‑uniform.
    Pre‑hang regime (t >= hang_start): Dirichlet(α=10 for first 5 blocks, α=1 else) → skewed.
    """
    rng = np.random.default_rng(seed)
    cpu_hist = np.empty((n_steps, n_blocks))
    gpu_hist = np.empty((n_steps, n_blocks))
    for t in range(n_steps):
        if t < hang_start:
            alpha_cpu = np.ones(n_blocks)
            alpha_gpu = np.ones(n_blocks)
        else:
            alpha_cpu = np.ones(n_blocks)
            alpha_gpu = np.ones(n_blocks)
            # skew GPU accesses toward first few blocks
            alpha_gpu[:5] = 10.0
        cpu_hist[t] = rng.dirichlet(alpha_cpu) * 1000  # scale to counts
        gpu_hist[t] = rng.dirichlet(alpha_gpu) * 1000
    return cpu_hist, gpu_hist

# ─────────────────────────────────────────────────────────────────────────────
# 2. Entropy & “informational jerk” pipeline
# ─────────────────────────────────────────────────────────────────────────────
def shannon_entropy(hist):
    """Compute Shannon entropy (bits) for a histogram (counts)."""
    p = hist / hist.sum()
    p = p[p > 0]
    return -np.sum(p * np.log2(p))

def compute_jerk_pipeline(cpu_hist, gpu_hist, dt=1e-3, sg_window=11, sg_poly=3):
    """
    Returns smoothed total entropy and jerk time series.
    """
    n_steps = cpu_hist.shape[0]
    I_total = np.array([shannon_entropy(cpu_hist[t]) + shannon_entropy(gpu_hist[t])
                        for t in range(n_steps)])
    # Savitzky‑Golay smoothing
    I_smooth = signal.savgol_filter(I_total, sg_window, sg_poly)
    # Central‑difference third derivative (inner points only)
    J = np.full(n_steps, np.nan)
    for t in range(2, n_steps - 2):
        J[t] = (-I_smooth[t - 2] + 2 * I_smooth[t - 1] -
                2 * I_smooth[t + 1] + I_smooth[t + 2]) / (2 * dt**3)
    return I_smooth, J

# ─────────────────────────────────────────────────────────────────────────────
# 3. Critical slowing‑down ratio R(t) = ρ₁ / ρ₁₀
# ─────────────────────────────────────────────────────────────────────────────
def autocorr_ratio(I_total, window=100, lag1=1, lag10=10):
    """
    Compute sliding‑window ratio of autocorrelation at lag1 vs lag10.
    """
    n = len(I_total)
    R = np.full(n, np.nan)
    for t in range(window, n):
        seq = I_total[t - window:t]
        # demean
        seq = seq - np.mean(seq)
        # compute autocorrelation via FFT for speed
        norm = np.sum(seq**2)
        if norm == 0:
            continue
        # correlation with lag k = ∑ x[i] x[i+k] / ∑ x[i]^2
        rho = np.correlate(seq, seq, mode='full')[window - 1:] / norm
        # extract lags
        rho1 = rho[lag1] if lag1 < len(rho) else np.nan
        rho10 = rho[lag10] if lag10 < len(rho) else np.nan
        if rho10 != 0:
            R[t] = rho1 / rho10
    return R

# ─────────────────────────────────────────────────────────────────────────────
# 4. Main experiment
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # generate data
    cpu_hist, gpu_hist = generate_histograms()

    # compute entropy & jerk pipeline
    I_smooth, J = compute_jerk_pipeline(cpu_hist, gpu_hist)

    # compute RMS jerk over sliding window (same length as R)
    window = 100
    RMS_J = np.full_like(J, np.nan)
    for t in range(window, len(J)):
        RMS_J[t] = np.sqrt(np.nanmean(J[t - window:t]**2))

    # compute critical slowing‑down ratio
    R = autocorr_ratio(I_smooth, window=window)

    # split stable vs pre‑hang periods
    hang_start = 1500
    stable = slice(0, hang_start)
    prehang = slice(hang_start, len(I_smooth))

    # print summary statistics
    print("=== Stable period (t < 1500) ===")
    print(f"RMS jerk mean ± std: {np.nanmean(RMS_J[stable]):.4f} ± {np.nanstd(RMS_J[stable]):.4f}")
    print(f"R ratio mean ± std: {np.nanmean(R[stable]):.4f} ± {np.nanstd(R[stable]):.4f}")

    print("\n=== Pre‑hang period (t >= 1500) ===")
    print(f"RMS jerk mean ± std: {np.nanmean(RMS_J[prehang]):.4f} ± {np.nanstd(RMS_J[prehang]):.4f}")
    print(f"R ratio mean ± std: {np.nanmean(R[prehang]):.4f} ± {np.nanstd(R[prehang]):.4f}")

    # show that R approaches 1 before hang
    print("\n=== Last 10 R values before hang ===")
    print(R[hang_start - 10:hang_start])

    # show that jerk spikes are noise‑driven
    print("\n=== Sample jerk values (first 20) ===")
    print(J[:20])