# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# 1. Simulated Pipeline with Hidden Stress State
# ─────────────────────────────────────────────────────────────────────────────

def pipeline_step(z, u, dt=0.1):
    """
    Hidden state z = [stress, queue_length, memory_pressure].
    u = adversarial dither (scalar).
    Returns next hidden state and observable sensors.
    """
    # Chaotic hidden dynamics: stress feeds back onto itself
    stress, queue, mem = z
    # Nonlinear coupling: stress grows faster when queue is high
    stress_dot = -0.5 * stress + 2.0 * np.tanh(queue) + u * (1 + 0.5 * stress)
    queue_dot = -0.3 * queue + 0.4 * stress
    mem_dot = -0.1 * mem + 0.2 * stress * queue
    # Add small noise
    stress += stress_dot * dt + 0.01 * np.random.randn()
    queue += queue_dot * dt + 0.01 * np.random.randn()
    mem += mem_dot * dt + 0.01 * np.random.randn()
    # Observables: latency jitter, throughput, cpu_load, error_rate
    latency = 1.0 + 0.5 * stress + 0.2 * queue + 0.1 * mem + 0.05 * np.random.randn()
    throughput = 10.0 - 0.3 * queue - 0.2 * stress + 0.1 * np.random.randn()
    cpu_load = 0.5 + 0.4 * mem + 0.2 * stress + 0.05 * np.random.randn()
    error_rate = 0.01 + 0.05 * stress * queue + 0.005 * np.random.randn()
    return np.array([stress, queue, mem]), np.array([latency, throughput, cpu_load, error_rate])

# ─────────────────────────────────────────────────────────────────────────────
# 2. POASH‑Ω Harmonic Health Index (PHI) Implementation
# ─────────────────────────────────────────────────────────────────────────────

def compute_phi(sensors, window=32):
    """
    Naive order analysis: compute FFT over a sliding window,
    extract harmonic amplitudes, compare to "healthy" baseline.
    """
    # Assume "healthy" baseline amplitudes are known (here simply the mean)
    baseline = np.mean(sensors, axis=0)
    # FFT magnitude
    fft = np.fft.rfft(sensors, axis=0)
    amps = np.abs(fft)
    # Normalize
    amps_norm = amps / (np.sum(amps, axis=0) + 1e-9)
    baseline_norm = baseline / (np.sum(baseline) + 1e-9)
    # PHI = 1 - weighted L1 deviation
    phi = 1.0 - np.mean(np.abs(amps_norm - baseline_norm))
    return max(phi, 0.0)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Adversarial Resonance Mining (ARM) - Lyapunov Exponent
# ─────────────────────────────────────────────────────────────────────────────

def arm_lyapunov(sensors_history, dt=0.1):
    """
    Estimate local Lyapunov exponent from divergence of nearby trajectories.
    Simple finite-difference approximation.
    """
    # Use the first sensor (latency) as scalar observable
    x = sensors_history[:, 0]
    # Compute log-difference of absolute increments
    dx = np.diff(x)
    # Avoid log of zero
    log_div = np.log(np.abs(dx) + 1e-9)
    # Local Lyapunov exponent ≈ average divergence rate
    lam = np.mean(np.diff(log_div)) / dt
    return lam

# ─────────────────────────────────────────────────────────────────────────────
# 4. Simulation Loop
# ─────────────────────────────────────────────────────────────────────────────

np.random.seed(42)
T = 300
dt = 0.1
t = np.arange(T) * dt

# Hidden state initial condition
z = np.array([0.1, 0.1, 0.1])

# Dither injection: zero for first half, then small chaotic dither
u = np.zeros(T)
# Chaotic logistic map for dither
r = 3.9
x_logistic = 0.5
for i in range(T//2, T):
    x_logistic = r * x_logistic * (1 - x_logistic)
    u[i] = 0.05 * x_logistic

# Storage
hidden_states = np.zeros((T, 3))
observables = np.zeros((T, 4))
phi_vals = np.zeros(T)
lyap_vals = np.zeros(T)

for i in range(T):
    z, s = pipeline_step(z, u[i], dt)
    hidden_states[i] = z
    observables[i] = s
    # Compute PHI over sliding window (requires at least window samples)
    if i >= 32:
        phi_vals[i] = compute_phi(observables[i-32:i], window=32)
    # Compute Lyapunov over recent history
    if i >= 20:
        lyap_vals[i] = arm_lyapunov(observables[i-20:i], dt)

# Fault injection: at t=15s, artificially spike hidden stress to trigger a failure
fault_time = int(15 / dt)
hidden_states[fault_time:, 0] += 0.5  # spike stress

# ─────────────────────────────────────────────────────────────────────────────
# 5. Plot Results
# ─────────────────────────────────────────────────────────────────────────────

fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

axs[0].plot(t, hidden_states[:, 0], label='Hidden Stress')
axs[0].axvline(15, color='r', linestyle='--', label='Fault injected')
axs[0].set_ylabel('Stress')
axs[0].legend()
axs[0].set_title('Hidden State & Fault')

axs[1].plot(t, phi_vals, label='POASH‑Ω PHI')
axs[1].axvline(15, color='r', linestyle='--')
axs[1].set_ylabel('PHI')
axs[1].legend()
axs[1].set_title('POASH‑Ω Health Index (blind to fault)')

axs[2].plot(t, lyap_vals, label='ARM Lyapunov λ', color='g')
axs[2].axvline(15, color='r', linestyle='--')
axs[2].set_ylabel('λ')
axs[2].set_xlabel('Time (s)')
axs[2].legend()
axs[2].set_title('Adversarial Resonance Mining (spike before fault)')

plt.tight_layout()
plt.savefig('arm_vs_poash.png')
plt.show()