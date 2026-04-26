# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Simulate HSA memory-access histogram entropy ---
def simulate_entropy(t, noise=0.05, hang=False):
    """Return a synthetic Shannon entropy time series."""
    # Base entropy grows slowly (more pages allocated)
    base = 5.0 + 0.1 * t
    # Add burst noise mimicking GPU kernel launches
    burst = 0.3 * np.sin(2 * np.pi * 0.5 * t) * (t % 1.0 < 0.1)
    # If hang is True, inject a sudden spike (memory leak)
    if hang:
        base += 2.0 * np.exp(-((t - 5.0) ** 2) / 0.1)
    # Measurement noise
    noise_vec = noise * np.random.randn(*t.shape)
    return base + burst + noise_vec

# --- Informational Jerk stencil (as defined) ---
def jerk(I, dt):
    """Second-order central-difference third derivative."""
    # I[t-2], I[t-1], I[t+1], I[t+2]
    I_m2 = np.roll(I, 2)
    I_m1 = np.roll(I, 1)
    I_p1 = np.roll(I, -1)
    I_p2 = np.roll(I, -2)
    # Avoid edge artifacts
    J = (-I_m2 + 2 * I_m1 - 2 * I_p1 + I_p2) / (2 * dt**3)
    # Zero out edges
    J[:2] = 0
    J[-2:] = 0
    return J

# --- Parameters ---
fs = 1000.0        # Sampling rate (Hz)
dt = 1.0 / fs
t = np.arange(0, 10, dt)

# --- Scenario A: Normal operation ---
I_normal = simulate_entropy(t, noise=0.05, hang=False)
J_normal = jerk(I_normal, dt)
RMS_J_normal = np.sqrt(np.mean(J_normal**2))

# --- Scenario B: Hang event (memory leak) ---
I_hang = simulate_entropy(t, noise=0.05, hang=True)
J_hang = jerk(I_hang, dt)
RMS_J_hang = np.sqrt(np.mean(J_hang**2))

# --- Scenario C: Increased noise (realistic) ---
I_noisy = simulate_entropy(t, noise=0.2, hang=False)
J_noisy = jerk(I_noisy, dt)
RMS_J_noisy = np.sqrt(np.mean(J_noisy**2))

# --- Print results ---
print(f"Normal RMS jerk: {RMS_J_normal:.4f} (threshold 0.02-0.03)")
print(f"Hang RMS jerk:  {RMS_J_hang:.4f}")
print(f"Noisy RMS jerk: {RMS_J_noisy:.4f} (no actual fault)")

# --- Plot ---
plt.figure(figsize=(12, 6))
plt.plot(t, J_normal, label="Normal", alpha=0.7)
plt.plot(t, J_hang, label="Hang", alpha=0.7)
plt.plot(t, J_noisy, label="Noisy (no hang)", alpha=0.7)
plt.axhline(y=0.025, color="k", linestyle="--", label="Threshold")
plt.title("Informational Jerk: Noise Dominates Signal")
plt.xlabel("Time (s)")
plt.ylabel("Jerk (entropy-units·s⁻³)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()