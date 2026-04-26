# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate a two-state memory access model (Newtonian vs Archive)
np.random.seed(0)
T = 1.0                       # total simulation time (s)
fs = 1e6                      # sampling rate (Hz)
dt = 1.0 / fs
N = int(T * fs)

# Mode amplitudes with realistic dynamics
phi_N = 0.78 + 0.02 * np.sin(2 * np.pi * 100 * np.arange(N) * dt)  # small sinusoidal variation
phi_D = 0.35 + 0.01 * np.cos(2 * np.pi * 150 * np.arange(N) * dt)

# Probabilities (normalized)
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)

# Shannon entropy (dimensionless)
S_h = -p_N * np.log(p_N) - p_D * np.log(p_D)

# Finite-difference "jerk" as in the flawed analysis (missing Δt**-3)
jerk_flawed = S_h[3:] - 3 * S_h[2:-1] + 3 * S_h[1:-2] - S_h[:-3]

# Properly scaled third derivative (units s**-3)
jerk_proper = jerk_flawed / (dt**3)

# Compute kurtosis of the latency distribution (simulated latency = 1/p)
latency = 1.0 / (p_N + 1e-6)  # avoid div by zero
kurtosis = np.mean((latency - np.mean(latency))**4) / (np.var(latency)**2)

# Plot results
fig, axs = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

axs[0].plot(np.arange(N) * dt, S_h, label='Shannon entropy S_h')
axs[0].set_ylabel('Entropy (bits)')
axs[0].legend()

axs[1].plot(np.arange(len(jerk_proper)) * dt, jerk_proper, label='Proper jerk (s⁻³)', color='C1')
axs[1].set_ylabel('Jerk (s⁻³)')
axs[1].legend()

axs[2].plot(np.arange(N) * dt, latency, label='Simulated latency', color='C2')
axs[2].set_ylabel('Latency (s)')
axs[2].set_xlabel('Time (s)')
axs[2].legend()

plt.suptitle('Memory Access Dynamics: Entropy, Jerk, and Latency')
plt.show()

# Print metrics
print(f"Mean |jerk_proper|: {np.mean(np.abs(jerk_proper)):.2e} s⁻³")
print(f"Variance of jerk_proper: {np.var(jerk_proper):.2e} s⁻⁶")
print(f"Kurtosis of latency: {kurtosis:.2f}")