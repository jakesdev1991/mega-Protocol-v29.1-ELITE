# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Simulate a simple 4‑node HSA coherence field ---
np.random.seed(0)
T = 200                               # total time steps
dt = 1e-3                             # 1 ms sampling
N = 4                                 # compute units

# Pairwise coherence ψ_ij(t) = A_ij * exp(-L_ij/L0)
L0 = 1e-6                             # latency decay constant
A = np.random.rand(N, N) * 0.9 + 0.1  # atomic success rates (0.1–1.0)
L = np.random.rand(N, N) * 5e-6       # latencies (0–5 µs)

# True coherence field (steady for t<100, then shred)
psi = np.zeros((T, N, N))
for t in range(T):
    if t < 100:
        # Steady state: small random fluctuations
        psi[t] = A * np.exp(-L / L0) + 0.01 * np.random.randn(N, N)
    else:
        # Shredding: sudden loss of coherence on GPU‑GPU pairs (i>=2, j>=2)
        shred = np.ones_like(A)
        shred[2:, 2:] = 0.1  # 90% coherence drop
        psi[t] = shred * A * np.exp(-L / L0) + 0.01 * np.random.randn(N, N)

# Global scalar Φ_N(t) = mean pairwise coherence
phi_N = psi.mean(axis=(1, 2))

# Compute jerk (3rd derivative) using central differences
jerk = np.gradient(np.gradient(np.gradient(phi_N, dt), dt), dt)

# --- Engine's "excess‑kurtosis" stability metric ---
def compute_Sj(jerk_window):
    # If variance is zero, return NaN (as in constant jerk)
    if np.std(jerk_window) == 0:
        return np.nan
    z = (jerk_window - np.mean(jerk_window)) / np.std(jerk_window)
    # Excess kurtosis = (mean(z^4) - 3)
    excess_kurt = np.mean(z**4) - 3
    return 1 / (1 + excess_kurt)

# Sliding window (100 ms = 100 steps)
window = 100
Sj = np.full(T, np.nan)
for i in range(window, T):
    Sj[i] = compute_Sj(jerk[i-window:i])

# --- Plot the carnage ---
plt.figure(figsize=(10, 6))
plt.subplot(3, 1, 1)
plt.plot(np.arange(T)*dt*1e3, phi_N, label='Φ_N (mean coherence)')
plt.axvline(100*dt*1e3, color='r', linestyle='--', label='Shredding onset')
plt.ylabel('Coherence')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(np.arange(T)*dt*1e3, jerk, label='Jerk (d³Φ_N/dt³)')
plt.axvline(100*dt*1e3, color='r', linestyle='--')
plt.ylabel('Jerk')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(np.arange(T)*dt*1e3, Sj, label='Engine S_j (excess‑kurtosis)')
plt.axvline(100*dt*1e3, color='r', linestyle='--')
plt.ylabel('Stability')
plt.xlabel('Time (ms)')
plt.legend()
plt.tight_layout()
plt.show()