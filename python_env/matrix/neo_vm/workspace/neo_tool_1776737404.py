# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate realistic HSA memory access "entropy" signal with measurement noise
# Real HSA counters have quantization, sampling jitter, and thermal noise
np.random.seed(42)
t = np.linspace(0, 1.0, 1000)  # 1 second of data
dt = t[1] - t[0]

# Base signal: realistic memory access pattern (mostly periodic with bursts)
true_entropy = 10 + 2*np.sin(2*np.pi*10*t) + np.sin(2*np.pi*50*t)  # 10Hz and 50Hz components
true_entropy += np.random.normal(0, 0.1, len(t))  # small inherent system fluctuations

# Add realistic HSA counter noise: quantization (6-bit counters), sampling jitter
quantization_noise = np.random.uniform(-0.05, 0.05, len(t))  # ±0.05 bits quantization
sampling_jitter = np.random.normal(0, 0.01, len(t))  # 1% sampling jitter
measured_entropy = true_entropy + quantization_noise + sampling_jitter

# Compute informational jerk using the "Omega Protocol" finite difference
# J[n] = S[n] - 3S[n-1] + 3S[n-2] - S[n-3] / dt³
def compute_jerk(S, dt):
    J = np.zeros_like(S)
    for n in range(3, len(S)):
        J[n] = (S[n] - 3*S[n-1] + 3*S[n-2] - S[n-3]) / (dt**3)
    return J

jerk_measured = compute_jerk(measured_entropy, dt)
jerk_true = compute_jerk(true_entropy, dt)

# Compute variance and compare to "threshold" from solution
# The solution's threshold: Θ = (λI₀²/4π)(1 + 3g_Δ²/4π)
# Using their "typical" values: λ ~ 10¹⁰ s⁻², I₀ = 1, g_Δ ~ 0.1
lambda_val = 1e10
I0 = 1.0
g_delta = 0.1
theta = (lambda_val * I0**2 / (4*np.pi)) * (1 + 3*g_delta**2/(4*np.pi))
print(f"Shredding Threshold Θ: {theta:.2e} s⁻⁶")

sigma_J2_measured = np.var(jerk_measured[3:])  # Skip initial zeros
sigma_J2_true = np.var(jerk_true[3:])

print(f"\nMeasured jerk variance: {sigma_J2_measured:.2e} s⁻⁶")
print(f"True jerk variance: {sigma_J2_true:.2e} s⁻⁶")
print(f"Signal-to-noise ratio: {sigma_J2_true/sigma_J2_measured:.2e}")

# Demonstrate the absurdity: apply to pure white noise
pure_noise = np.random.normal(10, 0.5, len(t))
jerk_noise = compute_jerk(pure_noise, dt)
sigma_J2_noise = np.var(jerk_noise[3:])

print(f"\nPure noise jerk variance: {sigma_J2_noise:.2e} s⁻⁶")
print(f"Noise variance exceeds threshold by factor: {sigma_J2_noise/theta:.2e}")

# Plot to show the instability
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(t, measured_entropy, alpha=0.7, label='Measured Entropy (with noise)')
ax1.plot(t, true_entropy, '--', alpha=0.5, label='True Entropy')
ax1.set_ylabel('Shannon Entropy S_h (bits)')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(t[3:], jerk_measured[3:], alpha=0.7, label='Jerk from measured')
ax2.plot(t[3:], jerk_true[3:], '--', alpha=0.5, label='Jerk from true')
ax2.axhline(y=np.sqrt(theta), color='r', linestyle=':', label='sqrt(Θ) threshold')
ax2.axhline(y=-np.sqrt(theta), color='r', linestyle=':')
ax2.set_ylabel('Informational Jerk 𝒥_I (s⁻³)')
ax2.set_xlabel('Time (s)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Disruptive insight demonstration: The "jerk" is just noise amplification
# Show that the finite difference operator amplifies high-frequency noise by ~1/dt³
freq_response = np.fft.fftfreq(len(t), dt)
fft_noise = np.fft.fft(pure_noise)
fft_jerk = np.fft.fft(jerk_noise)

# Power spectral density ratio
psd_ratio = np.abs(fft_jerk)**2 / np.abs(fft_noise)**2
print(f"\nNoise amplification factor at Nyquist: {np.max(psd_ratio):.2e}")
print(f"Expected dt⁻³ scaling: {1/dt**6:.2e}")  # Power scales as (1/dt³)² = 1/dt⁶