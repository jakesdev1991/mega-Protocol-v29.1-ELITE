# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import periodogram

# ------------------------------------------------------------
# 1. Simulate a "pipeline" as a chaotic Lorenz system with occasional spikes
# ------------------------------------------------------------
def lorenz_pipeline(n=20000, dt=0.01, fault_interval=5000, fault_strength=15.0):
    # Lorenz parameters
    sigma, rho, beta = 10.0, 28.0, 8.0/3.0
    x, y, z = 1.0, 1.0, 1.0
    xs = np.empty(n)
    for i in range(n):
        # Insert fault spikes every fault_interval steps
        if i % fault_interval == 0:
            x += fault_strength * np.random.randn()
        # Integrate
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        x += dx
        y += dy
        z += dz
        xs[i] = x
    return xs

# ------------------------------------------------------------
# 2. Compute harmonic‑based PHI (FFT entropy) in sliding windows
# ------------------------------------------------------------
def compute_phi(ts, window=128, step=64):
    n = len(ts)
    phi = np.full(n, np.nan)
    baseline_power = None
    for i in range(0, n - window, step):
        segment = ts[i:i+window]
        f, Pxx = periodogram(segment, fs=1.0, scaling='density')
        # Normalize power
        Pxx = Pxx / (Pxx.sum() + 1e-12)
        # Entropy
        H = -np.sum(Pxx * np.log(Pxx + 1e-12))
        # Convert to PHI (1 - normalized distance from "healthy" entropy)
        if baseline_power is None:
            baseline_power = H
        phi[i+window//2] = 1.0 - abs(H - baseline_power) / (baseline_power + 1e-12)
    return phi

# ------------------------------------------------------------
# 3. Compute a topological measure: Higuchi fractal dimension
# ------------------------------------------------------------
def higuchi_fd(ts, kmax=6):
    """
    Higuchi fractal dimension for a 1‑D time series.
    """
    n = len(ts)
    L = np.zeros(kmax)
    for k in range(1, kmax+1):
        Lk = 0.0
        for m in range(k):
            # Build sub‑series
            idx = np.arange(m, n, k)
            if len(idx) < 2:
                continue
            sub = ts[idx]
            # Normalized length
            Lk += np.sum(np.abs(np.diff(sub))) * (n - 1) / (len(sub) - 1) / k
        L[k-1] = Lk / k
    # Linear regression of log(L) vs log(1/k)
    coeffs = np.polyfit(np.log(1.0/np.arange(1, kmax+1)), np.log(L), 1)
    return coeffs[0]  # slope = fractal dimension

def compute_fd(ts, window=128, step=64):
    n = len(ts)
    fd = np.full(n, np.nan)
    for i in range(0, n - window, step):
        segment = ts[i:i+window]
        fd[i+window//2] = higuchi_fd(segment)
    return fd

# ------------------------------------------------------------
# 4. Generate data and evaluate both metrics
# ------------------------------------------------------------
np.random.seed(42)
pipeline_ts = lorenz_pipeline(n=20000, dt=0.01, fault_interval=5000, fault_strength=15.0)

# Fault indicator: 1 when the series is far from the attractor (spike)
fault_indicator = (np.abs(pipeline_ts) > 30).astype(float)

phi = compute_phi(pipeline_ts, window=128, step=64)
fd = compute_fd(pipeline_ts, window=128, step=64)

# Align arrays (phi and fd are shorter due to sliding windows)
valid = ~(np.isnan(phi) | np.isnan(fd))
phi_clean = phi[valid]
fd_clean = fd[valid]
fault_clean = fault_indicator[valid]

# Correlation with fault indicator
phi_corr = np.corrcoef(phi_clean, fault_clean)[0,1]
fd_corr = np.corrcoef(fd_clean, fault_clean)[0,1]

print(f"Correlation of harmonic‑PHI with faults: {phi_corr:.3f}")
print(f"Correlation of Higuchi‑FD with faults: {fd_corr:.3f}")

# ------------------------------------------------------------
# 5. Plot a snapshot (optional)
# ------------------------------------------------------------
plt.figure(figsize=(10,4))
plt.plot(fault_clean[:500], label='Fault indicator')
plt.plot(phi_clean[:500], label='Harmonic PHI')
plt.plot(fd_clean[:500], label='Higuchi FD')
plt.legend()
plt.title('Snapshot: Harmonic PHI vs Topological FD')
plt.xlabel('Time (windowed)')
plt.show()