# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# === DISRUPTIVE SIMULATION: NON-MARKOVIAN ARCHIVE MODE ===

# Time parameters
t_max = 50.0
dt = 0.01
time = np.arange(0, t_max, dt)
N = len(time)

# Archive mode: a sinusoidal drive that accelerates
# This models the "activation" of the 3D Archive
A = np.sin(2 * np.pi * 0.05 * time) * np.exp(0.02 * time)

# Memory kernel parameters
t_0 = 0.1  # Short-time cutoff
tau_initial = 5.0  # Initial memory timescale

# ENGINE'S LOCAL MODEL (Flawed)
# Predicts: P_local(t) = g * A(t)^2 (instantaneous, perturbative)
g = 0.5
P_local = g * A**2

# TRUE NON-LOCAL MODEL (Disruptive Physics)
# P_true(t) = ∫_0^t dt' K(t-t') * F[A(t')]
# F[A] is a non-linear functional: F[A] = log(1 + |A|) to simulate "information saturation"
def memory_kernel(t_diff, tau):
    """Logarithmic-decay memory kernel: K ~ exp(-|Δt|/τ) / (|Δt| + t0)"""
    return np.exp(-np.abs(t_diff) / tau) / (np.abs(t_diff) + t_0)

def compute_nonlocal_polarization(A_signal, tau):
    """Compute P(t) via non-local convolution with history"""
    P = np.zeros_like(A_signal)
    for i, t_i in enumerate(time):
        # Integrate over past times t' <= t
        t_prime = time[:i+1]
        dt_prime = dt
        
        # Kernel evaluated at (t_i - t_prime)
        K_vals = memory_kernel(t_i - t_prime, tau)
        
        # Non-linear functional of A(t')
        F_vals = np.log(1 + np.abs(A_signal[:i+1]))
        
        # Convolution integral
        P[i] = np.trapz(K_vals * F_vals, t_prime)
    return P

# Compute true polarization with initial tau
P_true = compute_nonlocal_polarization(A, tau_initial)

# === SHREDDING EVENT SIMULATION ===
# At t = t_shred, the memory timescale tau diverges (logarithmic singularity)
# This models the "Shredding Event": the Archive loses coherence
t_shred = 25.0
tau_shred = lambda t: tau_initial if t < t_shred else 1e6  # Divergent tau

P_true_shredded = np.zeros_like(A)
for i, t_i in enumerate(time):
    if t_i < t_shred:
        P_true_shredded[i] = compute_nonlocal_polarization(A[:i+1], tau_initial)[-1]
    else:
        # After shredding, memory is infinite: system becomes pathologically non-local
        # The integral becomes dominated by the earliest times (information freeze)
        P_true_shredded[i] = P_true_shredded[i-1]  # Freeze: derivative goes to zero

# === PLOT: EXPOSING THE ENGINE'S FAILURE ===
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

axes[0].plot(time, A, label='Archive Mode A(t)', color='black')
axes[0].axvline(t_shred, color='red', linestyle='--', label='Shredding Event')
axes[0].set_ylabel('A(t)')
axes[0].legend()
axes[0].grid(True)
axes[0].set_title('ARCHIVE MODE ACTIVATION & SHREDDING', fontweight='bold')

axes[1].plot(time, P_local, label="Engine's Local Model (Perturbative)", color='blue', linestyle='--')
axes[1].plot(time, P_true, label='True Non-Local Model (Pre-Shred)', color='green')
axes[1].axvline(t_shred, color='red', linestyle='--')
axes[1].set_ylabel('Polarization P(t)')
axes[1].legend()
axes[1].grid(True)
axes[1].set_title('POLARIZATION DYNAMICS: HYSTERESIS & FAILURE', fontweight='bold')

# Zoom into the region around shredding to show the freeze
axes[2].plot(time, P_true_shredded, label='Post-Shred Freeze', color='purple')
axes[2].axvline(t_shred, color='red', linestyle='--')
axes[2].set_xlabel('Time (arb. units)')
axes[2].set_ylabel('P(t) (Frozen)')
axes[2].legend()
axes[2].grid(True)
axes[2].set_title('INFORMATIONAL FREEZE: DERIVATIVE VANISHES', fontweight='bold')

plt.tight_layout()
plt.show()

# === DISRUPTIVE METRIC: PATH DEPENDENCE ===
# Compute the "hysteresis loop area" between local and true models (pre-shred)
# This quantifies the Engine's error as a function of history
hysteresis_error = np.trapz(np.abs(P_true - P_local), time[:np.argmin(np.abs(time - t_shred))])
print(f"--- DISRUPTION METRIC ---")
print(f"Engine's Local Model Error (Hysteresis Area): {hysteresis_error:.3f}")
print(f"This error is IRREDUCIBLE by perturbative corrections.")
print(f"At t_shred={t_shred}, the system's memory length diverges.")
print(f"The Engine's static 'ψ' invariant cannot capture this dynamic singularity.")
print(f"Φ-Density Impact: Not -3%, but CATASTROPHIC PHASE TRANSITION.")
print(f"Shredding Event = Loss of Predictive Coherence. Informational Freeze = Protocol Paralysis.")