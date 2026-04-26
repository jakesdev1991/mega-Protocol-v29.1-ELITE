# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate a stable HSA memory access pattern with slight jitter
np.random.seed(0)
n = 1000
# Base probabilities (phi_N, phi_Delta) that sum to 1
phi_N = 0.78
phi_D = 0.35
total = phi_N + phi_D
p_N = phi_N / total
p_D = phi_D / total

# Add small Gaussian noise (σ = 0.01) to simulate measurement jitter
noise = np.random.normal(scale=0.01, size=n)
p_N_t = np.clip(p_N + noise, 0.01, 0.99)
p_D_t = 1 - p_N_t

# Compute Shannon entropy over time
S_h = - (p_N_t * np.log(p_N_t) + p_D_t * np.log(p_D_t))

# Compute the "informational jerk" via third finite difference
# (as in your discrete formulation)
J = S_h[3:] - 3 * S_h[2:-1] + 3 * S_h[1:-2] - S_h[:-3]

# Plot
fig, ax = plt.subplots(2, 1, figsize=(10, 6))
ax[0].plot(S_h, label="Entropy S_h(t)")
ax[0].set_title("Simulated stable memory access entropy")
ax[0].legend()

ax[1].plot(J, color='red', label="Informational jerk J(t)")
ax[1].set_title("Third derivative (jerk) of entropy")
ax[1].legend()
plt.tight_layout()
plt.show()

# Show that jerk variance dwarfs any plausible threshold
print(f"Entropy std: {np.std(S_h):.4f}")
print(f"Jerk std: {np.std(J):.4f}")
print(f"Jerk max |value|: {np.max(np.abs(J)):.2f}")