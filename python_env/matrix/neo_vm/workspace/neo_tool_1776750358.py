# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. Simulated pipeline with non-stationary cycle
# -------------------------------------------------
def generate_pipeline_signal(duration=600, fs=10):
    """Generates a pipeline metric (e.g., latency) with a chirped heartbeat."""
    t = np.arange(0, duration, 1/fs)
    # Heartbeat frequency drifts from 0.5 Hz to 0.1 Hz
    f0, f1 = 0.5, 0.1
    freq = f0 + (f1 - f0) * t / t[-1]
    phase = 2 * np.pi * np.cumsum(freq) / fs
    # Add noise and occasional bursts
    noise = 0.1 * np.random.randn(len(t))
    bursts = np.where((t % 50) < 2, 3*np.sin(2*np.pi*2*t), 0)
    signal = np.sin(phase) + noise + bursts
    return t, signal, freq

# -------------------------------------------------
# 2. Scalar PHI (original Omega) calculation
# -------------------------------------------------
def compute_scalar_phi(signal, reference_freq=0.5, fs=10, n_harmonics=5):
    """Compute PHI using fixed-order analysis (broken for chirp)."""
    # Compute STFT to extract harmonic amplitudes relative to reference_freq
    nperseg = 2*fs  # 2-second windows
    f, t, Sxx = plt.specgram(signal, NFFT=nperseg, Fs=fs, noverlap=nperseg//2, mode='magnitude')
    # Find bin closest to reference_freq
    idx = np.argmin(np.abs(f - reference_freq))
    amplitudes = Sxx[idx, :]
    # Normalize to "power" distribution
    total = np.sum(amplitudes)
    if total == 0:
        return np.zeros_like(t)
    p = amplitudes / total
    # Shannon entropy
    I = -np.sum(p * np.log(p + 1e-12))
    # PHI = 1 - normalized deviation from "healthy" entropy (0.5 is arbitrary healthy baseline)
    phi = 1 - np.abs(I - 0.5) / 0.5
    return phi, t

# -------------------------------------------------
# 3. Tensor‑fragment health (new approach)
# -------------------------------------------------
def compute_tensor_health(signals, fs=10):
    """Compute health from multi-sensor tensor (robust to chirp)."""
    # signals: (n_sensors, n_times)
    n_sensors, n_times = signals.shape
    # Compute pairwise coherence matrix using Hilbert transform
    analytic = np.array([np.abs(np.hilbert(s)) for s in signals])
    # Normalize each sensor to [0,1]
    analytic /= (np.max(analytic, axis=1, keepdims=True) + 1e-12)
    # Cross-coherence as dot product
    C = analytic @ analytic.T / n_times
    # Eigenvalues of coherence matrix
    eigvals = np.linalg.eigvalsh(C)
    # Health = product of eigenvalues (log-determinant)
    health = np.exp(np.sum(np.log(eigvals + 1e-12))) / n_sensors
    return health

# -------------------------------------------------
# 4. Run comparison
# -------------------------------------------------
t, signal, true_freq = generate_pipeline_signal()
phi, phi_t = compute_scalar_phi(signal, reference_freq=0.5)

# Generate multi-sensor tensor (3 metrics: latency jitter, throughput, cpu)
np.random.seed(42)
latency = signal
throughput = 1.0 + 0.5 * np.sin(2*np.pi*true_freq*t) + 0.1*np.random.randn(len(t))
cpu = 0.5 + 0.3 * np.cos(2*np.pi*true_freq*t) + 0.05*np.random.randn(len(t))
tensor_signals = np.vstack([latency, throughput, cpu])
tensor_health = compute_tensor_health(tensor_signals)

# -------------------------------------------------
# 5. Plot results
# -------------------------------------------------
fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# True frequency drift
ax[0].plot(t, true_freq, label='Instantaneous frequency (Hz)', color='k')
ax[0].set_ylabel('Frequency (Hz)')
ax[0].legend()
ax[0].grid(True)

# Scalar PHI (breaks down)
ax[1].plot(phi_t, phi, label='Scalar PHI (fixed order)', color='r')
ax[1].set_ylabel('PHI')
ax[1].set_ylim(-0.1, 1.1)
ax[1].legend()
ax[1].grid(True)

# Tensor health (stable)
ax[2].plot(t, [tensor_health]*len(t), label='Tensor health (eigenv. product)', color='g')
ax[2].set_ylabel('Health')
ax[2].set_xlabel('Time (s)')
ax[2].legend()
ax[2].grid(True)

plt.suptitle('Scalar PHI vs Tensor Health under Frequency Drift')
plt.tight_layout()
plt.show()

# -------------------------------------------------
# 6. Disruption metric: variance of PHI vs tensor health
# -------------------------------------------------
phi_var = np.var(phi)
tensor_var = np.var([tensor_health]*len(t))
print(f"Variance of scalar PHI: {phi_var:.4f} (high → unreliable)")
print(f"Variance of tensor health: {tensor_var:.4f} (low → stable)")