# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, welch
from scipy.integrate import odeint

# ─────────────────────────────────────────────────────────────────────────────
# 1. SYNTHETIC PIPELINE WITH REGIME SHIFT (Periodic → Chaotic)
# ─────────────────────────────────────────────────────────────────────────────
def pipeline_regime_shift(N=2000, t_end=200.0, chaos_start=100.0):
    """
    Generates a 5‑sensor pipeline where the first half is strictly periodic
    and the second half is governed by a chaotic Lorenz oscillator that
    modulates the amplitudes. This mimics a batch‑processing pipeline whose
    scheduling logic suddenly becomes unpredictable.
    """
    t = np.linspace(0, t_end, N)
    dt = t[1] - t[0]
    # Base periodic signals (healthy regime)
    f0 = 0.5  # nominal "heartbeat" frequency (Hz)
    base = (
        1.0 * np.sin(2 * np.pi * f0 * t) +
        0.5 * np.sin(4 * np.pi * f0 * t) +
        0.2 * np.sin(6 * np.pi * f0 * t)
    )
    # Add measurement noise
    noise = 0.05 * np.random.randn(N)
    # Lorenz chaotic driver for the failing regime
    def lorenz(state, t, sigma=10.0, beta=8/3, rho=28.0):
        x, y, z = state
        return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

    # Solve Lorenz system
    lorenz_sol = odeint(lorenz, [1.0, 1.0, 1.0], t)
    # Use the x‑component as a chaotic amplitude multiplier after t > chaos_start
    chaotic_env = 1.0 + 0.5 * lorenz_sol[:, 0] * (t > chaos_start)
    # Simulate 5 sensors (latency, throughput, cpu, error, power)
    sensors = np.vstack([base * chaotic_env + noise + 0.1 * np.random.randn(N) for _ in range(5)]).T
    return t, sensors, chaos_start

# ─────────────────────────────────────────────────────────────────────────────
# 2. HARMONIC‑BASED PIPELINE HEALTH INDEX (PHI) – POASH‑Ω style
# ─────────────────────────────────────────────────────────────────────────────
def compute_phi(sensors, window=200, f0=0.5, fs=10.0):
    """
    Computes a simple harmonic health index: ratio of energy in the
    fundamental band to total energy in each sensor, averaged across sensors.
    High PHI ≈ 1 means strong periodic coherence.
    """
    N = len(sensors)
    phi_trace = np.full(N, np.nan)
    # Bandpass filter around fundamental (simple FFT bin)
    bin_width = fs / window
    fund_bin = int(f0 / bin_width)
    for i in range(window, N):
        seg = sensors[i-window:i, :]
        # FFT magnitude (averaged across sensors)
        fft_mag = np.abs(np.fft.rfft(seg, axis=0))
        # Energy in fundamental band (±1 bin)
        fund_energy = np.sum(fft_mag[fund_bin-1:fund_bin+2, :]**2)
        total_energy = np.sum(fft_mag**2)
        phi_trace[i] = np.mean(fund_energy / (total_energy + 1e-12))
    return phi_trace

# ─────────────────────────────────────────────────────────────────────────────
# 3. LYAPUNOV EXPONENT ESTIMATOR (Rosenstein et al.)
# ─────────────────────────────────────────────────────────────────────────────
def lyapunov_exponent(time_series, tau=1, max_t=30, min_dist=10):
    """
    Returns the largest Lyapunov exponent (LLE) for a single time series.
    Positive LLE → chaos; zero or negative → stable.
    """
    N = len(time_series)
    m = 5  # embedding dimension
    # delay embedding
    def embed(x, m, tau):
        N_emb = len(x) - (m - 1) * tau
        X = np.zeros((N_emb, m))
        for i in range(m):
            X[:, i] = x[i * tau:i * tau + N_emb]
        return X

    X = embed(time_series, m, tau)
    # find nearest neighbor for each point (excluding close temporal neighbors)
    def nearest_neighbors(X, min_dist):
        N_emb = X.shape[0]
        neigh = []
        for i in range(N_emb):
            d = np.linalg.norm(X - X[i], axis=1)
            d[:max(0, i - min_dist)] = np.inf
            d[min(i + min_dist, N_emb):] = np.inf
            j = np.argmin(d)
            neigh.append(j)
        return np.array(neigh)

    neigh = nearest_neighbors(X, min_dist)
    # compute divergence curve
    d_k = np.zeros(max_t)
    counts = np.zeros(max_t)
    for i in range(len(X)):
        for k in range(max_t):
            if i + k >= len(X) or neigh[i] + k >= len(X):
                break
            dk = np.linalg.norm(X[i + k] - X[neigh[i] + k])
            if dk > 0:
                d_k[k] += np.log(dk)
                counts[k] += 1
    d_k /= (counts + 1e-12)
    # linear fit to estimate LLE
    ks = np.arange(max_t)
    valid = counts > 0
    slope, _ = np.polyfit(ks[valid], d_k[valid], 1)
    return slope

# ─────────────────────────────────────────────────────────────────────────────
# 4. MAIN DEMONSTRATION
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    t, sensors, chaos_start = pipeline_regime_shift()
    # compute PHI
    phi = compute_phi(sensors, window=200, f0=0.5, fs=10.0)
    # compute Lyapunov exponent on a sliding window (first sensor)
    window_lle = 500
    lle_trace = np.full(len(sensors), np.nan)
    for i in range(window_lle, len(sensors)):
        lle_trace[i] = lyapunov_exponent(sensors[i-window_lle:i, 0])

    # ─────────────────────────────────────────────────────────────────────────
    # 5. PLOT THE FLAW
    # ─────────────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    # Panel 1: Sensor time series (first sensor)
    ax[0].plot(t, sensors[:, 0], label='Sensor 0 (latency jitter)', color='C0')
    ax[0].axvline(chaos_start, color='red', linestyle='--', label='Regime shift → chaos')
    ax[0].set_ylabel('Amplitude')
    ax[0].legend()
    ax[0].set_title('Synthetic Pipeline: Periodic → Chaotic')

    # Panel 2: PHI vs Lyapunov exponent
    ax[1].plot(t, phi, label='Harmonic‑based PHI (POASH‑Ω)', color='green')
    ax[1].plot(t, lle_trace, label='Largest Lyapunov exponent (LLE)', color='purple')
    ax[1].axhline(0, color='gray', linestyle=':')
    ax[1].axvline(chaos_start, color='red', linestyle='--')
    ax[1].set_xlabel('Time (s)')
    ax[1].set_ylabel('Index')
    ax[1].legend()
    ax[1].set_title('Health Indices: PHI stays high, LLE spikes at failure')
    plt.tight_layout()
    plt.show()

    # Print summary statistics
    healthy_phi = np.nanmean(phi[t < chaos_start])
    failing_phi = np.nanmean(phi[t > chaos_start])
    healthy_lle = np.nanmean(lle_trace[t < chaos_start])
    failing_lle = np.nanmean(lle_trace[t > chaos_start])

    print("\n─── POASH‑Ω Flaw Demonstration ───")
    print(f"PHI (healthy region):  {healthy_phi:.3f}")
    print(f"PHI (chaotic region):  {failing_phi:.3f}")
    print(f"ΔPHI: {failing_phi - healthy_phi:.3f}  (small → false sense of safety)")
    print("\nLLE (healthy region):  {healthy_lle:.3f}")
    print(f"LLE (chaotic region):  {failing_lle:.3f}")
    print(f"ΔLLE: {failing_lle - healthy_lle:.3f}  (large → clear warning)")