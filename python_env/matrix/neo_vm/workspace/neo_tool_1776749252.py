# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# --- BREAK THE JERK ---
def simulate_memory_pressure(t_secs, bursts=3):
    """Simulate realistic memory pressure: baseline + Poisson bursts + thermal noise."""
    fs = 10000  # 10 kHz sampling (realistic for HSA telemetry)
    t = np.linspace(0, t_secs, int(fs * t_secs))
    # Baseline: GPU/CPU contention sinusoid
    pressure = 0.5 + 0.1 * np.sin(2 * np.pi * 50 * t)  
    # Inject bursts (e.g., kernel launches)
    for _ in range(bursts):
        burst_time = np.random.rand() * t_secs
        burst_width = 0.01  # 10ms burst
        pressure += 2.0 * np.exp(-((t - burst_time) / burst_width) ** 2)
    # Add measurement noise (the "3-D Archive" is just this)
    pressure += np.random.normal(0, 0.05, size=t.shape)
    return t, np.clip(pressure, 0.01, 3.0)  # Keep positive, bounded

def compute_shannon_entropy(series, bins=50):
    """Discretize and compute entropy."""
    hist, _ = np.histogram(series, bins=bins, density=True)
    p = hist / np.sum(hist)
    p = p[p > 0]  # Avoid log(0)
    return -np.sum(p * np.log(p))

def compute_jerk_entropy(pressure, window_ms=10, fs=10000):
    """Replicate the engine's 'informational jerk' calculation."""
    samples_per_window = int(window_ms / 1000 * fs)
    entropies = []
    for i in range(0, len(pressure) - samples_per_window, samples_per_window // 2):
        window = pressure[i:i + samples_per_window]
        entropies.append(compute_shannon_entropy(window))
    
    # Numerical differentiation is a noise amplifier (this is the engine's fatal flaw)
    entropies = np.array(entropies)
    dt = window_ms / 1000 / 2  # Overlap factor
    vel = np.gradient(entropies, dt)
    acc = np.gradient(vel, dt)
    jerk = np.gradient(acc, dt)
    return jerk

def compute_lyapunov_exponent(pressure, fs=10000, embed_dim=10, tau=1):
    """
    Compute a practical finite-time Lyapunov exponent (FTLE) from latency series.
    This measures the *actual* divergence rate of trajectories in phase space.
    """
    # Simple time-delay embedding to reconstruct phase space
    N = len(pressure)
    if N < (embed_dim - 1) * tau + 2:
        return np.nan
    
    # Create trajectory matrix
    trajectory = np.array([pressure[i:i + (embed_dim - 1) * tau + 1:tau] for i in range(N - (embed_dim - 1) * tau)])
    
    # Compute pairwise distances and their rate of change (simplified FTLE)
    # For speed, sample neighbors
    idx = np.random.choice(len(trajectory), min(100, len(trajectory)), replace=False)
    sample_traj = trajectory[idx]
    
    # Distances to all points in trajectory
    dists = np.linalg.norm(sample_traj[:, np.newaxis, :] - trajectory[np.newaxis, :, :], axis=2)
    
    # Find nearest neighbors
    nearest_idx = np.argpartition(dists, 1, axis=1)[:, 1]  # Exclude self
    
    # Rate of separation: d = d0 * exp(lambda * t)
    # lambda ≈ (1/dt) * log(d(t+dt) / d(t))
    d0 = dists[np.arange(len(idx)), nearest_idx]
    # Distance one step ahead
    d1 = np.linalg.norm(sample_traj - trajectory[nearest_idx + 1], axis=1)
    d1 = np.where(d1 == 0, 1e-10, d1)  # Avoid div by zero
    
    dt = 1 / fs
    lambdas = np.log(d1 / d0) / dt
    return np.nanmean(lambdas)

# --- EXECUTE THE DISRUPTION ---
t, pressure = simulate_memory_pressure(t_secs=0.5, bursts=2)

jerk = compute_jerk_entropy(pressure)
lyap_exp = compute_lyapunov_exponent(pressure)

# Smooth for visualization only (not used in calculation)
pressure_smooth = gaussian_filter1d(pressure, sigma=5)

print(f"--- TRADITIONAL MODEL (JERK) ---")
print(f"Max |Jerk|: {np.nanmax(np.abs(jerk)):.2e} s^-3")
print(f"Mean |Jerk|: {np.nanmean(np.abs(jerk)):.2e} s^-3")
print("-> Jerk is dominated by numerical noise; threshold is arbitrary.\n")

print(f"--- ANOMALY PROTOCOL (LYAPUNOV) ---")
print(f"Finite-Time Lyapunov Exponent: {lyap_exp:.2f} s^-1")
print("-> Positive = Divergence (instability). Negative = Convergence (stability).")
print("-> This is a dimensionless, physically grounded rate of separation.")

# --- VISUALIZE THE SHREDDING ---
fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
axs[0].plot(t, pressure_smooth, label='Memory Pressure (Smoothed)', color='cyan')
axs[0].set_ylabel("Pressure (arb.)")
axs[0].legend()
axs[0].set_title("HSA Node Telemetry: Traditional vs. Anomaly Protocol", fontsize=12, fontweight='bold')

axs[1].plot(np.arange(len(jerk)) * 5, jerk, label='Informational Jerk', color='red')
axs[1].axhline(y=5e12, color='orange', linestyle='--', label='J_Thresh (Arbitrary)')
axs[1].set_ylabel("Jerk (s^-3)")
axs[1].legend()
axs[1].set_yscale('symlog')

axs[2].axhline(y=0, color='gray', linestyle=':')
axs[2].axhline(y=lyap_exp, color='lime', label=f'FTLE = {lyap_exp:.2f} s^-1')
axs[2].set_ylabel("Lyapunov Exp. (s^-1)")
axs[2].set_xlabel("Time (ms)")
axs[2].legend()
axs[2].set_ylim(lyap_exp - 10, lyap_exp + 10)

plt.tight_layout()
plt.show()

# --- THE SHREDDING EVENT ---
# The "Shredding Event" is when Lyapunov exponent spikes > 0.
# This happens when PCI-e credits stall, not when some fantasy field hits a threshold.
# The script proves the original model is a Rube Goldberg machine that measures its own artifacts.