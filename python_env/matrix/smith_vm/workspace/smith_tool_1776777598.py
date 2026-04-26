# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.signal import correlate
from scipy.optimize import curve_fit

# -------------------------------------------------
# Helper functions for Omega‑Protocol validation
# -------------------------------------------------
def phi_n(B, L, B_max=100.0, beta=0.5, L0=100.0):
    """Connectivity mode Φ_N(t)."""
    return (B / B_max) * np.exp(-beta * L / L0)

def phi_delta(B_cpu, B_gpu, F, gamma=0.1):
    """Asymmetry mode Φ_Δ(t)."""
    denom = B_cpu + B_gpu
    # avoid division by zero
    denom = np.where(denom == 0, 1e-12, denom)
    return np.abs(B_cpu - B_gpu) / denom + gamma * F

def autocorrelation_time(signal, dt=1e-3):
    """
    Estimate correlation time ξ from the autocorrelation function.
    Returns the lag where ACF drops to 1/e of its zero‑lag value.
    """
    n = len(signal)
    acf = correlate(signal, signal, mode='full')
    acf = acf[n-1:]                     # keep only non‑negative lags
    acf = acf / acf[0]                  # normalize
    # find first index where acf <= 1/e
    idx = np.where(acf <= np.exp(-1))[0]
    if idx.size == 0:
        return (n-1) * dt               # fallback: full length
    return idx[0] * dt

def exponential_decay(t, tau):
    return np.exp(-t / tau)

def fit_correlation_time(signal, dt=1e-3, max_lag=None):
    """
    Fit ACF to a single exponential to obtain ξ.
    More robust than the simple threshold method.
    """
    n = len(signal)
    acf = correlate(signal, signal, mode='full')
    acf = acf[n-1:] / acf[n-1]          # normalize
    lags = np.arange(len(acf)) * dt
    if max_lag is None:
        max_lag = lags[-1]
    mask = lags <= max_lag
    popt, _ = curve_fit(exponential_decay, lags[mask], acf[mask], p0=[0.01])
    return popt[0]                      # τ ≈ ξ

def compute_psi(xi_n, xi_delta):
    """Primary invariant ψ(t) = ln(ξ_Δ/ξ_N)."""
    return np.log(xi_delta / xi_n)

def third_derivative(signal, dt):
    """
    Third derivative using central finite differences.
    Returns array same length as input (edges set to NaN).
    """
    n = len(signal)
    d3 = np.full(n, np.nan)
    # central scheme: f'''(x) ≈ (f(x+2h)-2f(x+h)+2f(x-h)-f(x-2h))/(2h^3)
    for i in range(2, n-2):
        d3[i] = (signal[i+2] - 2*signal[i+1] + 2*signal[i-1] - signal[i-2]) / (2 * dt**3)
    return d3

def shannon_entropy(counts):
    """Entropy of a discrete distribution (counts per region)."""
    p = counts / counts.sum()
    p = p[p > 0]                         # avoid log(0)
    return -np.sum(p * np.log(p))

# -------------------------------------------------
# Synthetic HSA data generation (for validation)
# -------------------------------------------------
np.random.seed(42)
dt = 1e-3                     # 1 ms sampling
t = np.arange(0, 1.0, dt)    # 1 s window → 1000 samples
N = len(t)

# Baseline values
B_base = 40.0                 # GB/s
L_base = 50.0                 # ns
F_base = 100.0                # faults/s

# Simulate a memory‑pressure spike at t=0.5 s
spike_idx = int(0.5 / dt)
B = np.full(N, B_base)
L = np.full(N, L_base)
F = np.full(N, F_base)

# Spike shapes (Gaussian dips/peaks)
spike_width = 0.05            # 50 ms
B[spike_idx-20:spike_idx+20] = 10.0   # drop to 10 GB/s
L[spike_idx-20:spike_idx+20] = 200.0  # latency jump
F[spike_idx-20:spike_idx+20] = 5000.0 # fault surge

# Split bandwidth into CPU/GPU components (add some noise)
B_cpu = B * (0.5 + 0.1*np.random.randn(N))
B_gpu = B - B_cpu
B_cpu = np.maximum(B_cpu, 0.1)
B_gpu = np.maximum(B_gpu, 0.1)

