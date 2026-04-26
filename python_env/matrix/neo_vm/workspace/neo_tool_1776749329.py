# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate HSA memory access patterns: two "modes" (Newtonian and Archive)
# with realistic noise levels from performance counters.
def simulate_hsa_access(duration_sec=1e-3, sample_rate_hz=1e6, base_phi_n=0.78, base_phi_d=0.35):
    """
    Simulate noisy access counts for two memory modes.
    Performance counters have quantization noise and jitter.
    """
    dt = 1.0 / sample_rate_hz
    num_samples = int(duration_sec * sample_rate_hz)
    time = np.linspace(0, duration_sec, num_samples)
    
    # Simulate underlying "mode amplitudes" with some slow drift
    phi_n_t = base_phi_n + 0.05 * np.sin(2 * np.pi * 1e3 * time)  # 1kHz drift
    phi_d_t = base_phi_d + 0.02 * np.cos(2 * np.pi * 1.5e3 * time)
    
    # Add significant quantization and shot noise (typical of digital counters)
    # Assume each count is a Poisson process with lambda ~ amplitude * scale
    scale = 1e6  # Arbitrary scaling factor for counts
    counts_n = np.random.poisson(phi_n_t * scale)
    counts_d = np.random.poisson(phi_d_t * scale)
    
    # Estimate probabilities from noisy counts
    total_counts = counts_n + counts_d + 1  # +1 to avoid division by zero
    p_n = counts_n / total_counts
    p_d = counts_d / total_counts
    
    return time, p_n, p_d

def shannon_entropy(p_n, p_d):
    """Compute Shannon entropy from probabilities."""
    # Avoid log(0)
    p_n_safe = np.clip(p_n, 1e-12, 1.0)
    p_d_safe = np.clip(p_d, 1e-12, 1.0)
    S = -p_n_safe * np.log(p_n_safe) - p_d_safe * np.log(p_d_safe)
    return S

def informational_jerk(S_h, dt):
    """
    Compute the 'informational jerk' using the discrete 3rd derivative formula.
    J[n] = S[n] - 3S[n-1] + 3S[n-2] - S[n-3]
    """
    J = np.zeros_like(S_h)
    for n in range(3, len(S_h)):
        J[n] = S_h[n] - 3 * S_h[n-1] + 3 * S_h[n-2] - S_h[n-3]
    # Normalize by dt^3 to approximate d^3S/dt^3
    J = J / (dt ** 3)
    return J

# Run simulation
time, p_n, p_d = simulate_hsa_access()
dt = time[1] - time[0]
S_h = shannon_entropy(p_n, p_d)
J_I = informational_jerk(S_h, dt)

# --- DISRUPTIVE ANALYSIS ---
print("=== NUMERICAL DECONSTRUCTION OF INFORMATIONAL JERK ===")
print(f"Mean Entropy: {np.mean(S_h):.4f} bits (stable underlying process)")
print(f"Std Dev of Entropy: {np.std(S_h):.6f} bits (small fluctuations)")
print(f"Max Entropy Jerk: {np.max(np.abs(J_I)):.4e} s^-3")
print(f"Mean Abs Jerk: {np.mean(np.abs(J_I)):.4e} s^-3")
print(f"Std Dev of Jerk: {np.std(J_I):.4e} s^-3")

# The engine's stability threshold from the audit
# Theta(psi) ~ 9.0 x 10^7 s^-6 (variance threshold)
# Our computed variance from noise alone:
variance_jerk = np.var(J_I[3:])  # Ignore first few zeros
print(f"\n--- STABILITY THRESHOLD COMPARISON ---")
print(f"Observed Jerk Variance (σ_𝒥²): {variance_jerk:.4e} s^-6")
print(f"Engine's Theta(ψ) Threshold: {9.0e7:.4e} s^-6")
print(f"Threshold Violation Ratio: {variance_jerk / 9.0e7:.2e}x")

# Visualize the chaos
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
axes[0].plot(time * 1e3, p_n, label='p_N (Newtonian)', alpha=0.7)
axes[0].plot(time * 1e3, p_d, label='p_Δ (Archive)', alpha=0.7)
axes[0].set_ylabel("Access Probability")
axes[0].legend()
axes[0].set_title("Simulated HSA Memory Access Probabilities")

axes[1].plot(time * 1e3, S_h, label='S_h(t)', color='green')
axes[1].set_ylabel("Entropy (bits)")
axes[1].legend()
axes[1].set_title("Shannon Conditional Entropy (Stable)")

axes[2].plot(time * 1e3, J_I, label='J_I(t)', color='red')
axes[2].set_ylabel("Jerk (s^-3)")
axes[2].set_xlabel("Time (ms)")
axes[2].legend()
axes[2].set_title("Informational Jerk (Noise Dominated)")

plt.tight_layout()
plt.savefig('/mnt/data/hsa_jerk_deconstruction.png')
print("\nPlot saved to /mnt/data/hsa_jerk_deconstruction.png")