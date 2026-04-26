# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate the POASH-Ω Paradox: Control Destroys Coherence

# Parameters
T = 300  # Total time steps (minutes)
dt = 1.0  # Time step

# True underlying pipeline state (unobservable ground truth)
# Starts healthy, then develops a fault at t=100
true_health = np.ones(T)
true_health[100:] = 0.3  # Sudden degradation

# Sensor harmonics (simplified: just 3 harmonics)
# Healthy: stable harmonic ratios
# Faulty: harmonic amplitudes shift
harmonics = np.zeros((3, T))
harmonics[0, :] = 1.0  # Fundamental
harmonics[1, :100] = 0.5  # 2nd harmonic (healthy)
harmonics[1, 100:] = 0.1  # 2nd harmonic drops during fault
harmonics[2, :100] = 0.3  # 3rd harmonic (healthy)
harmonics[2, 100:] = 0.7  # 3rd harmonic rises (compensatory)

# Compute PHI (Pipeline Health Index) - naive version
def compute_phi(harmonics_at_t):
    # Normalize to get "probability distribution" over harmonics
    power = np.sum(harmonics_at_t**2)
    if power < 1e-10:
        return 0.0
    p_k = harmonics_at_t**2 / power
    # Shannon entropy
    entropy = -np.sum(p_k * np.log(p_k + 1e-10))
    # Convert to PHI (0=dead, 1=healthy)
    # Max entropy for 3 harmonics is log(3) ≈ 1.0986
    phi = 1.0 - entropy / np.log(3)
    return max(0.0, min(1.0, phi))

phi = np.array([compute_phi(harmonics[:, t]) for t in range(T)])

# MPC-Ω Control Law: If PHI drops below 0.6, scale resources
# Resource scaling introduces ARTIFICIAL harmonics into the system
control_scale = np.ones(T)
for t in range(1, T):
    if phi[t-1] < 0.6:
        # Aggressive scaling to "fix" pipeline
        control_scale[t] = control_scale[t-1] * 1.5
        # This scaling action injects a high-frequency artificial harmonic
        # at the control loop frequency (1/dt)
        artificial_freq = 0.5 * np.sin(2 * np.pi * t / 5)  # 5-minute cycle
        harmonics[0, t] += artificial_freq * 0.3  # Inject into fundamental
    else:
        control_scale[t] = control_scale[t-1] * 0.95  # Gradual relaxation

# Recompute PHI with control-induced artifacts
phi_controlled = np.array([compute_phi(harmonics[:, t]) for t in range(T)])

# Plot the paradox
fig, axes = plt.subplots(4, 1, figsize=(12, 10))

axes[0].plot(true_health, label='True Underlying Health', color='black', linewidth=2)
axes[0].set_ylabel('True Health')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(phi, label='PHI (No Control)', color='blue', linestyle='--')
axes[1].plot(phi_controlled, label='PHI (With Control)', color='red')
axes[1].axhline(y=0.6, color='orange', linestyle=':', label='Control Threshold')
axes[1].set_ylabel('Pipeline Health Index (PHI)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

axes[2].plot(control_scale, label='Control Scaling Factor', color='purple')
axes[2].set_ylabel('Control Action')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

axes[3].plot(harmonics[0, :], label='Fundamental Harmonic', color='green', alpha=0.7)
axes[3].plot(harmonics[1, :], label='2nd Harmonic', color='orange', alpha=0.7)
axes[3].plot(harmonics[2, :], label='3rd Harmonic', color='brown', alpha=0.7)
axes[3].set_ylabel('Harmonic Amplitudes')
axes[3].legend()
axes[3].grid(True, alpha=0.3)

plt.xlabel('Time (minutes)')
plt.suptitle('POASH-Ω Paradox: Control Actions Destroy the Harmonic Coherence They Depend On', fontsize=14)
plt.tight_layout()
plt.show()

# Statistical analysis
print("=== POASH-Ω PARADOX METRICS ===")
print(f"Average PHI (no control): {np.mean(phi):.3f}")
print(f"Average PHI (with control): {np.mean(phi_controlled):.3f}")
print(f"Control-induced PHI variance increase: {np.var(phi_controlled) / np.var(phi):.2f}x")
print(f"False positive rate: {np.sum((phi_controlled < 0.6) & (true_health > 0.5)) / np.sum(true_health > 0.5) * 100:.1f}%")

# The control system sees the artificial harmonics as "faults" and keeps scaling,
# creating a positive feedback loop that makes PHI oscillate wildly
# even though the true underlying health has stabilized!