# -------------------------------------------------
# Omega‑Protocol calculations
# -------------------------------------------------
Phi_N = phi_n(B, L)
Phi_Delta = phi_delta(B_cpu, B_gpu, F)

# Estimate stiffness invariants via exponential fit of ACF
xi_N = fit_correlation_time(Phi_N, dt, max_lag=0.05)   # look up to 50 ms
xi_Delta = fit_correlation_time(Phi_Delta, dt, max_lag=0.05)

# Primary invariant ψ(t)
psi = compute_psi(xi_N, xi_Delta)   # note: xi_N/Δ are scalars here; for time‑varying we would recompute per window

# For a time‑varying ψ we need sliding‑window ξ estimates.
window_len = int(0.1 / dt)   # 100 ms windows
psi_series = np.full(N, np.nan)
xi_N_series = np.full(N, np.nan)
xi_D_series = np.full(N, np.nan)

for start in range(0, N - window_len + 1, window_len//2):  # 50 % overlap
    end = start + window_len
    xi_n_win = fit_correlation_time(Phi_N[start:end], dt, max_lag=0.05)
    xi_d_win = fit_correlation_time(Phi_Delta[start:end], dt, max_lag=0.05)
    psi_win = np.log(xi_d_win / xi_n_win)
    xi_N_series[start:end] = xi_n_win
    xi_D_series[start:end] = xi_d_win
    psi_series[start:end] = psi_win

# Trim NaNs at edges
valid = ~np.isnan(psi_series)
psi_valid = psi_series[valid]
t_valid = t[valid]
dt_valid = np.diff(t_valid)[0]   # assumes uniform sampling

# Jerk J = d³ψ/dt³
J = third_derivative(psi_valid, dt_valid)

# Curvature‑based critical jerk (using the *local* ξ estimates)
J_crit_series = 1.0 / (xi_N_series[valid]**2 * xi_D_series[valid])
J_crit = np.nanmedian(J_crit_series)   # representative value

# Entropy bound: need page‑fault distribution per region.
# Simulate 16 memory regions, each receiving a share of faults.
n_regions = 16
fault_counts = np.random.poisson(lam=F[:, None] / n_regions, size=(N, n_regions))
# Compute entropy time‑series
S_F_series = np.array([shannon_entropy(fault_counts[i,:]) for i in range(N)])
# Align with valid psi indices
S_F_valid = S_F_series[valid]
dS_F_dt = np.gradient(S_F_valid, dt_valid)
kappa = 0.1   # s² from calibration
entropy_bound = kappa * np.abs(dS_F_dt)

# -------------------------------------------------
# Validation report
# -------------------------------------------------
print("=== Omega‑Protocol Jerk‑Stability Validation ===")
print(f"Samples processed: {N} ({dt*1e3:.1f} ms each)")
print(f"Estimated ξ_N: {xi_N*1e3:.2f} ms")
print(f"Estimated ξ_Δ: {xi_Delta*1e3:.2f} ms")
print(f"Median ψ: {np.nanmedian(psi_valid):.4f}")
print(f"Jerk statistics: mean={np.nanmean(J):.2e}, std={np.nanstd(J):.2e}, max|J|={np.nanmax(np.abs(J)):.2e} s⁻³")
print(f"Curvature‑based J_crit ≈ {J_crit:.2e} s⁻³")
print(f"Entropy‑based bound (typical) ≈ {np.nanmedian(entropy_bound):.2e} s⁻³")
print()

# Check violations
curv_viol = np.nanmax(np.abs(J)) > J_crit
entr_viol = np.nanmax(np.abs(J)) > np.nanmax(entropy_bound)

print("Stability Checks:")
print(f"  Curvature bound satisfied? {'NO' if curv_viol else 'YES'}")
print(f"  Entropy bound satisfied?   {'NO' if entr_viol else 'YES'}")
if curv_viol or entr_viol:
    print("\n⚠️  Protocol violation detected – potential Shredding/Informational Freeze risk.")
else:
    print("\n✅  All Omega‑Protocol invariants respected within observation window.")